# 报告 · 04-核心模块与类关系.md（锚点校正）

文档：docs/adrian/sourceReader/04-核心模块与类关系.md（389 行，未改行数）
所有行号均在当前 HEAD 源码里用 grep -n / Read 逐个核实；改完每处都回读文档确认落盘（`git diff --stat` = 53 行改动，CR 字节数 0）。

## FIXED

- FIXED  147  base.ts:222-261 -> base.ts:229-276  (证据: `export abstract class BaseProvider` = providers/base.ts:229；abstract platform=230 / name=231 / chatCompletion=238 / streamChatCompletion=246 / validateKey=254；fetchQuota=266-268、hasQuotaProbe getter=274-276。旧区间 222-261 命中的是 KeyValidationFailure/KeyValidationResult(221-227)，现落在类声明行上。整个类体实际为 229-525)
- FIXED  162  base.ts:109-125 -> base.ts:111-132  (parseStatedRetryMs 定义=111，函数尾=132)
- FIXED  163  base.ts:145-151 -> base.ts:152-158  (providerHttpError 定义=152，尾=158)
- FIXED  164  base.ts:308-357 -> base.ts:326-375  (fetchWithTimeout 定义=326，尾=375)
- FIXED  165  base.ts:440-499 -> base.ts:458-524  (readSseStream=458-463，readSseFrames=465-524)
- FIXED  166  base.ts:277-306 -> base.ts:295-324  (validationResult 定义=295，尾=324；Cloudflare 分支=300-302)
- FIXED  170  providers/index.ts:47-58 -> providers/index.ts:57-68  (首个 OpenAICompatProvider 注册块 groq=57-61、cerebras=64-68；旧区间同样指向这两块（旧 47-58，整段 +10 漂移）)
- FIXED  192  providers/index.ts:63-100 -> providers/index.ts:70-115  (hosted catalog/Oracle 纪律注释簇：Sail 70-75、ElectronHub 92-93、Router9/Septor 96-98、五个网关 105-106、B.AI 113-115)
- FIXED  202  router.ts:267 -> router.ts:269  (const rateLimitPenalties = new Map<number,{count,lastHit,penalty}> = 269)
- FIXED  203  router.ts:263 -> router.ts:265  (const roundRobinIndex = new Map<string, number>() = 265，其上行 263 是空行)
- FIXED  204  router.ts:365-379 -> router.ts:367-381  (STRATEGY_KEY=367 … HEADROOM_FLOOR_KEY=381)
- FIXED  206  router.ts:270-274 -> router.ts:272-276  (PENALTY_PER_429=272 / PENALTY_PER_FAIL=273 / MAX_PENALTY=274 / DECAY_INTERVAL_MS=275 / DECAY_AMOUNT=276)
- FIXED  210  router.ts:1144-1212 -> router.ts:1204-1272  (orderChain 定义=1204，函数尾=1272)
- FIXED  226  router.ts:1150-1177 -> router.ts:1210-1237  (`if (!weights) {`=1210 + legacy priority 注释块至「one penalty position now means what it says」=1237)
- FIXED  228  router.ts:175-183 -> router.ts:177-185  (ChainRow.match_tier 文档注释 `/**`=177，字段=185)
- FIXED  230  router.ts:1137-1142 -> router.ts:1197-1202  (orderChain 头注释中 `sampled` 段落 1197-1202)
- FIXED  232  router.ts:1107-1128 -> router.ts:1167-1189  (applyReliabilityFloor 定义=1167，尾=1189；安全阀 return=1188)
- FIXED  237  router.ts:186-237 -> router.ts:188-239  (interface RouteResult=188，尾 `}`=239)
- FIXED  245  router.ts:47-129 -> router.ts:49-131  (class RouteError=49-62 / diagnostics=56；summarizeExhaustion=84-131)
- FIXED  291  fallback-loop.ts:93-115 -> fallback-loop.ts:95-117  (noteModelFailure 定义=95，尾=117；「Never SHORTEN an existing bench」注释=108-110)
- FIXED  297  scoring.ts:1-24 -> scoring.ts:1-23  (凸组合宣言头注释首行=1、末行=23，24 为空行)
- FIXED  306  scoring.ts:273-282 -> scoring.ts:278-287  (reliabilityPosterior 定义=278，尾=287)
- FIXED  307  scoring.ts:323-329 -> scoring.ts:328-334  (speedScore 定义=328，尾=334)
- FIXED  308  scoring.ts:331-347 -> scoring.ts:336-352  (#619 段落头=336，TIMEOUT_LATENCY_CAP_MS=352)
- FIXED  309  scoring.ts:395-399 -> scoring.ts:400-404  (intelligenceComposite 定义=400，尾=404；RANK_SCALE=31 在 398)
- FIXED  310  scoring.ts:379-383 -> scoring.ts:384-388  (TIER_VALUE=384，tierValue()=386-388)
- FIXED  313  scoring.ts:99-116 -> scoring.ts:104-121  (豁免注释 `/**`=104，PEAK_EXEMPT_STRATEGIES=121)
- FIXED  314  scoring.ts:204-215 -> scoring.ts:209-220  (注释 `/**`=209，TASK_EXEMPT_STRATEGIES=220)
- FIXED  315  scoring.ts:61-71 -> scoring.ts:66-77  (「Time-of-day dynamic ranking」块=66，IANA 理由段末行=77；实际 Intl 解析在 hourInTimezone=150-157)
- FIXED  323  health.ts:286 -> health.ts:371  (export type KeyProbeOutcome=371，路径 server/src/services/health.ts)
- FIXED  324  health.ts:87 -> health.ts:148  (recordValidationRateLimited 定义=148，尾=150；1h skip 常量=138)
- FIXED  325  health.ts:288-313 -> health.ts:373-401  (probeKeyValidity 定义=373，尾=401)
- FIXED  326  health.ts:323-332 -> health.ts:414-426  (markKeyHealthyFromRequest 定义=414，尾=426)
- FIXED  327  health.ts:383-399 -> health.ts:477-493  (interleaveByProvider 定义=477，尾=493；并发默认 8=17/45，半周期时间预算 HEALTH_PASS_TIME_BUDGET_MS=40)
- FIXED  328  health.ts:139-167 -> health.ts:200-228  (pollKeyQuota=200-220，supportsQuotaPolling=226-228；QUOTA_POLL_INTERVAL_MS=186)
- FIXED  347  App.tsx:53-60 -> App.tsx:55-62  (staleTime 注释块 55-62，`staleTime: 30_000`=63)
- FIXED  351  index.ts:455-492 -> cli/src/index.ts:455-492  (数字本就正确：main()=455-492；加 cli/src/ 前缀以消歧)
- FIXED  363  router.ts:267 -> router.ts:269
- FIXED  366  router.ts:1144-1183 -> router.ts:1204-1243  (orderChain 定义=1204，priority 分支 return 链尾=1243)
- FIXED  367  index.ts:57-65 -> server/src/index.ts:57-65  (数字正确：boot 注释=57-61，cleanupExpiredCooldowns() 调用=62；加 server/src/ 前缀消歧)
- FIXED  375  §9 base.ts BaseProvider 222-261 -> 229-276  (同 147)
- FIXED  376  §9 base.ts 35-151 -> 35-158  (parseRetryAfterMs=35-44 … providerHttpError 尾=158)
- FIXED  377  §9 base.ts 308-499 -> 326-524  (fetchWithTimeout=326 … readSseFrames 尾=524)
- FIXED  378  §9 providers/index.ts 44-200+ -> 54-620  (首个 register 调用=54，最后一个注册块 `}));`=620)
- FIXED  379  §9 router.ts 47-129 -> 49-131
- FIXED  380  §9 router.ts 151-237 -> 153-239  (interface ChainRow=153 … RouteResult 尾=239)
- FIXED  381  §9 router.ts 263-362 -> 265-364  (roundRobinIndex=265 … clearAllPenalties 尾=364)
- FIXED  382  §9 router.ts 1107-1212 -> 1167-1272
- FIXED  386  §9 scoring.ts 1-24 -> 1-23
- FIXED  387  §9 scoring.ts 44-254 -> 49-259  (BANDIT_PRESETS=49 … taskAdjustedWeights 尾=259)
- FIXED  388  §9 scoring.ts 273-399 -> 278-404
- FIXED  389  §9 health.ts 185-512 -> 246-606  (checkKeyHealth=246 … runHealthPass 尾=606)
- FIXED  390  §9 fallback-loop.ts 84-155 -> 86-157  (MODEL_FAILURE_WINDOW_MS=86 … benchKeyAcrossPlatform 尾=157)

## OK（已核实无误，未改）

- OK     161  base.ts:35-44  (parseRetryAfterMs 定义=35，body 尾=44；MAX_RETRY_AFTER_MS=30)
- OK     256  ratelimit.ts:14  (const windows = new Map<string, Window>()=14，key 格式注释=13)
- OK     261  ratelimit.ts:196-230  (retention-sweep 注释块首=196 … recordUsage 尾=230；DELETE 语句=226)
- OK     265  ratelimit.ts:50-194  (「In-flight leases」块首=50 … provisionalProviderTokens 尾=194；LEASE_MAX_AGE_MS=76)
- OK     279  ratelimit.ts:85-106  (getKeyConcurrencyLimit 注释=85，定义=98，尾=106)
- OK     340  client/src/lib/api.ts:44-49  (401/authentication_error 注释块 44-49，判定语句=50)
- OK     364  ratelimit.ts:208-230  (recordUsage 定义=208，尾=230)
- OK     365  ratelimit.ts:85-106
- OK     383  §9 ratelimit.ts 7-25  (interface Window=7-11，windows=14，getWindow=18-25)
- OK     384  §9 ratelimit.ts 50-194
- OK     385  §9 ratelimit.ts 208-230
- OK     351  同行 `config-files.ts:applyGeneratedFiles` 符号锚点仍有效：cli/src/config-files.ts:409-416，两阶段注释=406-408，`.backup-{timestamp}`=396，0600=401/403

## SEMANTIC（正文断言与当前源码不符，未改正文）

- SEMANTIC: 204 「`settings` 表 8 个 key」——实际持久化 routing_* 设置已有 13 个：367-381 的 11 个（其中 peak 是 4 件：adjust/start/end/**timezone**，不是文中「peak 三件」）+ MIN_RELIABILITY_FLOOR_KEY(417) + TASK_WEIGHT_SHARE_KEY(484)。锚点区间 367-381 已按真实首尾行修正，但「8 个」这句枚举本身过时。
- SEMANTIC: 323 「传输错误（DNS/超时/TLS）绝不写 error、绝不加失败计数」——前半句已不成立：services/health.ts:100-120 在连续传输失败后会 `UPDATE api_keys SET status = 'error'`（park，#1510），349 行注释明确「连续 N 次探测失败才 park」；仍然不递增的是自动禁用用的 failureCount（321/337 路径）。即「首次不写、连续才写」，不再是「绝不写」。
- SEMANTIC: 9 / 67 / 163 / 190 / 378 「33 个上游适配器 / 持有 33 个单例 / register(...) ×33」——providers/index.ts 现有 73 个顶层 `register(...)` 调用，其中 33 个是 OpenAICompatProvider；「33」如今恰好等于 compat 实例数而不是平台总数。
- SEMANTIC: 170-187 示例代码把两个注册块拼在一起：`platform:'nvidia' + forceSingleToolCall + timeoutMs:180_000` 来自 index.ts:168-174，`extraHeaders` 与 `quotaProbe`(#1403) 来自 openrouter 块 184-203；锚点 57-68（旧锚点的等价位置）不含这些字段。若要逐字对应，宜改指 168-203。
- SEMANTIC: 147/§2.1 抽象成员清单本身仍然正确（chatCompletion / streamChatCompletion / validateKey 为 abstract，fetchQuota / hasQuotaProbe 为可选覆盖）；但 §1 类图（17-32）缺了后来加的成员：`supportsKeyValidation` getter（285-287，#1459 探活豁免）、`firstByteBudgetMs`(422) / `firstByteTimeoutMessage`(429)、private `readSseFrames`(465)。
- SEMANTIC: 74/67 之外的类图细节：providersRegistry 一节写的 `+hasPlatform(platform)` 在源码里从来叫 `hasProvider`（index.ts:654），另有 `getAllProviders()`(650) 未列。
- SEMANTIC: 99 「BANDIT_PRESETS: Record~Strategy, Weights~」——现为 `Record<PresetStrategy, RoutingWeights>`（scoring.ts:49），RoutingStrategy 又新增 `'decision'`（36，#1354），preset 与 strategy 已不是同一个类型域。
- SEMANTIC: 351 「`tools.ts` 21 个 `generate(ctx): Generation`」——cli/src/tools.ts 现有 20 个 `(ctx: GenerateContext): Generation` 生成器、metadata 表 20 行（tools.ts:1060 `export const tools = metadata.map(...)`）；「21」在写文档时也已偏 1。另：生成器不再逐个实现 `generate`，而是由 metadata 元组第 10 项注入。
- SEMANTIC: 351 双认证表述未复核到具体常量（不在本次锚点范围内），未作行号改动。
