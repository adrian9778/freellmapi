# 03-详细逐步说明-主链路拆解.md 锚点校正报告

文档：`docs/adrian/sourceReader/03-详细逐步说明-主链路拆解.md`（571 行，改后仍 571 行）
核对基准：当前 HEAD（分支 adrian）源码，逐个 `grep -n` / Read 确认。
统计：**FIXED 52**，**OK 4**，**SEMANTIC 待主线定夺 14 条**（其中 4 处锚点因文件归属错误未动数字：文档 253 / 索引 543、547、557）。

## FIXED

正文：
- FIXED  文档:26  `app.ts:115-140` -> `app.ts:113-218`  (证据: helmet 注册块首注释=113、`app.use(helmet(`=130、`cors(`=182、`express.json`=198-202、`clientContextMiddleware`=206、`createProxyRateLimiter`=215-218)
- FIXED  文档:47  `middleware/rateLimit.ts:1-80` -> `middleware/rateLimit.ts:34-78`  (证据: `export function createProxyRateLimiter`=34，闭括号=78)
- FIXED  文档:55  `config.ts:105` -> `config.ts:100-112`  (证据: `function parseTrustProxy`=100，闭括号=112；实际生效处 `app.set('trust proxy')`=app.ts:107)
- FIXED  文档:101  `proxy.ts:78-89` -> `routes/proxy.ts:81-92`  (证据: `export function extractApiToken`=81，闭括号=92；加目录前缀消歧，仓库另有 lib/proxy.ts)
- FIXED  文档:102  `lib/system-prompt.ts:1-120` -> `lib/system-prompt.ts:56-70`  (证据: `export function resolveAuth`=56，闭括号=70；文件归属其实正确——system-prompt.ts 仅 82 行，故 1-120 越界)
- FIXED  文档:103  `proxy.ts:66-73` -> `routes/proxy.ts:69-76`  (证据: `function requireInferenceAuth`=69，闭括号=76)
- FIXED  文档:124  `lib/content.ts:+50` -> `lib/content.ts:129`  (证据: `export function normalizeOutboundContent`=129)
- FIXED  文档:125  `lib/image-normalize.ts:+30` -> `lib/image-normalize.ts:282`  (证据: `export async function normalizeMessageImages`=282)
- FIXED  文档:126  `lib/tool-call-rescue.ts:+20` -> `lib/tool-call-rescue.ts:217`  (证据: `export function rescueInlineToolCalls`=217)
- FIXED  文档:127  `lib/structured-output.ts:+10` -> `lib/structured-output.ts:58`  (证据: `export function enforceJsonContent`=58)
- FIXED  文档:128  `lib/sampling-params.ts:+40` -> `lib/sampling-params.ts:166`  (证据: `export function pickSamplingParams`=166)
- FIXED  文档:129  `lib/task-type.ts:+10` -> `lib/task-type.ts:96`  (证据: `export function resolveTaskType`=96)
- FIXED  文档:130  `services/context-handoff.ts:+60` -> `services/context-handoff.ts:111`  (证据: `export function maybeInjectContextHandoff`=111)
- FIXED  文档:136  `router.ts:600-800` -> `router.ts:2152-2381`  (证据: `export function routeRequest`=2152，闭括号=2381)
- FIXED  文档:169  `router.ts:650-750` -> `router.ts:1437-1480`  (证据: `export function resolveRoutingChain`=1437，闭括号=1480)
- FIXED  文档:177  `router.ts:680-720` -> `router.ts:2304-2372`  (证据: 模型级过滤循环 `for (const entry of servingChain)`=2304~2372；见 SEMANTIC #3 关于 key 级闸门位置)
- FIXED  文档:192  `scoring.ts:200-300` -> `scoring.ts:534-541`  (证据: `export function combineScore`=534，闭括号=541=文件末)
- FIXED  文档:206  `router.ts:378-389` -> `router.ts:376-391`  (证据: headroom 阈值块首注释=376、`HEADROOM_RAMP_START_KEY`=380/`HEADROOM_FLOOR_KEY`=381、`getHeadroomThresholds`=383-391)
- FIXED  文档:207  `router.ts:270-336` -> `router.ts:267-338`  (证据: `// ── Dynamic priority` =267、`rateLimitPenalties`=269、`MAX_PENALTY`=274、`recordModelFailure`=285、`getPenalty`=326-338)
- FIXED  文档:210  `scoring.ts:44-54` -> `scoring.ts:49-59`  (证据: `export const BANDIT_PRESETS`=49，闭括号=59)
- FIXED  文档:220  `scoring.ts:160-194` -> `scoring.ts:181-199`  (证据: `export function peakAdjustedWeights`=181，闭括号=199；`PEAK_EXEMPT_STRATEGIES`=121、`isPeakHours`=165)
- FIXED  文档:225  `ratelimit.ts:250-400` -> `ratelimit.ts:312-356`  (证据: 现存的预检闸门 = `canMakeRequest`312-332 + `canUseTokens`334-356；见 SEMANTIC #5)
- FIXED  文档:247  `ratelimit.ts:27` -> `ratelimit.ts:1112`  (证据: `export function getCooldownDecisionForLimit`=1112；ratelimit.ts:27 现为 `pruneTimestamps`)
- FIXED  文档:330  `providers/base.ts:1-250` -> `providers/base.ts:229-525`  (证据: `export abstract class BaseProvider`=229，类闭括号=525=文件末)
- FIXED  文档:372  `fallback-loop.ts:200-500` -> `fallback-loop.ts:1367-1660`  (证据: `async function runFallbackLoopAttempts`=1367，函数尾=1660=文件末；外层 `runFallbackLoop`=1348-1365)
- FIXED  文档:406  `fallback-loop.ts:157-195` -> `fallback-loop.ts:159-197`  (证据: `// ── Wall-clock retry budget` =159、`DEFAULT_FALLBACK_TIME_BUDGET_MS = 45_000`=172、`getFallbackTimeBudgetMs`=183-197)
- FIXED  文档:416  `proxy.ts:1000-1100` -> `routes/proxy.ts:2358-2833`  (证据: chat/completions 流式分支 `if (stream)`=2358，分支闭括号=2833；`flushHeaders`=2417、`writeChunk`=2446、`data: [DONE]`=2755-2757)

文末源码索引（§9）：
- FIXED  文档:529  `server/src/app.ts | createApp() 中间件链 | 115-140` -> `113-218`  (同上 文档:26)
- FIXED  文档:530  `middleware/rateLimit.ts | createProxyRateLimiter() | 1-80` -> `34-78`  (def=34，闭=78)
- FIXED  文档:531  `lib/system-prompt.ts | resolveAuth(), extractApiToken() | 1-120` -> `56-70`  (resolveAuth=56-70；见 SEMANTIC #10：extractApiToken 不在此文件)
- FIXED  文档:532  `routes/proxy.ts | requireInferenceAuth() | 66-73` -> `69-76`  (def=69，闭=76)
- FIXED  文档:533  `routes/proxy.ts | 主处理器 (规范化管线) | 500-900` -> `1643-3097`  (`proxyRouter.post('/chat/completions'`=1643，处理器 `});`=3097)
- FIXED  文档:534  `lib/content.ts | normalizeOutboundContent() | 50-150` -> `129-143`  (def=129，闭=143)
- FIXED  文档:535  `lib/image-normalize.ts | normalizeMessageImages() | 30-200` -> `282-320`  (def=282，闭=320)
- FIXED  文档:536  `lib/tool-call-rescue.ts | rescueInlineToolCalls() | 20-150` -> `217-246`  (def=217，闭=246)
- FIXED  文档:537  `lib/structured-output.ts | enforceJsonContent() | 10-80` -> `58-77`  (def=58，闭=77)
- FIXED  文档:538  `lib/sampling-params.ts | pickSamplingParams() | 40-120` -> `166-187`  (def=166，闭=187)
- FIXED  文档:539  `lib/task-type.ts | resolveTaskType() | 10-60` -> `96-104`  (def=96，闭=104)
- FIXED  文档:540  `services/context-handoff.ts | maybeInjectContextHandoff() | 60-150` -> `111-157`  (def=111，闭=157)
- FIXED  文档:541  `services/router.ts | routeRequest() | 600-800` -> `2152-2381`  (def=2152，闭=2381)
- FIXED  文档:542  `services/router.ts | resolveRoutingChain() | 650-750` -> `1437-1480`  (def=1437，闭=1480)
- FIXED  文档:544  `services/scoring.ts | combineScore(), reliabilityPosterior() | 200-300` -> `534-541`  (combineScore=534-541；reliabilityPosterior 另在 278-287，见 SEMANTIC #11)
- FIXED  文档:545  `services/scoring.ts | peakAdjustedWeights() | 176-194` -> `181-199`  (def=181，闭=199)
- FIXED  文档:546  `services/ratelimit.ts | checkAndReserve() | 250-400` -> `312-356`  (canMakeRequest=312 / canUseTokens=334-356；符号名不存在，见 SEMANTIC #5)
- FIXED  文档:549  `lib/fallback-loop.ts | runFallbackLoop() | 200-500` -> `1348-1365`  (def=1348，闭=1365)
- FIXED  文档:550  `lib/fallback-loop.ts | noteModelFailure(), benchKeyAcrossPlatform() | 89-155` -> `95-157`  (noteModelFailure=95-117，benchKeyAcrossPlatform=133-157)
- FIXED  文档:551  `lib/fallback-loop.ts | getFallbackTimeBudgetMs() | 181-195` -> `183-197`  (def=183，闭=197)
- FIXED  文档:552  `providers/base.ts | BaseProvider abstract | 1-250` -> `229-525`  (class=229，闭=525)
- FIXED  文档:553  `providers/google.ts | streamChatCompletion() | 100-500` -> `647-836`  (def=647，闭=836；class GoogleProvider=553)
- FIXED  文档:554  `providers/index.ts | getProvider() | 1-100` -> `626-628`  (def=626，闭=628；resolveProvider=636)
- FIXED  文档:555  `lib/crypto.ts | decrypt() | 50-100` -> `204-212`  (def=204，闭=212)
- FIXED  文档:556  `lib/request-log.ts | persistRequestAttempts() | 1-80` -> `171-188`  (def=171，闭=188)

## OK（核对后未改）

- OK  文档:34  `config.ts:20`  (已核实无误：`const DEFAULT_REQUEST_BODY_LIMIT_MB = 25;`=lib/config.ts:20)
- OK  文档:195  `scoring.ts:7-17`  (核心公式注释块：`base = w_rel·...`=8、`effective = base × headroom × rateLimit`=14、两个 factor 说明=16-17)
- OK  文档:245  `ratelimit.ts:151-194`  (块首注释 `// ── Provisional usage ──`=151，`provisionalRequests`=163 / `provisionalTokens`=172 / `provisionalProviderTokens` 尾=194)
- OK  文档:548  `services/ratelimit.ts | acquireLease(), releaseLease() | 127-144`  (acquireLease=126 注释/127 def，releaseLease=142-144)

## SEMANTIC（正文断言与当前源码不符，未改动正文）

1. **文档:253 / 543（§4.1 + 索引行）**：`router.ts:800-1100 "streamChatCompletion() 核心循环"` —— **router.ts 内不存在 streamChatCompletion**（`grep -n streamChatCompletion server/src/services/router.ts` 无命中）。本节实际描述的是 `routes/proxy.ts` chat/completions 的流式分支（`if (stream)`=2358-2833；provider 生成器调用 `route.provider.streamChatCompletion(...)`=2453-2457；成功记账 `recordUpstreamSuccess`=2764）加上 `lib/fallback-loop.ts` 的尝试循环（1367-1660，`route.release?.()`=1652）。因文件归属本身错误，**只报不改**。
2. **文档:225 / 546**：`checkAndReserve()` 在当前源码里**完全不存在**（全仓 grep 仅命中 docs/）。真实对应：`services/ratelimit.ts` 的 `canMakeRequest`=312、`canUseTokens`=334、`canUseProvider`=665、`canUseProviderMinute`=689、`canUseProviderTokens`=783、`canUseKeyConcurrency`=120、`acquireLease`=127、`isOnCooldown`=1255，以及 `services/key-budget.ts` 的 `checkMonthlyBudget`=92；把这些串起来"预检 + 取租约"的编排其实是 `services/router.ts:selectKeyForModel`=1582（调用点 1670-1700），而不是 ratelimit.ts 里的单个函数。
3. **文档:177（§3.2 过滤条件）**：伪代码列出的过滤条件并非位于 `resolveRoutingChain`（该函数只做链选择 + `filter(e => e.enabled)`=1472）。真实分布：模型级闸门在 `routeRequest` 走链 2304-2372（ruled-out 2310/2317、vision 2321、tools 2328、structured 2336、context window 2349、tpm 2364）+ 链前置过滤 2158/2260-2263/2292-2302；key 级闸门（enabled+healthy 查询 1593、`scopeAllows` 1604、cooldown 1660、并发 1669、rpm/rpd 1670、tpm/tpd 1671、provider caps 1661/1665/1672、月度预算 1677）在 `selectKeyForModel` 1582-1700。文档只给了一个区间，我按"模型级过滤块"落 2304-2372。
4. **文档:247**：措辞 "`ratelimit.ts:27` 导入" 与现状不符——ratelimit.ts:27 现为 `pruneTimestamps`；`getCooldownDecisionForLimit` 的定义=ratelimit.ts:1112，而"第 27 行导入"这个说法现在恰好对应 **`lib/fallback-loop.ts:27`**（import 列表内）。另 `services/fusion.ts:10` 也导入它。我把数字改成定义行 1112，"导入"二字未动。
5. **文档:281 / 547**：`recordResult()` / `recordFailure()` 在 `services/ratelimit.ts` 中**不存在**（全仓只有 routes/auth.ts 里同名的登录失败函数）。真实符号：`services/ratelimit.ts` 的 `recordRequest`=821-831、`recordTokens`=833-845；失败/成功记账在 `lib/fallback-loop.ts` 的 `recordUpstreamSuccess`=663、`recordRetryableFailure`=440、`recordAuthFailure`=651。索引行 547 的数字因此**未改**。
6. **文档:557**：索引把 `resolveRoutingChain()` 数据源归到 `server/src/services/model-state.ts` —— model-state.ts 内没有该符号（它管 models 行的 override/墓碑）。真正的链读取在 `services/router.ts`：`getActiveChain` / `getChainByProfileName` / `getChainByGlobalSort`（resolveRoutingChain=1437-1480）。数字**未改**。
7. **文档:330-343（§4.2 provider 契约）**：真实 `BaseProvider`（base.ts:229-525）只有 `abstract readonly platform`/`name`、`chatCompletion`=238、`streamChatCompletion`=246、`validateKey`=254；**没有 `listModels()` / `checkHealth()` / `getModelCapabilities()`**，也没有 `supportsStreaming` 字段。签名参数顺序是 `(apiKey, messages, modelId, options?, quotaContext)`，文档写成 `(modelId, messages, apiKey, opts)`（§4.1 mermaid 与 §4.2 代码片段同此问题）。
8. **文档:345-366（§4.3 统一响应类型，标注 `providers/base.ts`）**：`StreamChunk` / `ChatResponse` / `TokenUsage` 三个接口**不在 base.ts**；真实定义在 `shared/types.ts`：`TokenUsage`=531、`ChatCompletionChunk`=559（对应文档的 StreamChunk）、`ChatCompletionResponse`=546（对应 ChatResponse）、`ChatMessage`=489。名称也不一致（StreamChunk → ChatCompletionChunk）。
9. **文档:293-328（§4.2 google.ts 片段）**：google.ts 不使用 `GoogleGenerativeAI` SDK，也没有 `convertMessages()` / `normalizeChunk()` 方法（grep 均无命中）；真实实现是手写 fetch + `toGeminiContents`/`contentsForModel` 映射，`streamChatCompletion`=647-836。
10. **文档:82/86（§2.1 时序图）**：`extractApiToken(req)` 被画成 `lib/system-prompt.ts` 的调用；实际 `extractApiToken` 属 `routes/proxy.ts:81-92`，`resolveAuth` 才在 `lib/system-prompt.ts:56-70`（索引行 531 同样把两个符号并到一个文件下，我按 resolveAuth 落 56-70）。另 `ResolvedAuth` 真实形状是 `{kind:'unified'|'profile', profileId, name, systemPrompt}`（system-prompt.ts:39-41），文档写的是 `{type, keyId?, prompt?}`。
11. **文档:544**：该行把 `combineScore()` 与 `reliabilityPosterior()` 共用一个区间——两者不同段：`reliabilityPosterior`=278-287，`combineScore`=534-541（我按首位符号 combineScore 落 534-541）。
12. **文档:207**：公式 `rateLimitFactor = 1 - penalty / MAX_PENALTY` 少了一个阻尼系数——真实实现 `scoring.ts:488-491`：`1 - (p / MAX_PENALTY) * RATE_LIMIT_MAX_DAMP`，`RATE_LIMIT_MAX_DAMP = 0.6`（486）。
13. **文档:124/127/129（§2.2 每步转换语义）**：
    - `normalizeOutboundContent()`（content.ts:129-143）是**出站 chunk/message 的数组 content → string 收敛**，不是"任意 content → 统一 `ChatMessage[]`"（请求侧规范化另有 `contentToString` 等）。
    - `enforceJsonContent()`（structured-output.ts:58-77）是**响应文本的 JSON 修复/校验**（trim / 剥 fence / 截取），并不"注入 system prompt 强制 JSON"。
    - `resolveTaskType()`（task-type.ts:96-104）只返回 `'code' | 'chat' | undefined`（header 优先，其次从 tools/messages 派生），没有 `analysis` / `creative` 两档。
14. **文档:18 / 36-47 / 397-404（零散事实）**：
    - §0 图里"最多20次/**60s**"：`FALLBACK_MAX_RETRIES = 20`（fallback-loop.ts:69）正确，墙钟默认预算是 **45s**（`DEFAULT_FALLBACK_TIME_BUDGET_MS = 45_000`=172），与 §5.3 自相矛盾。
    - §1.1 顺序里 `compression()` 实际注册在 **app.ts:351**（路由挂载之后），不在 helmet 之后。
    - §1.2 代码片段是"滑动窗口 + timestamps[]"，真实 `createProxyRateLimiter` 是**固定窗口计数**（`WindowState {count, resetAt}`，rateLimit.ts:21-24、47-52），并额外做 `MAX_TRACKED_IPS`=10_000 剪枝与 X-RateLimit 头；429 的 `type` 是 `'rate_limit_error'`（70），文档写 `'rate_limit_exceeded'`。
    - §5.2 冷却表：402 走 `PAYMENT_REQUIRED_COOLDOWN_MS = DAY`（ratelimit.ts:963，即 24h，非"60min"）；401 走 `AUTH_FAILURE_COOLDOWN_MS = 5 * 60 * 1000`（fallback-loop.ts:627，即 5min，非"10min"）。
    - §6.2 `await persistRequestAttempts(requestId, attempts)`：真实是同步函数 `persistRequestAttempts(trace: RequestTrace)`（request-log.ts:171-188），由 `lib/fallback-loop.ts:1363` 在 `finally` 里调用（不在 proxy 处理器尾部，也不 await）。
