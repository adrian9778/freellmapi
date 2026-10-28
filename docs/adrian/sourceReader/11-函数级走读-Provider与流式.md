# 11 · 函数级走读：Provider 与流式

> 本篇逐函数拆解 provider 抽象层：`BaseProvider`（base.ts:229）的四个共享机制函数（超时、stall、SSE 读、验证诊断）与 `OpenAICompatProvider`（openai-compat.ts:102）的五个业务函数（chat/stream/validate/quota/normalize）。`BaseProvider` 的抽象契约只有五个成员——`platform`（+1）、`name`（+2）、`chatCompletion`（+9）、`streamChatCompletion`（+17）、`validateKey`（+25），其余是带默认实现的可选项：`fetchQuota`（+37，默认不联网、直接返回 false）、`hasQuotaProbe`（+45）、`supportsKeyValidation`（+56）。请求/响应形状不在这一层定义：`TokenUsage`、`ChatCompletionResponse`、`ChatCompletionChunk` 三个类型都出自 `shared/types.ts`。这一层的注释几乎每一条都对应一个线上事故编号，走读时把「函数行为」和「它防的事故」一起记。

调用位置回顾（03 篇）：`runFallbackLoop` 的 `hooks.dispatch` 内部调 `provider.chatCompletion / streamChatCompletion`（`routes/proxy.ts:2453`/`2835`、`routes/anthropic.ts:933`/`715`、`routes/responses.ts:1281`/`1519`），健康检查调 `validateKey`、quota 探测调 `fetchQuota`（`services/health.ts:270`/`387` 与 `health.ts:209`）。实例来自 `resolveProvider`（providers/index.ts:636）：内置平台取注册单例，`custom` 平台按 api_keys 行的 base URL 现造一个 `OpenAICompatProvider`（+4），`timeoutMs: CUSTOM_PROVIDER_TIMEOUT_MS` 在 +8。

---

## 1. `BaseProvider.fetchWithTimeout`（base.ts:326）

```ts
protected async fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs = providerTimeoutMs(this.platform, 15000),   // 默认即 env 覆盖链
  fetchOpts?: ProviderFetchOptions,                       // {signal, timeoutBounds}
): Promise<Response>
```

**职责**：给一次 fetch 套上「可组合、双语义」的超时，并把错误信息标准化供 `requests.error` 列分诊。

内部分步（`fetchWithTimeout+8~+48`）：

1. **signal 组装**（+8~+9）：调用方 signal（客户端断连）先进数组。
2. **`timeoutMs <= 0` = 无超时**（+11~+12 注释）：`PROVIDER_TIMEOUT_X=0` 的语义；`setTimeout(abort, 0)` 会在下一个宏任务杀光所有请求，必须显式跳过。
3. **两种 bounds**（+14~+31）：
   - `timeoutBounds: 'request'`（+19~+23 注释）：**整请求期限**。timer 不清、只 `unref()`（+24）——200 之后 body 永远读不完也要杀（保 `res.json()` 不悬挂）；unref 保证花完的期限不留住进程。
   - 默认（headers-only，+26~+29 注释）：**响应头一到就 clearTimeout**（finally +47）。SSE 必须用这个——流的合法寿命超过任何固定期限，中段挂死归 stall watchdog 管。
4. **signal 合成**（+34~+40）：`AbortSignal.any`；**客户端 signal 永不解除**——undici 把它绑到整个请求，断连会连 body 读取和流迭代一起 error，reason 是带标记的 `newClientAbortError`（回退循环靠它区分「自家客户挂了」与「上游卡死」，10 篇 §7.8）。
5. **错误文案**（+43~+45）：`proxyFetch(url, init, platform, 'chat', timeoutMs)` 使 AbortError 读作 `groq, chat, 15s`——从仪表盘错误列直接分诊。

**坑**：`fetchWithTimeout` 的默认参数在**调用时**求值 `providerTimeoutMs(this.platform, 15000)`（+5），所以**没传超时**的适配器吃到的是 env > 15s；而 `OpenAICompatProvider` 的优先级不在这里落——构造函数（openai-compat.ts:122）在实例化时就把 env 压在注册 spec 上（`this.timeoutMs = providerTimeoutMs(platform, opts.timeoutMs ?? 60_000)`，+18，#547），请求时再传 `options?.timeoutMs ?? this.timeoutMs` 做 per-call 覆盖，于是实际次序是 **env > per-call > 注册 spec > 60s**。env 只在构造时读一次，改值要重启（provider-timeout.ts:5 注释言明）。

## 2. `readWithStallTimeout` + `firstByteBudgetMs`（base.ts:392/422）

```ts
protected async readWithStallTimeout<T>(read: () => Promise<T>,
  inactivityTimeoutMs: number, timeoutMessage?: string): Promise<T>
protected firstByteBudgetMs(chatTimeoutMs: number, stallTimeoutMs: number): number
```

- 前者是 `Promise.race([read(), setTimeout(reject)])`（`readWithStallTimeout+7~+15`），`<=0` 直通（+5）；客户端 abort 的 rejection 原样穿过（undici 已用请求 signal 的 reason error 掉 body，这里不会误报 stall）。
- 后者两行（`firstByteBudgetMs+1~+2`）：`max(chat, stall)`，任一为 0 则 0（无界）。**存在理由**（`firstByteBudgetMs` 的头注释，base.ts:410-421）：chat 超时本意是「首 token 可以慢多久」，但在流式下它随响应头就被解除；NVIDIA NIM 这类「秒回 headers、prefill 几分钟」的 provider 会让第一口 read 无人看守。下限取 stall 预算，保证不会被改得比 #584 之前更严。

## 3. `readSseStream` / `readSseFrames`（base.ts:458-524）

```ts
protected async *readSseStream(res, opts?): AsyncGenerator<ChatCompletionChunk>
// 实现 = extractThinkTagsFromStream(this.readSseFrames(res, opts))
```

`readSseFrames`（base.ts:465；`readSseStream` 458-463 只是它外面套的一层）是 **OpenAI 线格式**流式响应共用的 SSE 读取器，口径可复跑：`grep -rn 'this\.readSseStream(' server/src/providers/*.ts` = 4 处调用（openai-compat.ts:518、cohere.ts:128、moondream.ts:115、cloudflare.ts:161）；`grep -rln 'super.streamChatCompletion' server/src/providers/*.ts | wc -l` = 16 个文件再经继承落到 openai-compat 那条。按「注册行 → 实际流式实现」对齐后的结论：`grep -cE '^\s*register\(' server/src/providers/index.ts` = **73 个注册 provider，其中 60 个的流最终进 `readSseFrames`**；剩下的 13 个是 GoogleProvider（自解析 Gemini 线格式）、5 个搜索类（tavily / exa / firecrawl / linkup / serpsearch）与 aclide、sail、freeai、speechify、aihorde、beatapi 这些自写流的。`new OpenAICompatProvider` 在 index.ts 出现 34 次（33 处注册 + 1 处 `resolveProvider` 现造 custom 实例）。google.ts 不进 `readSseFrames`，但复用 §2 的 `readWithStallTimeout`（google.ts:718-719）与 `firstByteBudgetMs`（google.ts:712）。

三个预算取值（`readSseFrames+13~+19`）：

```
inactivityTimeoutMs = opts?.stallTimeoutMs ?? streamStallTimeoutMs(platform)  // 默认 90s，0 关
chatTimeoutMs       = opts?.firstByteTimeoutMs ?? providerTimeoutMs(platform, 15000)
firstByteMs         = this.firstByteBudgetMs(chatTimeoutMs, inactivityTimeoutMs)
```

循环骨架（`readSseFrames+26~+58`）：

1. **第一口 read 用 firstByteMs，之后每次用 stall 预算**（+28~+31；`awaitingFirstByte` 在 +24 置位、+31 复位）——「慢」与「卡死」分治。
2. 增量解码（+34~+42）：`buffer.split('\n')`，残段留 buffer；只认 `data:` 行；`[DONE]` **return（正常结束）**。
3. 每帧 JSON.parse 成功才 yield（+43~+46）；**坏帧静默跳过**（+47~+49 的空 `catch`）；任一 choice 带非空 `finish_reason` ⇒ `sawFinishReason=true`（+45）。
4. `finally { reader.cancel() }`（+52~+54）——消费者提前 break（客户端断开）时释放上游。
5. **循环自然结束但 `!sawFinishReason` ⇒ 抛「stream ended unexpectedly」**（+56~+58）：EOF 前既无 `[DONE]` 又无 finish_reason 是**截断生成**，不是完成。修复前它被静默收尾、按成功记账（响应「就是停了」，#553）；抛出的文案被 `isRetryableError` 直接命中（`lib/error-classify.ts:94`），于是回退循环按 retryable 通道轮换下一跳。

外层 `readSseStream`（+0~+5，调用在 +4）再套 `extractThinkTagsFromStream`（lib/think-tags.ts:163）：DeepSeek 式把推理写进 `delta.content` 的 `<think>…</think>` 内联块被搬去 `delta.reasoning_content`——下游永远不把思考当答案渲染；无标签的流逐字节原样转发。

## 4. `validationResult`（base.ts:295）

```ts
protected async validationResult(res: Response): Promise<KeyValidationResult>
// true | {valid:false, error:'…'} | throw
```

- 非 401/403 → `true`（+1）（**其他状态一律视为「key 有效」**——validate 打的是 models/catalog 端点，5xx 说明不了 key）。
- `cf-mitigated: challenge` 头 → **throw**（+2~+4 注释，throw 在 +5~+7）：Cloudflare bot 挑战是对调用方 IP/UA 说话，不是对 key；抛错让健康服务记「无定论」，**永不自动禁用好 key**（#1298）。
- 401/403 → 从六种 body 形状（`error.message / errors[0].message / message / detail / title / statusText`，+16~+23）里找第一个非空字符串拼进 error——把「invalid」升级成「invalid, because 上游说了 X」。

## 5. `OpenAICompatProvider.chatCompletion`（openai-compat.ts:322）

```ts
async chatCompletion(apiKey, messages, modelId, options?, quotaContext?)
  → Promise<ChatCompletionResponse>
```

**请求组装**（+7~+26：`samplingForModel` 在 +7，body 字段块 +15~+26）——每个字段背后一个平台差异机制：

| 字段 | 机制 |
|---|---|
| `sampling` | `samplingForModel`（229-241）：只改写 Requesty 的 `mistral/leanstral-1-5` + `temperature=0`（该路由拒绝 greedy sampling）→ 去掉温度、补 `top_p ?? 1`；其余请求原样透传 |
| `max_tokens` | `resolveMaxTokens(platform, max_tokens, contextBudget)`（+19；lib/sampling-params.ts:386）：预算夹紧 |
| `messages` | `messagesForPlatform`（255-320，用于 +17）：strict 平台集合 `mistral/groq/cerebras`（`STRICT_PLATFORMS`=254）按 key 白名单重建消息；其余路径剥掉 assistant `partial`（#1038）；`radeon` 的 `Qwen3.8-Flash-Next` 把多条 system 合成一条（311-317） |
| `parallel_tool_calls` | `resolveParallelToolCalls`（151-154，用于 +24）：spec `forceSingleToolCall` 且带 tools → false（NVIDIA NIM「This model only supports single tool-calls at once!」，#255） |
| `...extendedBodyParams` | reasoning 等平台私参透传（+25；lib/sampling-params.ts:335） |

随后 `fetchWithTimeout(..., timeoutBounds: 'request')`（+27~+29 注释：非流式必须连 body 读取一起 bounded）+ `recordQuotaObservationsFromResponse`（+31~+38，响应头里的配额观测顺手落库，永不影响返回值）。

**四个非平凡出口**：

1. **`!res.ok` + rescue**（+40~+59）：`rescueFailedGeneration`（166-189，#264）——某些 provider 以 **HTTP 错误 body** 返回已经生成的 tool call（`tool_use_failed` 形态）；解析成功就**当场伪造一个合法的 tool_calls 响应返回**（+45~+54：`finish_reason: 'tool_calls'`、usage 全 0、照样带 `_routed_via`），流式版则 yield 三帧（role → tool_calls → finish，见 §6）后正常收束。救不回来先试 **pinned tool_choice 单次重试**（+56~+57，`pinnedToolChoiceRetryFor`=194-199：custom 端点对钉住某个函数的 `tool_choice` 回 400 时，改用 `"required"` + 把 tools 收窄到那个函数再发一次，#1548；重试请求本身不再满足条件，所以不可能连环重试）。两条都不成立才 `providerHttpError`（+58；保留 status + 上游原文，`upstreamErrorText`=206-212 按 `error.message / detail / title / statusText` 归一，NVIDIA 的 RFC7807 体靠它才不被压成 "Bad Request"，#522）。
2. **parse 抛错但属 abort**（+63~+72）：`isAbortLikeError`（+69）⇒ **原样 rethrow**——期限/断连不是「畸形 body」，不该被归进下面的兼容性诊断（否则 10 篇 §7 的 hedge/client-abort 分类全被打乱）。
3. **200 非 JSON 的一分为二**（+73~+115，#430 事故记录在 +74~+91）：
   - 截断特征（`looksTruncated`，+101~+103：`Unexpected end of JSON input`，或 position 错误 **且** Content-Type 声称 JSON 且不是 NDJSON）⇒「上游 CDN 在 600s 边缘空闲处掐了慢响应」，文案让运营**重试或换快模型**（+104~+110）；
   - 其余 ⇒「不是 OpenAI 兼容端点」，文案直接教 Ollama/llama.cpp/vLLM/LM Studio 的 `/v1` 路径（+111~+114，形状判定依据见 +75~+81 的 #189 注释）。
   - 不拆分时两种混报一种，运营到处找不存在的 base-URL 配置错误。
4. **in-band 余额告**（+117~+126）：200 + 正文是充值提示（Pollinations 形态）⇒ 拼成 `402: insufficient credit` 字符串抛出（+124~+126）——让 `isPaymentRequiredError` 按真 402 处理（failover + 长 bench），而不是把「请充值」当回答返回给用户。判据是模块级 `inBandCreditsError`（56-66）：把每条 choice 的 `message.content` 用 `contentToString` 拼起来送进去（+121~+123），**刻意收紧**——必须同时出现 credits 措辞与 top-up/quest/Pollinations 标记，免得真在讨论额度的回答被误杀。

成功路径收尾：`normalizeChoices(data)`（+116）+ `data._routed_via = {platform, model}`（+127，诊断字段，05 篇）。

## 6. `streamChatCompletion`（openai-compat.ts:453）

与 5 同构，三处不同：

1. body 加 `stream: true, stream_options`（+26~+27）。
2. `fetchWithTimeout` **不传 timeoutBounds**（+31）——默认 headers 语义（+29~+30 注释：headers 一到期限退场，之后流归 client signal + stall watchdog）。
3. 出口：`yield* this.guardInBandCreditsError(this.readSseStream(res, { firstByteTimeoutMs: options?.timeoutMs ?? this.timeoutMs }))`（+64~+66，#584 的第一字节宽限从这条路传进 §3；+61~+63 是它的注释）。rescue 失败生成走三帧 yield（+45~+52：role → tool_calls → `finish_reason: 'tool_calls'`）；`pinnedToolChoiceRetryFor` 的重试在流式版是 `yield*` 递归再 `return`（+53~+57）。

`guardInBandCreditsError`（openai-compat.ts:532-552，由 `streamChatCompletion+64` 调用）：只检查**第一个 content-bearing chunk**（+5~+16 把各 choice 的 `delta.content` 拼串喂 `inBandCreditsError`），余额告是单条固定文案；`sawContent` 一旦置位，之后每帧原样 `yield`（+18），reasoning/role chunk 直接过（首 token 延迟不受影响）。抛出落在 proxy 的 commit point **之前**（529-530 注释言明），回退循环还能轮换下一跳——反例是「SSE 头已冲出 = `committed`，之后无法回退」（`topics/model调度算法.md` §5.1 的共同契约）。

## 7. `validateKey` 与 `fetchQuota`（openai-compat.ts:603/634）

```ts
validateKey(apiKey, quotaContext?) → fetchCatalogEndpoint(validateUrl ?? modelsUrl) → 默认 /models 还要验 JSON 形状 → §4 validationResult
```

- `fetchCatalogEndpoint`（570-594）把这类 GET 的策略收在一处：30s + `timeoutBounds: 'request'`（+12~+14，571-575 注释说明为什么不是 10s——高延迟区域取大 catalog 会超 10s，把健康 key 误标成 `error`），响应头配额观测顺手落库（+15~+21）；传输错误照实上抛，health 记 `status='error'` 但**不**计 auto-disable 次数（566-568）。
- #1557 分支（`validateKey+7~+15`）：没配 provider 专属 `validateUrl` 且 200 时，body 必须 `JSON.parse` 得过，否则抛 `providerHttpError`——已停摆/被停放的服务会对每个路径回 200 纯文本 "OK"，让所有 key 都看起来健康。带 `validateUrl` 的端点保留自己的形状，直接落到 §4（+16）。

quota 探测（#1403，注册 spec 驱动，如 openrouter 的 `GET https://openrouter.ai/api/v1/key`，`metric: 'credits'`，`limitFields`/`remainingFields`）：

- `fetchWithTimeout(spec.url, …, 10_000, {timeoutBounds:'request'})`（`fetchQuota+4~+10`）；spec 缺失 `return false`（+2）、非 2xx `return false`（+11）、传输/解析异常在 catch 里 `return false`（+51~+53）——「配额探针失败对 key 什么都不能说，调用方的健康判决必须只关于 key」（该句在 627-628，函数头注释块 622-629）。
- 取数：`data` 包裹层和顶层都查（+13~+15）；值接受**数字字符串**（SiliconFlow 把余额序列化成 `"88.88"`；`""`/null/散文不会 parse 成有限数，+22~+24 注释，判定在 +25~+28）。
- `limit` 与 `remaining` 全拿不到 ⇒ false（+35）；拿到就 `recordQuotaObservation(source:'quota_api', resetStrategy:'provider_reported')`（+36~+49），函数返回 `record !== null`（+50）。
- `hasQuotaProbe`（630-632 覆盖 base.ts:274-276）：**spec 存在与否**（`this.quotaProbe !== undefined`）才回答「有没有配额端点」——不能拿方法覆盖判断，base.ts:270-273 注释言明 `OpenAICompatProvider` 对每个实例都覆盖了 `fetchQuota`，`spec or not`。

## 8. `normalizeChoices`（openai-compat.ts:701）

上游形状矫正的收口点（模块级函数，原地改 `data`，每条 choice 三步）：

- `content` 是**文本段数组**（Mistral magistral）⇒ join 成字符串（+8~+12）。
- 内联 `<think>…</think>` 块（§3 那种 DeepSeek 写法）⇒ 搬到 `reasoning_content`（+18，`extractThinkFromMessage`=think-tags.ts:145），**必须在折叠之前**：只有思考块、块后没有答案的消息才不会留下空 content。
- `content` 为空串/null **且没有 tool_calls**（+24~+25），且 `reasoning_content`（Z.ai glm-4.5-flash、Cloudflare DeepSeek-R1-distill）或 `reasoning`（Ollama）非空（+26~+28）⇒ 折进 content（+29~+30）——OpenAI 兼容客户端不能看到空回答；有 tool_calls 时 `content=null` 才是正确形状，折叠会误骗按 content 分支的客户端。

## 9. 超时旋钮函数（lib/provider-timeout.ts）

```ts
parseTimeoutEnv(name, defaultMs)         // 29-41：唯一的 env 读取口
providerTimeoutEnvName(platform)         // 43-45：'PROVIDER_TIMEOUT_' + 大写 + 非[A-Z0-9]→'_'
providerTimeoutMs(platform, defaultMs)   // 51-53
DEFAULT_STREAM_STALL_TIMEOUT_MS = 90_000 // 55
streamStallTimeoutEnvName(platform)      // 57-59
streamStallTimeoutMs(platform?)          // 66-70：平台级 > 全局 > 90s，0 关
```

坏值（`!Number.isInteger(parsed) || parsed < 0`，33）一律回落到 default 并 `warnOnce`（23-27）——06 篇 §3 优先级链的读取端实现。**`0` 全程是合法值**（禁用），所以判据是 `parsed < 0` 而非 falsy 拒绝；`>0` 且小于 1000 会额外警告「是不是把秒当毫秒写了」（37-39）。chat 超时在 provider **构造时**读一次（5-6 注释，改 env 要重启），stall 看门狗则每次调用重读（61-62 注释）。

## 10. 风险与待补

| 级别 | 事项 |
|---|---|
| P2 | §3 的截断检测依赖上游发过 `finish_reason` 或 `[DONE]`；两者都不发且完整结束的 provider 会被误判截断（目前未观察到，但 spec 上无法排除） |
| P2 | §5.1 的 rescue 会**吞掉一次真实的上游失败**记账为成功——排查「tool call 时好时坏」时要记得有这条静默路径 |
| 待补 | `samplingForModel` / `extendedBodyParams` / `messagesForPlatform` 的完整平台矩阵（本篇按机制描述，未逐平台枚举） |
| 待补 | `GoogleProvider`（google.ts:553）等非 OpenAI 线格式适配器的函数级拆解：`chatCompletion`=564、`streamChatCompletion`=647-836、`validateKey`=838。它复用 §1 的 `fetchWithTimeout` 与 §2 的两个函数（712/718-719），但帧解析与截断抛错自写（834 行是同一句 `stream ended unexpectedly`），`validateKey` 也不走 §4——Google 把坏 key 回成 400、把权限/区域问题回成 403，判反了会自动禁用好 key（#268，857-868 注释） |

---

## 源码索引（绝对行号，以当前 checkout 为准）

- `server/src/providers/base.ts` — 229 `BaseProvider`（230 `platform`、231 `name`、238 `chatCompletion`、246 `streamChatCompletion`、254 `validateKey` 五个抽象成员；266-268 `fetchQuota` 默认实现、270-276 `hasQuotaProbe` 及其「方法覆盖不可作判据」注释、285-287 `supportsKeyValidation`）；289-324 `validationResult`（297-299 #1298 注释、300-302 cf-mitigated throw、311-318 六种 body 形状）；326-375 `fetchWithTimeout`（331 env 默认值、337-338 `timeoutMs<=0`、344-350 request bounds、351-356 headers-only、360-366 signal 合成、369-371 AbortError 文案、373 finally）；381-408 `readWithStallTimeout`（381-391 #553/#584 注释、397 `<=0` 直通、399-407 race）；410-425 `firstByteBudgetMs`（410-421 注释）；427-431 `firstByteTimeoutMessage`；433-463 `readSseStream`（458-463 实现，462 套 `extractThinkTagsFromStream`）；465-524 `readSseFrames`（472-477 #553/#584 注释、478/483/484 三个预算、493-495 首口 read、508-514 帧解析、517-519 finally、521-523 截断抛错）；525 文件尾
- `server/src/providers/openai-compat.ts` — 47-66 `inBandCreditsError`；68-82 `pinnedToolChoiceRetry`；89-100 `QuotaProbeSpec`；102 `class OpenAICompatProvider`；103-120 实例字段；122-145 构造函数（139-140 #547：env 压注册 spec）；147-154 `resolveParallelToolCalls`；156-189 `rescueFailedGeneration`（def 166-189）；191-199 `pinnedToolChoiceRetryFor`；201-212 `upstreamErrorText`；214-224 `authHeader`；226-241 `samplingForModel`；243-320 `messagesForPlatform`（254 `STRICT_PLATFORMS`、293-305 `partial` 剥离、307-317 radeon system 合并）；322-451 `chatCompletion`（349-351 request bounds、362-381 `!res.ok`、385-394 abort 直通、395-437 200 非 JSON 拆分、439-448 in-band 余额告）；453-520 `streamChatCompletion`（479-480 stream 字段、482-484 headers bounds、498-505 三帧 rescue、514-519 出口）；522-552 `guardInBandCreditsError`（def 532-552）；554-557 `modelsUrl`；559-594 `fetchCatalogEndpoint`（571-575 30s 依据、584 bounds）；596-601 `fetchModelCatalog`（#488）；603-620 `validateKey`（605-609 #1557 注释、610-618 JSON 形状闸）；622-629 配额探测注释（627-628「对 key 什么都不能说」）、630-632 `hasQuotaProbe`、634-689 `fetchQuota`（645/685-687 false 出口、647-649 `data` 包裹、656-658 数字字符串注释、670-683 记账）；692-733 `normalizeChoices`（def 701-733）
- `shared/types.ts` — 531 `TokenUsage`；546 `ChatCompletionResponse`；559 `ChatCompletionChunk`（provider 层的请求/响应形状都出自这里，不在 `providers/base.ts`）
- `server/src/lib/provider-timeout.ts` — 1-19 旋钮语义头注释（5-6「构造时读取，改值要重启」）；23-27 `warnOnce`；29-41 `parseTimeoutEnv`（33 判据、37-39 秒/毫秒警告）；43-45 `providerTimeoutEnvName`；51-53 `providerTimeoutMs`；55 `DEFAULT_STREAM_STALL_TIMEOUT_MS`；57-59 `streamStallTimeoutEnvName`；66-70 `streamStallTimeoutMs`；73-75 `resetTimeoutWarnings`（文件共 75 行）
- `server/src/providers/index.ts` — 51-54 google 60s 注册例；160-174 NVIDIA（160-162 #255、163-167 #584 注释、168-174 register、173 `timeoutMs: 180_000`）；183-203 openrouter（196-202 `quotaProbe`，`GET https://openrouter.ai/api/v1/key`，`metric:'credits'`）；616-620 custom 占位注册；624 `CUSTOM_PROVIDER_TIMEOUT_MS`；626-628 `getProvider`；636-648 `resolveProvider`（640 现造 custom 实例、644 用该常量）；650-656 `getAllProviders`/`hasProvider`
- `server/src/lib/think-tags.ts` — 145 `extractThinkFromMessage`；163 `extractThinkTagsFromStream`
- `server/src/lib/error-classify.ts` — 6 `isRetryableError`；94 命中 `stream ended unexpectedly`（§3 的截断抛错由此进 retryable 通道）
- `server/src/lib/sampling-params.ts` — 335 `extendedBodyParams`；386 `resolveMaxTokens`
- 调用点 — `routes/proxy.ts:2453`/`2835`、`routes/anthropic.ts:933`/`715`、`routes/responses.ts:1281`/`1519`（chat/stream）；`services/health.ts:270`/`387`（`validateKey`）、`services/health.ts:209`（`fetchQuota`）

---

上一篇 → [10-函数级走读-路由限流与回退](./10-函数级走读-路由限流与回退.md) ｜ 下一篇 → [12-函数级走读-存储配置与请求入口](./12-函数级走读-存储配置与请求入口.md) ｜ [返回索引](./README.md)
