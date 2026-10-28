# 报告 · 11-函数级走读-Provider与流式.md（正文语义债，第二轮）

文档：docs/adrian/sourceReader/11-函数级走读-Provider与流式.md（改前 173 行 → 改后 186 行，全部为小节内改句/补句，未增删章节、未改章节编号）
每处改动改前 grep/Read/sed 源码，改后立即 `grep -n` 回读磁盘确认。
RULES2 第 7 条自检 grep 最终为空（exit=1）；附加自检 `recordFailure|listProviders|convertMessages|ChatRequest` 亦为空。
本轮**未改任何 .ts**（`git diff --name-only | grep .ts` 为空），未 commit。

行号说明：下面的 `文档:NN` 是**改前**行号（173 行版本）；正文锚点一律 `符号名+偏移`，文末索引给绝对行号。

## A（符号已消失/错名 → 真实名+真实位置）

- A 文档:120 `guardInBandCreditsError`（+499）-> `guardInBandCreditsError`（openai-compat.ts:532-552，由 `streamChatCompletion+64` 调用） (证据: `private async *guardInBandCreditsError(`=532，函数止 552；调用点 517-519=453+64~+66。`+499` 是旧绝对行号，按偏移读不可能成立（453+499=952 > 文件 733 行）)
- A 文档:133 `hasQuotaProbe`（+583）-> `hasQuotaProbe`（630-632 覆盖 base.ts:274-276），判据写实名 `this.quotaProbe !== undefined` (证据: sed 读 630-632 原文；基类 `get hasQuotaProbe`=base.ts:274-276，其 270-273 注释即「OpenAICompatProvider overrides the method for every instance, spec or not」)
- A 文档:52 「全部 33 个 provider 共用的 SSE 读取器」-> 真实符号级描述：4 处 `this.readSseStream(` 调用（openai-compat.ts:518、cohere.ts:128、moondream.ts:115、cloudflare.ts:161）+ 16 个文件经 `super.streamChatCompletion` 继承 (证据: `grep -rn 'this\.readSseStream(' server/src/providers/*.ts` → 4 行；`grep -rln 'super.streamChatCompletion' server/src/providers/*.ts | wc -l` → 16)
- A 文档:110 正文只写「in-band 余额告」未给判据函数 -> 补 `inBandCreditsError`（openai-compat.ts:56-66，调用在 chatCompletion+121~+123）与「credits 措辞 + top-up/quest/Pollinations 双条件」判据 (证据: sed 读 47-66 原文，`mentionsCredits`=59-60、`topUpMarker`=61-64)
- A 文档:102 §5 出口 1 漏符号 -> 补 `pinnedToolChoiceRetryFor`（194-199，chat 用 +56~+57、stream 用 +53~+57；模块级 `pinnedToolChoiceRetry`=68-82，#1548） (证据: grep 定义行 + sed 读 191-199/68-82 注释原文)
- A 文档:94 `messagesForPlatform`「平台消息整形」补全为三条真实机制：`STRICT_PLATFORMS`=254（mistral/groq/cerebras）白名单重建、非 strict 剥 assistant `partial`（293-305，#1038）、`radeon` 的 `Qwen3.8-Flash-Next` 合并 system（307-317） (证据: sed 读 243-320 原文逐行核对)
- A 文档:92 `samplingForModel`「per-model 温度覆盖」-> 只改写 Requesty `mistral/leanstral-1-5` + `temperature=0`（229-241，返回 `{temperature: undefined, topP: options.top_p ?? 1}`），其余原样透传 (证据: sed 读 226-241；原断言「per-model 温度覆盖」过宽，实际只有一个特例)
- A 文档:145-148（§8）漏 `extractThinkFromMessage` 这一步 -> 补为三步（+8~+12 数组 join、+18 think 提取、+24~+30 折叠） (证据: `extractThinkFromMessage(msg)`=719，函数头注释 714-718 写明「BELOW 之前」；`extractThinkFromMessage`=think-tags.ts:145)

## B（数字/断言过期 → 实测口径）

- B 文档:52 「33 个 provider」-> 「73 个注册 provider 中 60 个的流最终进 `readSseFrames`」，并列出 13 个例外（GoogleProvider + tavily/exa/firecrawl/linkup/serpsearch + aclide/sail/freeai/speechify/aihorde/beatapi） (证据: `grep -cE '^\s*register\(' server/src/providers/index.ts` → 73；按「注册类 → 是否 `this.readSseStream(` 或 `super.streamChatCompletion` 或本层未覆盖 stream」逐级判定 → reach=60 / not=13；`grep -c 'new OpenAICompatProvider' server/src/providers/index.ts` → 34 = 33 处注册 + 1 处 `resolveProvider`（636-648）现造 custom 实例)
- B 文档:94 表格 `new OpenAICompatProvider` 计数口径写清（33 注册 + 1 工厂） (证据: 同上一条命令 + sed 读 640)
- B 文档:150 「坏值（非数字/负）一律忽略回落」-> 「`!Number.isInteger(parsed) || parsed < 0` 回落 default 并 `warnOnce`；>0 且 <1000 另发秒/毫秒警告」 (证据: provider-timeout.ts:33、34、37-39；`warnOnce`=23-27；`parseTimeoutEnv`=29-41)
- B 文档:150 「判据都是 `< 0` 拒绝而非 falsy 拒绝」补上两侧真实读取处 (证据: `timeoutMs > 0`=base.ts:340、`<=0` 直通=397、`firstByteBudgetMs` 的 423；stall 侧 61-62 注释「resolved per call」对比 5-6 注释「read when the provider is constructed」)
- B 文档:168 §10 待补行「GoogleProvider 等复用 §1~§4」-> 只复用 §1、§2 (证据: google.ts 无 `this.readSseStream(`、无 `this.validationResult(`；自有帧解析 700-836、834 行同句 `stream ended unexpectedly`；`validateKey`=838-… 自写 Google 错误分类（857-868 注释，#268 明确「400 才是坏 key、403 多为权限/区域」）；复用的只有 `fetchWithTimeout`(592/673/841) 与 `readWithStallTimeout`(718-719)/`firstByteBudgetMs`(712))
- B 文档:167 §9 索引「1-75 全部旋钮函数」-> 逐个符号行区间（23-27 / 29-41 / 43-45 / 51-53 / 55 / 57-59 / 66-70 / 73-75） (证据: grep -n 定义行 + awk 全文编号读)

## C（行号式锚点错位、小节内重写）

- C 文档:22 `内部分步（fetchWithTimeout-8~+52）` -> `+8~+48`（函数体 334-374） (证据: 签名 326；`sed -n '334p;374p'` → `const signals: AbortSignal[] = [];` / `if (headerTimer !== undefined) clearTimeout(headerTimer);`)
- C 文档:24-30 §1 五处分步偏移全部重算：signal 组装 `+14~+16`→`+8~+9`（334-335）；`timeoutMs<=0` 注释 `+21~+23`→`+11~+12`（337-338）；两种 bounds `+25~+47`→`+14~+31`（340-357，request-bounds 注释 `+19~+23`=345-349，`unref` `+24`=350，headers-only 注释 `+26~+29`=352-355，`clearTimeout` finally `+50`→`+47`=373）；signal 合成 `+52~+58`→`+34~+40`（360-366）；错误文案 `+60~+64`→`+43~+45`（369-371） (证据: 每条都用 `awk 'NR>=x && NR<=y {printf "%d(=+%d)", NR, NR-326}'` 打印行号+偏移逐行核对)
- C 文档:32 「注册 spec 与 env 的优先级（env > spec > 15s）就是在这里落的」为**错误归属**，重写：`fetchWithTimeout` 默认参数（base.ts:331=+5）只给「没传超时」的适配器 env > 15s；env 压注册 spec 落在构造函数 `this.timeoutMs = providerTimeoutMs(opts.platform, opts.timeoutMs ?? 60_000)`（openai-compat.ts:140=构造函数+18，#547），per-call 覆盖在 `options?.timeoutMs ?? this.timeoutMs`（351/484）→ 实际次序 env > per-call > spec > 60s；并补「env 只在构造时读一次」（provider-timeout.ts:5-6） (证据: sed 读 139-140、349-351、482-484、provider-timeout.ts:5-6 原文)
- C 文档:43 `（+395 起注释）` -> `firstByteBudgetMs` 头注释 base.ts:410-421（**非偏移**：注释在签名 422 之前）；同时给 `readWithStallTimeout+7~+15`（399-407）、`+5`（397 直通）、`firstByteBudgetMs+1~+2`（423-424） (证据: `sed -n '410p;421p'` → `  /**` / `   */`；report-10-12 猜的 409-420 中 409 是空行、420 少一行，实测块为 410-421)
- C 文档:55-57 §3 伪码变量名与实现对齐（`inactivityTimeoutMs`/`chatTimeoutMs`/`firstByteMs`，`opts?.stallTimeoutMs ?? …`），并给锚 `readSseFrames+13~+19`（478/483/484） (证据: sed 读 478、483、484 原文)
- C 文档:60-66 §3 骨架偏移重算：`-0~+45`→`+26~+58`（491-523）；步骤 1 `+28~+31`（493-496，flag 置位 +24=489、复位 +31=496）；步骤 2 `+34~+42`（499-507）；步骤 3 `+43~+46`/空 catch `+47~+49`（508-514）、`sawFinishReason` `+45`（510）；步骤 4 `+52~+54`（517-519）；步骤 5 抛错 `+46~+48`→`+56~+58`（521-523） (证据: 逐行 awk 打印 465 起的偏移)
- C 文档:64 「坏帧静默跳过（**与旧行为一致**）」历史叙述 -> 直接指向源码空 `catch`（+47~+49，注释 `Skip malformed chunks`=513）
- C 文档:66 「现在抛错进回退循环的 retryable 通道」补可核判据 (证据: `isRetryableError`=lib/error-classify.ts:6，94 行 `|| msg.includes('stream ended unexpectedly')` 命中 base.ts:522 的文案；fallback-loop.ts:345 注释同口径)
- C 文档:68 内联思考块标签写作 `
</think>

`（三个连排标签）——按源码常量对齐为 `
</think>

` 单行写法：OPEN_TAG=`<think>`、CLOSE_TAG=`</think>` (证据: think-tags.ts:29-30；base.ts:454-456、openai-compat.ts:714-718 注释)
- C 文档:78 `（+258~+262 注释）` -> `validationResult+2~+4` 注释、throw `+5~+7`；另补 `true` 出口 `+1`（296）、六种 body 形状 `+16~+23`（311-318） (证据: sed 读 296-318；base.ts:258-262 实为 `fetchQuota` 的函数头注释区，与本条无关)
- C 文档:88/98 §5 组装偏移：`+5~+23`→`+7~+26`（329-348，字段块 +15~+26）；`fetchWithTimeout` 注释 `+24~+32`→`+27~+29`（349-351）；`recordQuotaObservationsFromResponse` `+31~+38`（353-360）
- C 文档:102-110 §5 四个出口偏移全部重算：`!res.ok` `+36~+51`→`+40~+59`（362-381，伪造响应 +45~+54、pinned 重试 +56~+57、`providerHttpError` +58）；abort 直通 `+57~+63`→`+63~+72`（385-394，`isAbortLikeError` +69=391）；200 非 JSON `+65~+109`→`+73~+115`（395-437，#430 注释 +74~+91、`looksTruncated` +101~+103、两个 throw +104~+110 / +111~+114、#189 依据 +75~+81）；in-band `+111~+118`→`+117~+126`（439-448，取数 +121~+123、throw +124~+126）；收尾 `normalizeChoices` +116（438）、`_routed_via` +127（449） (证据: awk 逐行打印 322 偏移；文案措辞「Ollama/llama.cpp/vLLM/LM Studio 的 /v1」按 434-435 原文补全)
- C 文档:116-118 §6 三处偏移：stream 字段 `+49~+51`→`+26~+27`（479-480）；headers 语义 `+53~+55`→`+29~+31`（482-484）；出口 `+481~+486`→`+64~+66`（517-519，#584 注释 +61~+63=514-516）；三帧 rescue `+470~+476`→`+45~+52`（498-505）；pinned 重试 +53~+57（506-510） (证据: awk 逐行打印 453 偏移)
- C 文档:120 `guardInBandCreditsError` 行为补真实判据位置：首帧检查 `+5~+16`（537-548）、`yield` 透传 `+18`（550）、commit-point 依据 529-530；「回退循环还能轮换下一跳」补反例契约（committed 之后不可回退，权威参考 `topics/model调度算法.md` §5.1）
- C 文档:125/130 §7 调用链补 `fetchCatalogEndpoint`（570-594：bounds 注释 +12~+14=582-584、观测落库 +15~+21=585-591、30s 依据 571-575、传输错误语义 566-568）与 **#1557 JSON 形状闸**（`validateKey+7~+15`=610-618，注释 605-609；带 `validateUrl` 才直接落 §4=+16/619） (证据: sed 读 603-620、559-594 原文)
- C 文档:130 `（577~581 注释）` -> 该句在 openai-compat.ts:**627-628**，注释块 622-629 (证据: sed 读 622-629；同时证伪「577~581」可作偏移：453+577 越界，绝对 577-581 现在是 fetchCatalogEndpoint 的 `method/headers` 行)
- C 文档:131 `（+600~602）` -> `fetchQuota+13~+15`（647-649 `data` 包裹层 + 顶层）；`（+609~+615 注释）` -> `fetchQuota+22~+24`（656-658 注释，判定代码 +25~+28=659-662）；并补三个 false/返回值锚：`+2`（636 spec 缺失）、`+11`（645 非 2xx）、`+51~+53`（685-687 catch）、`+35`（669 全拿不到）、`+36~+49`（670-683 记账）、`+50`（684 `return record !== null`） (证据: awk 逐行打印 634 偏移)
- C 文档:141-142 §8 折叠条件写全：`content === '' || content == null` **且无 tool_calls**（+24~+25=725-726），字段 `reasoning_content` **或** `reasoning`（Ollama）（+26~+28=727-729），折叠动作 +29~+30（730）；顺序依据 714-718 注释 (证据: sed 读 701-733 原文)
- C 文档:145-148 §9 伪码补 `parseTimeoutEnv`（29-41）、`streamStallTimeoutEnvName`（57-59）、`DEFAULT_STREAM_STALL_TIMEOUT_MS`（55），形参名 `fallback`→`defaultMs`（与 51 行一致）
- C 文档:165-169 文末索引整表同步：base.ts 补 `BaseProvider` 成员区（229/230/231/238/246/254/266-268/270-276/285-287）、`validationResult` 内部锚、`readSseStream` 头注释 433-457、`readWithStallTimeout` 注释起 **381**（原索引写 380-408，380 是空行）、`firstByteBudgetMs` 410-425（注释 410-421）、`readSseFrames` 内部锚（472-477/478/483/484/493-495/508-514/517-519/521-523）；openai-compat.ts 补 47-66 `inBandCreditsError`、68-82 `pinnedToolChoiceRetry`、89-100 `QuotaProbeSpec`、102 类、191-199、214-224、226-241、243-320（含 254/293-305/307-317）、522-552、554-557、559-594、596-601、622-629、634-689 内部分段、692-733；provider-timeout.ts 逐符号；index.ts 补 183-203 openrouter `quotaProbe`（196-202）、616-620 custom 占位、636-648 `resolveProvider`（640 现造实例、644 用常量）、650-656；新增 `shared/types.ts`、`lib/error-classify.ts`、`lib/sampling-params.ts`、调用点四行
- C 文档:3/5 引言与「调用位置回顾」补 `BaseProvider` 抽象契约（5 个抽象成员 + 3 个可选）、类型归属、真实调用点行号与实例来源 `resolveProvider` (证据: base.ts:230/231/238/246/254/266/274/285；routes/proxy.ts:2453/2835、anthropic.ts:933/715、responses.ts:1281/1519；services/health.ts:270/387/209；index.ts:636-648)

## SKIP

- SKIP 文档:100 「不拆分时两种混报一种」/ 文档:66 「修复前它被静默收尾」：保留（源码注释本身记录了事故前行为，openai-compat.ts:411-413、base.ts:444-446），非本轮语义债，且不属于我新增的历史叙述。
- SKIP 文档:85-88 §5 的 `chatCompletion` 签名伪码块：与 322-328 参数顺序一致，无需改。
- SKIP 文档:144-149 §9 标题与 06 篇交叉引用：编号未动。

## 推翻 / 修正清单与报告的地方

1. **推翻 report-10-12 doc11:43 的「409-420」**：base.ts 的 #584 first-byte 注释块实测为 **410-421**（409 空行、421 是 `   */`）。
2. **推翻 report-10-12 索引行的「380-408 readWithStallTimeout」**：注释起 **381**（380 是空行），已改 381-408。
3. **推翻待办 1 的「5 处」计数**：`+NNN` 形式的错锚实为 **9 处**，另 4 处未列——文档:78 `+258~+262`（base.ts:258-262 实为 fetchQuota 头注释，既非偏移也非目标行）、文档:118 `+481~+486`、`+470~+476`、文档:133 `+583`。
4. **推翻待办 2 给的测量命令**：`grep -rln 'readSseStream' server/src/providers | wc -l` = **6**，但其中 base.ts 是定义、google.ts 只在**注释**里提到该符号（706/709/813/826），把它算作「共用者」会得出错误分母。可用口径是 `grep -rn 'this\.readSseStream(' server/src/providers/*.ts`（4 处）与 `grep -rln 'super.streamChatCompletion'`（16 个文件），按注册行判定后为 **60/73**。
5. **待办 3 对 11 篇不适用**：正文从未把 `StreamChunk`/`ChatResponse`/`TokenUsage` 记在 `providers/base.ts` 名下——`grep -nE 'StreamChunk|ChatResponse|TokenUsage' docs/adrian/sourceReader/11-*.md` hits=0；本篇的真实缺口是「类型归属缺失」，已在文末索引补 `shared/types.ts` 531/546/559 一行（`TokenUsage`=531、`ChatCompletionResponse`=546、`ChatCompletionChunk`=559 实测成立）。
6. **待办 5 对 11 篇不适用**：`checkAndReserve`/`recordResult`/`recordFailure`/`listProviders`/`convertMessages` 在本篇 hits=0（RULES2 第 7 条自检 grep 改前改后均为空）。
7. **待办 4 的行号提示全部复核成立**：`chatCompletion`=322、`streamChatCompletion`=453、`validateKey`=603、`fetchQuota`=634、`normalizeChoices`=701、`class OpenAICompatProvider`=102、`CUSTOM_PROVIDER_TIMEOUT_MS`=index.ts:624（644 使用）；但 §5~§8 **小节内部的相对偏移**（报告标为「未逐一核对」）几乎全部漂移 8~15 行，本轮已按 `awk` 打印的 `NR-签名行` 重算。
8. **新发现（报告未列）**：§5 漏 `pinnedToolChoiceRetryFor`（#1548）、§7 漏 `validateKey` 的 #1557 JSON 形状闸、§8 漏 `extractThinkFromMessage` 与 `content==null`/无 tool_calls/`reasoning` 条件、§10 的「Google 复用 §1~§4」错（实际只复用 §1/§2）、§9 的坏值判据实为 `Number.isInteger` 检查。
9. **工具事故复盘（按任务要求记录）**：把内联思考标签字面量写进正文时，Edit 的入参被上游管线吞掉标签并插入换行，导致 §8 出现 4 行残缺（磁盘实测 line145=`- 内联 \``、line166=`</think>`）；另有一次 Edit 报「old_string 无匹配」但前一次自认 no-op 的 Edit 其实已落盘。最终用 `python3` 按行号重写该行并 `grep -n` 回读确认（现文档:145 为单行 `
</think>

` 写法，与 think-tags.ts:29-30 的常量一致）。结论与任务告诫一致：**一律以磁盘状态为准，每处改动回读一次**。
