# 11 · 函数级走读：Provider 与流式

> 本篇逐函数拆解 provider 抽象层：`BaseProvider` 的四个共享机制函数（超时、stall、SSE 读、验证诊断）与 `OpenAICompatProvider` 的五个业务函数（chat/stream/validate/quota/normalize）。这一层的注释几乎每一条都对应一个线上事故编号，走读时把「函数行为」和「它防的事故」一起记。

调用位置回顾（03 篇）：`runFallbackLoop` 的 `hooks.dispatch` 内部调 `provider.chatCompletion / streamChatCompletion`，健康检查调 `validateKey`，quota 探测调 `fetchQuota`。

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

内部分步（`fetchWithTimeout-8~+52`）：

1. **signal 组装**（+14~+16）：调用方 signal（客户端断连）先进数组。
2. **`timeoutMs <= 0` = 无超时**（+21~+23 注释）：`PROVIDER_TIMEOUT_X=0` 的语义；`setTimeout(abort, 0)` 会在下一个宏任务杀光所有请求，必须显式跳过。
3. **两种 bounds**（+25~+47）：
   - `timeoutBounds: 'request'`：**整请求期限**。timer 不清、只 `unref()`——200 之后 body 永远读不完也要杀（保 `res.json()` 不悬挂）；unref 保证花完的期限不留住进程。
   - 默认（headers-only）：**响应头一到就 clearTimeout**（finally +50）。SSE 必须用这个——流的合法寿命超过任何固定期限，中段挂死归 stall watchdog 管。
4. **signal 合成**（+52~+58）：`AbortSignal.any`；**客户端 signal 永不解除**——undici 把它绑到整个请求，断连会连 body 读取和流迭代一起 error，reason 是带标记的 `newClientAbortError`（回退循环靠它区分「自家客户挂了」与「上游卡死」，10 篇 §7.8）。
5. **错误文案**（+60~+64）：`proxyFetch(url, init, platform, 'chat', timeoutMs)` 使 AbortError 读作 `groq, chat, 15s`——从仪表盘错误列直接分诊。

**坑**：默认参数在**调用时**求值 `providerTimeoutMs(this.platform, …)`，注册 spec 的 timeoutMs 与 env 覆盖的优先级（env > spec > 15s）就是在这里落的。

## 2. `readWithStallTimeout` + `firstByteBudgetMs`（base.ts:392/422）

```ts
protected async readWithStallTimeout<T>(read: () => Promise<T>,
  inactivityTimeoutMs: number, timeoutMessage?: string): Promise<T>
protected firstByteBudgetMs(chatTimeoutMs: number, stallTimeoutMs: number): number
```

- 前者是 `Promise.race([read(), setTimeout(reject)])`，`<=0` 直通；客户端 abort 的 rejection 原样穿过（undici 已用请求 signal 的 reason error 掉 body，这里不会误报 stall）。
- 后者一行：`max(chat, stall)`，任一为 0 则 0（无界）。**存在理由**（+395 起注释）：chat 超时本意是「首 token 可以慢多久」，但在流式下它随响应头就被解除；NVIDIA NIM 这类「秒回 headers、prefill 几分钟」的 provider 会让第一口 read 无人看守。下限取 stall 预算，保证不会被改得比 #584 之前更严。

## 3. `readSseStream` / `readSseFrames`（base.ts:458-524）

```ts
protected async *readSseStream(res, opts?): AsyncGenerator<ChatCompletionChunk>
// 实现 = extractThinkTagsFromStream(this.readSseFrames(res, opts))
```

`readSseFrames` 是全部 33 个 provider 共用的 SSE 读取器（google.ts 自parse线格式但复用 2 的函数）：

```
stallTimeoutMs = opts ?? streamStallTimeoutMs(platform)   // 默认 90s，0 关
chatTimeoutMs  = opts.firstByteTimeoutMs ?? providerTimeoutMs(platform, 15000)
firstByteMs    = this.firstByteBudgetMs(chatTimeoutMs, stallTimeoutMs)
```

循环骨架（`readSseFrames-0~+45`）：

1. **第一口 read 用 firstByteMs，之后每次用 stall 预算**（`awaitingFirstByte` 标志）——「慢」与「卡死」分治。
2. 增量解码：`buffer.split('\n')`，残段留 buffer；只认 `data:` 行；`[DONE]` **return（正常结束）**。
3. 每帧 JSON.parse 成功才 yield；**坏帧静默跳过**（与旧行为一致）；任一 choice 带非空 `finish_reason` ⇒ `sawFinishReason=true`。
4. `finally { reader.cancel() }`——消费者提前 break（客户端断开）时释放上游。
5. **循环自然结束但 `!sawFinishReason` ⇒ 抛「stream ended unexpectedly」**（+46~+48）：EOF 前既无 `[DONE]` 又无 finish_reason 是**截断生成**，不是完成。修复前它被静默收尾、按成功记账（响应「就是停了」，#553）；现在抛错进回退循环的 retryable 通道。

外层 `readSseStream` 再套 `extractThinkTagsFromStream`：DeepSeek 式把推理写进 `delta.content` 的 `<think>…</think>` 内联块被搬去 `delta.reasoning_content`——下游永远不把思考当答案渲染；无标签的流逐字节原样转发。

## 4. `validationResult`（base.ts:295）

```ts
protected async validationResult(res: Response): Promise<KeyValidationResult>
// true | {valid:false, error:'…'} | throw
```

- 非 401/403 → `true`（**其他状态一律视为「key 有效」**——validate 打的是 models/catalog 端点，5xx 说明不了 key）。
- `cf-mitigated: challenge` 头 → **throw**（+258~+262 注释）：Cloudflare bot 挑战是对调用方 IP/UA 说话，不是对 key；抛错让健康服务记「无定论」，**永不自动禁用好 key**（#1298）。
- 401/403 → 从六种 body 形状（`error.message / errors[0].message / message / detail / title / statusText`）里找第一个非空字符串拼进 error——把「invalid」升级成「invalid, because 上游说了 X」。

## 5. `OpenAICompatProvider.chatCompletion`（openai-compat.ts:322）

```ts
async chatCompletion(apiKey, messages, modelId, options?, quotaContext?)
  → Promise<ChatCompletionResponse>
```

**请求组装**（+5~+23）——每个字段背后一个平台差异机制：

| 字段 | 机制 |
|---|---|
| `sampling` | `samplingForModel`：per-model 温度覆盖 |
| `max_tokens` | `resolveMaxTokens(platform, max_tokens, contextBudget)`：预算夹紧 |
| `messages` | `messagesForPlatform`：平台消息整形（strict 平台集合 mistral/groq/cerebras） |
| `parallel_tool_calls` | `resolveParallelToolCalls`：spec `forceSingleToolCall` → false（NVIDIA「only supports single tool-calls」，#255） |
| `...extendedBodyParams` | reasoning 等平台私参透传 |

随后 `fetchWithTimeout(..., timeoutBounds: 'request')`（+24~+32 注释：非流式必须连 body 读取一起 bounded）+ `recordQuotaObservationsFromResponse`（响应头里的配额观测顺手落库，永不影响返回值）。

**四个非平凡出口**：

1. **`!res.ok` + rescue**（+36~+51）：`rescueFailedGeneration`(#264)——某些 provider 以 **HTTP 错误 body** 返回已经生成的 tool call（tool_use_failed 形态）；解析成功就**当场伪造一个合法的 tool_calls 响应返回**，流式版则 yield 三帧（role → tool_calls → finish）后正常收束。救不回来才 `providerHttpError`（保留 status + 上游原文，`upstreamErrorText` 归一形状）。
2. **parse 抛错但属 abort**（+57~+63）：`isAbortLikeError` ⇒ **原样 rethrow**——期限/断连不是「畸形 body」，不该被归进下面的兼容性诊断（否则 10 篇 §7 的 hedge/client-abort 分类全被打乱）。
3. **200 非 JSON 的一分为二**（+65~+109，#430 事故记录）：
   - 截断特征（`Unexpected end of JSON input`，或 position 错误 + Content-Type 声称 JSON）⇒「上游 CDN 在 600s 边缘空闲处掐了慢响应」，文案让运营**重试或换快模型**；
   - 其余 ⇒「不是 OpenAI 兼容端点」，文案直接教 Ollama/llama.cpp 的 `/v1` 路径（#189）。
   - 修复前两种混报一种，运营到处找不存在的 base-URL 配置错误。
4. **in-band 余额告**（+111~+118）：200 + 正文是充值提示（Pollinations 形态）⇒ 拼成 `402: insufficient credit` 字符串抛出——让 `isPaymentRequiredError` 按真 402 处理（failover + 长 bench），而不是把「请充值」当回答返回给用户。

成功路径收尾：`normalizeChoices(data)` + `data._routed_via = {platform, model}`（诊断字段，05 篇）。

## 6. `streamChatCompletion`（openai-compat.ts:453）

与 5 同构，三处不同：

1. body 加 `stream: true, stream_options`（+49~+51）。
2. `fetchWithTimeout` **不传 timeoutBounds**——默认 headers 语义（+53~+55 注释：headers 一到期限退场，之后流归 client signal + stall watchdog）。
3. 出口：`yield* this.guardInBandCreditsError(this.readSseStream(res, {firstByteTimeoutMs: 同一份 chat timeout}))`（+481~+486，#584 的第一字节宽限从这条路传进 §3）。rescue 失败生成走三帧 yield（+470~+476）。

`guardInBandCreditsError`（+499）：只检查**第一个 content-bearing chunk**——余额告是单条固定文案；第一帧之后逐字节透传，reasoning/role chunk 直接过（首 token 延迟不受影响）。抛出发生在 proxy 的 commit point **之前**，回退循环还能轮换下一跳。

## 7. `validateKey` 与 `fetchQuota`（openai-compat.ts:603/634）

```ts
validateKey(apiKey, quotaContext?) → fetchCatalogEndpoint(validateUrl ?? modelsUrl) → §4 validationResult
```

quota 探测（#1403，注册 spec 驱动，如 openrouter 的 `GET /api/v1/key`，metric:'credits'，limitFields/remainingFields）：

- `fetchWithTimeout(spec.url, …, 10_000, {timeoutBounds:'request'})`，**任何失败返回 false**——「配额探针失败对 key 什么都不能说，调用方的健康判决必须只关于 key」（577~581 注释）。
- 取数：`data` 包裹层和顶层都查（+600~602）；值接受**数字字符串**（SiliconFlow 把余额序列化成 `"88.88"`；`""`/null/散文不会 parse 成有限数，+609~+615 注释）。
- `limit` 与 `remaining` 全拿不到 ⇒ false；拿到就 `recordQuotaObservation(source:'quota_api', resetStrategy:'provider_reported')`。
- `hasQuotaProbe`（+583）：**spec 存在与否**才回答「有没有配额端点」——不能拿方法覆盖判断（OpenAICompatProvider 对所有实例都覆盖了 fetchQuota，base.ts 注释言明）。

## 8. `normalizeChoices`（openai-compat.ts:701）

上游形状矫正的收口点（原地改 data）：

- `content === ""` 且 `reasoning_content` 非空（Z.ai glm-4.5-flash、Cloudflare DeepSeek-R1-distill）⇒ 把 reasoning 折进 content——OpenAI 兼容客户端不能看到空回答。
- `content` 是**文本段数组**（Mistral magistral）⇒ join 成字符串。

## 9. 超时旋钮函数（lib/provider-timeout.ts）

```ts
providerTimeoutEnvName(platform)     // 'PROVIDER_TIMEOUT_' + 大写 + 非[A-Z0-9]→'_'
providerTimeoutMs(platform, fallback)
streamStallTimeoutMs(platform?)      // 平台级 > 全局 > 90s，0 关
```

坏值（非数字/负）一律忽略回落——06 篇 §3 优先级链的读取端实现。**`0` 全程是合法值**（禁用），所以判据都是 `< 0` 拒绝而非 falsy 拒绝。

## 10. 风险与待补

| 级别 | 事项 |
|---|---|
| P2 | §3 的截断检测依赖上游发过 `finish_reason` 或 `[DONE]`；两者都不发且完整结束的 provider 会被误判截断（目前未观察到，但 spec 上无法排除） |
| P2 | §5.1 的 rescue 会**吞掉一次真实的上游失败**记账为成功——排查「tool call 时好时坏」时要记得有这条静默路径 |
| 待补 | `samplingForModel` / `extendedBodyParams` / `messagesForPlatform` 的完整平台矩阵（本篇按机制描述，未逐平台枚举） |
| 待补 | `GoogleProvider` 等非 OpenAI 线格式适配器的函数级拆解（它们复用 §1~§4，只差 body/帧解析） |

---

## 源码索引（绝对行号，以当前 checkout 为准）

- `server/src/providers/base.ts` — 295-324 `validationResult`；326-375 `fetchWithTimeout`；380-408 `readWithStallTimeout` 与 #584/#553 注释；422-431 `firstByteBudgetMs`/`firstByteTimeoutMessage`；458-524 `readSseStream`/`readSseFrames`（521-523 截断抛错）；525 文件尾
- `server/src/providers/openai-compat.ts` — 103-120 spec 字段；122-145 timeoutMs 解析；151-154 `resolveParallelToolCalls`；166-189 `rescueFailedGeneration`；206-212 `upstreamErrorText`；255-320 `messagesForPlatform`；322-451 `chatCompletion`；453-520 `streamChatCompletion`；532-552 `guardInBandCreditsError`；603-620 `validateKey`；630-689 `hasQuotaProbe`/`fetchQuota`；701-732 `normalizeChoices`
- `server/src/lib/provider-timeout.ts` — 1-75 全部旋钮函数
- `server/src/providers/index.ts` — 51-54 google 60s 注册例；NVIDIA 180s/#584 注释（160-174）；`CUSTOM_PROVIDER_TIMEOUT_MS`（624）
- `server/src/lib/think-tags.ts` — `extractThinkTagsFromStream`

---

上一篇 → [10-函数级走读-路由限流与回退](./10-函数级走读-路由限流与回退.md) ｜ 下一篇 → [12-函数级走读-存储配置与请求入口](./12-函数级走读-存储配置与请求入口.md) ｜ [返回索引](./README.md)
