# 02 + 07 正文语义校正报告（第二轮 prose 轮）

HEAD = 当前 adrian 工作树。只改 `docs/adrian/sourceReader/02-简单例子-全路径走读.md` 与
`07-状态存储与并发.md` 两个文件；未动源码、未 commit/push。每条证据均在本轮亲自 grep/Read 复核。
行号按**编辑后**磁盘文件回读。文末「落盘校验」为编辑后 `grep -n` 的真实输出摘要。

推翻上游报告的条目集中在最后一节「报告/事实表纠错」。

---

## 02-简单例子-全路径走读.md

A  L101   §3 标题 `router.ts:pickModel() + streamChatCompletion()` -> `router.ts:routeRequest()` + `lib/fallback-loop.ts:runFallbackLoop()` (证据: routeRequest=services/router.ts:2152、runFallbackLoop=lib/fallback-loop.ts:1348、router.ts 内 grep `function*`/AsyncGenerator 零命中)
A  L103-116 §3.1 伪码 `async routeRequest(req,opts): Promise<ResolvedChain>` -> 真实同步签名 `routeRequest(estimatedTokens=1000, skipKeys?, preferredModelDbId?, requireVision=false, requireTools=false, skipModels?, prefetchedChain?, requireStructured=false, skipPlatforms?, exactOutputReserve=0, task?): RouteResult` (证据: router.ts:2152 逐参数核对；链取 `prefetchedChain ?? getActiveChain(db)`=2158，getActiveChain=1328)
A  L118-121 resolveRoutingChain 语义修正：真实签名 `resolveRoutingChain(modelString: string|undefined): ResolvedChain`，由 proxy 调用（routes/proxy.ts:1282/2158），入参是模型字符串不是 (db,req,opts)；「custom_endpoint 表」不存在 (证据: router.ts:1437；链 SQL = profile_models/fallback_config JOIN models（router.ts:1336-1359）；`grep -n "CREATE TABLE" server/src/db/migrations/20260101_000000_legacy_baseline.ts` 全量 17 表中无 custom_endpoint 类表；`20260930_000001` 迁移名 custom_endpoint_group_label 只是给 api_keys 加列)
B  L118-123 「过滤：status !== 'error'」-> 真实 key 过滤 `enabled = 1 AND status IN ('healthy','unknown')` (证据: router.ts:1593)
A/C L126-145 §3.2 `checkAndReserve()` 整块 -> `selectKeyForModel()`（router.ts:1582）内真实闸门序列（源码顺序 router.ts:1660-1677）：isOnCooldown(=1255) → canUseProvider(=665) → canUseProviderMinute(=689) → canUseKeyConcurrency(=120) → canMakeRequest(=312) → canUseTokens(=334) → canUseProviderTokens(=783) → checkMonthlyBudget(services/key-budget.ts:92) → acquireLease(=127) (证据: 逐行读 router.ts:1657-1701；`note('rpm/rpd-limit')` 等类别与源码字符串一致)
A  L142   原「provider_quota_state 表」预检项 -> 删；provider 级闸门读的是 env cap + 当日计数，`provider_quota_state` 是配额观测不是预检门 (证据: ratelimit.ts:665-672 `getProviderDailyRequestCap`，canUseProvider 不读 provider_quota_state)
B  L147-151 「关键常量」小节按源码重写：`RPM/TPM/RPD/TPD_WINDOW_MS`、`COOLDOWN_BASE_MS`、`COOLDOWN_MAX_MS`、`KEY_CONCURRENCY_LIMIT=3` 均不存在 -> MINUTE=32/DAY=33；冷却阶梯 COOLDOWN_DURATIONS=[2min,10min,1h,24h]=879；封顶 settings 键 `routing_cooldown_ceiling_ms`(COOLDOWN_CEILING_KEY=896, 边界 897-898)；402=`PAYMENT_REQUIRED_COOLDOWN_MS=DAY`(963)；并发上限 opt-in：`getKeyConcurrencyLimit`(98) 未设 env 返回 null，`canUseKeyConcurrency` 对 null 直接放行 (证据: ratelimit.ts:32-33/879-884/896-898/963/98-101/120-124 逐行)
C  L153-177 §3.3：判断结论 = **保留「概念示意」标注，但重写为真实调用序列**（真实流程跨 fallback-loop 与 proxy 两文件的 hooks 注入，逐行贴源码会超出走读小节体量）。新序列：runFallbackLoop(1348)→runFallbackLoopAttempts(1367)→hooks.route→routeRequest(router.ts:2152)→hooks.dispatch→`route.provider.streamChatCompletion(...)`(routes/proxy.ts:2453/2459)→成功 `recordUpstreamSuccess`(proxy.ts:2764, fallback-loop.ts:663 内部 recordRequest=821/recordTokens=833 + router.recordSuccess=310)→失败 `recordRetryableFailure`(=440)/`recordAuthFailure`(=651)+`getCooldownDecisionForLimit`(=1112)→finally `route.release?.()`(=1652)。`recordResult`/`recordFailure` 不再出现 (证据: 上述行逐条 grep)
C  L181-207 §4.1 google 片段重写：不依赖 `@google/generative-ai`（google.ts 无该 import），真实为 `toGeminiContents`(=406，内部 `userContentToParts`=382) + `contentsForModel` + `${API_BASE}/models/{id}:streamGenerateContent?alt=sse`(API_BASE=20) + `fetchWithTimeout`(x-goog-api-key 头) + 手动 SSE 行解析后 yield OpenAI 形制帧、`[DONE]` 时补 finish_reason 帧 (证据: google.ts:647-700/733-745)
A  L209-227 §4.2：`StreamChunk`->`ChatCompletionChunk`(shared/types.ts:559)、`ChatResponse`->`ChatCompletionResponse`(=546)、`TokenUsage`(=531)；`Provider` abstract->`BaseProvider`(providers/base.ts:229，抽象成员 230/231/238/246/254) (证据: grep 行号逐一命中)
B  L227   「所有 33 个 provider」-> 四口径实测并写明命令：73 个 `register()`（`grep -cE '^\s*register\(' server/src/providers/index.ts` → 73）、其中 34 个 `new OpenAICompatProvider`（→ 34）、providers 目录 44 个 .ts（`ls | wc -l` → 44）、43 个 `class *Provider`（sort -u → 43）(证据: 本轮复跑，四命令输出与统一事实表一致)
A  L233-244 §5.1：`ratelimit.recordResult(...)` 不存在 -> `recordUpstreamSuccess`(fallback-loop.ts:663) 展开为 `recordRequest`(821)+`recordTokens`(833)+`recordSuccess`(router.ts:310)；`release` 闭包 = releaseLease(ratelimit.ts:142)+月度预算回冲(router.ts:1716) (证据: fallback-loop.ts:673-675/1652，router.ts:1716)
A  L246-257 §5.2：`router.streamChatCompletion(...)` 不存在 -> SSE 帧由 routes/proxy.ts:2453/2459 派发闭包写出，`[DONE]`=2755；补充「帧 model 一律改写为 route.modelId」(证据: proxy.ts:2468 `const anyChunk = { ...chunk, model: route.modelId }`)
C  L262-291 §6 ASCII 图重写为真实链路：runFallbackLoop 外层、routeRequest/selectKeyForModel 闸门链、dispatch 闭包、recordUpstreamSuccess/recordRetryableFailure、finally release；删除 checkAndReserve/normalizeChunk/StreamChunk/recordResult/recordFailure 全部旧符号 (证据: 同上各行)
B  L275   图内「60s 墙钟」类断言 -> 默认 45s（`DEFAULT_FALLBACK_TIME_BUDGET_MS = 45_000`=fallback-loop.ts:172，可被 settings `fallback_time_budget_ms`(=181)/env 覆盖，getFallbackTimeBudgetMs=183）(证据: 复跑 grep)
B  L44-47 §1.1 中间件树：`compression()` 从 helmet 之后第二位移到链尾并注真因（app.ts:345-351 注释：挂在所有 API/proxy 路由与 error handler 之后，只包静态/SPA，防 SSE 缓冲）(证据: app.ts:351 `app.use(compression())`；helmet=130、cors=182、json=202、clientContext=206、proxyRateLimiter=217/296/302/316/324 相对顺序不变)
B  L81  §2.1 注释「调用 router.ts 的流式管线」-> 「进入 runFallbackLoop 重试循环，route/dispatch hooks 由本处理器提供」（调用点 proxy.ts:1366/2300）(证据: grep `runFallbackLoop(` routes/proxy.ts → 1366、2300)
A  L317 §7.1 `release: [Function: releaseLease]` -> 闭包 = releaseLease + 月度预算回冲（router.ts:1716）
A  L356/357 源码索引：`system-prompt.ts | resolveAuth(), extractApiToken()` 一行两文件错配拆开——resolveAuth 留在 system-prompt.ts(56-70)，`extractApiToken()`(=routes/proxy.ts:81) 并入 proxy 行 (证据: grep -n "export function extractApiToken" routes/proxy.ts → 81；system-prompt.ts 全文无该符号)
A  L359 ratelimit 行：checkAndReserve/recordResult/recordFailure -> `getKeyConcurrencyLimit/acquireLease/canMakeRequest/canUseTokens/recordRequest/recordTokens/getCooldownDecisionForLimit`，区间 98-1112
A  L361 base 行：`Provider` abstract/StreamChunk/ChatResponse -> `BaseProvider` 抽象类（230/231/238/246/254）；新增一行 `shared/types.ts | TokenUsage, ChatCompletionResponse, ChatCompletionChunk | 531 / 546 / 559`
A  L363 google 行：convertMessages -> `toGeminiContents()`/`userContentToParts()`，区间 382-836
A  L364 index 行：listProviders -> `getAllProviders()`(=650)/`hasProvider()`(=654)（getProvider=626 保留）
A  L366 fallback-loop 行：补 `recordUpstreamSuccess`(663)/`recordRetryableFailure`(440)，区间 243-1652
A  L371 model-state 行：`getChainCandidates()` 不存在（全仓 hits=0）-> 该文件真实职责 catalog override/tombstone（导出 114-353），候选链读取在 router.ts `getActiveChain()`=1328
A  L379-380 §9：`checkAndReserve 返回 {ok:false}` -> selectKeyForModel 闸门 note 类别；`recordFailure` -> `recordRetryableFailure`(440)+`recordRateLimitHit`(303)/`recordModelFailure`(285)；「60s 墙钟」-> 45s（DEFAULT_FALLBACK_TIME_BUDGET_MS=172）
SKIP L55/L65/L88 等第一轮已 FIX/OK 行 正文断言复跑无变化（resolveAuth/requireInferenceAuth/AUTO_MODEL_ID 等逐条 grep 命中），不再改动
SKIP 全文测试数字 02 未出现测试计数，无需按「文件数+命令」口径改写

## 07-状态存储与并发.md

A  L12  mermaid `libSqliteFactory` -> `betterSqliteFactory`(db/index.ts:32)；并注 `defaultDbFactory`(45-47) 在 platform==='android' 时切 `nodeSqliteFactory`(db/node-sqlite.ts:66)
B  L28  「一次建齐 12 张表；后续 38 个迁移」-> 13 张表（models/api_keys/requests/rate_limit_usage/rate_limit_cooldowns/fallback_config/profiles/profile_models/settings/users/sessions/provider_quota_state/provider_quota_observations，createTables=58-232 内 13 个 CREATE TABLE 逐行数）；迁移目录 44 个 .ts（含基线，即 43 个增量），命令 `ls server/src/db/migrations/*.ts | wc -l` → 44 一并写进正文
C  L109 dev/prod 分叉**写反**修正：读 db/index.ts:197-223 确认 `initDb` 仅在 `process.env.NODE_ENV !== 'development'`(203) 时 `runMigrationsSync(db,'up')`(204)；development 分支只探测 `migrations` 表，缺表 console.error 提示 `npm run db:migration:up` 后 `process.exit(1)`(206-218)。正文改为「prod 自动补齐迁移；dev 不跑迁移、只校验并带提示退出」
C  L151 「provisional 用量 = 占位行先写 kind、成功后转实账」错误 -> 真实为纯内存租约求加和：`provisionalRequests`(=163)/`provisionalTokens`(=172)/`provisionalProviderRequests`(=183)/`provisionalProviderTokens`(=187) 遍历 `leases` Map（段头注释 =151~161「live in memory only」语义即此），叠加进 canMakeRequest/canUseTokens 计数闭合 check-then-act；`rate_limit_usage.kind('request'|'tokens')` 是 recordRequest(821)/recordTokens(833) 写的实账
A  L158 `RESERVED_TABLES` 不存在 -> dump 内部表排除是 `isInternalTable`(services/backups.ts:67-69，migrations/backups/sqlite_*)，「backups 表自己就是备份索引」的注释在其上方(64-66)；另 `EXCLUDED_TABLES`(=62，users/sessions/url_tokens)与理由注释 55-61（含 settings 刻意不排除）分句写清，两常量用途不同
B  L159 安全阀覆盖面修正：盯 users/sessions/url_tokens（表清单经 `isExcludedTable`=71 + SQL 文本 `EXCLUDED_STATEMENT_RE`=401 兜底，判定 451-457、文案 454）；`api_keys` **不在**排除名单、照常 dump/restore，前置拦截是 key 指纹门(438-449，不一致 409)
A  L160 `dbBackupPump` -> `startDbBackupPump`=lib/db-backup.ts:263（不在 services/backups.ts），`FREEAPI_DB_BACKUP_TARGET`=lib/db-backup.ts:24；两 job 在 server/src/index.ts onReady 启动(=87/88)
B  L184 索引行「12 表」-> 13 表
B  L185 索引行「38 个增量迁移（20260627_000001 … 20260930_000001）」-> 44 个 .ts = 基线 + 43 个增量，首 `20260627_000001_custom_provider_modalities.ts`、最新 `20261017_233153_request_failure_attribution.ts`（`ls` 实测，附命令）
A  L187 索引行 ratelimit 段：旧「头段 windows/leases」-> `windows`=14/`leases`=69、`LEASE_MAX_AGE_MS`=76、provisional 段=151~194、`recordRequest`=821/`recordTokens`=833、prune 节流注释=195-202（`USAGE_PRUNE_INTERVAL_MS`=202）
A  L188 索引行 backups 段：`RESERVED_TABLES` -> `EXCLUDED_TABLES`=62/`isInternalTable`=64-69/`EXCLUDED_STATEMENT_RE`=401/指纹门 438-449/安全阀 451-457
A  L189 新增索引行 `server/src/lib/db-backup.ts` — 24/263（startDbBackupPump 的真实所在文件，原来错挂在 services/backups.ts）
A  L190 索引行 index.ts 段：`dbBackupPump`/`backupScheduler` -> `startDbBackupPump`(87)/`startBackupScheduler`(88)
SKIP §5 表格 L143-148 与 §4 加密段 逐条复跑无误（windows=14/leases=69/LEASE_MAX_AGE_MS=76=2*MINUTE、crypto.ts 各锚点第一轮已 OK），不改
SKIP 测试数字 07 未出现测试计数；若后续要写，按「server 347 个 .test.ts 文件（`find server/src -name '*.test.ts' | wc -l` → 347）」口径

## 报告/事实表纠错（本轮亲自复跑后推翻）

1. RULES2 统一事实表「provider 侧真实类型 …（约 531/546/559）」按列表顺序会读成 Response=531/Chunk=546/TokenUsage=559；**实测** shared/types.ts：`TokenUsage`=531、`ChatCompletionResponse`=546、`ChatCompletionChunk`=559（顺序不同）。文档已按实测写。
2. report-02-07 SEMANTIC-3（及任务简报）把 `getCooldownDecisionForLimit`(1112) 列为预检入口之一；实读 router.ts:1660-1677：**预检不含它**，预检的冷却门是 `isOnCooldown`(=1255)；`getCooldownDecisionForLimit` 只在失败记账侧被 fallback-loop.ts:330 调用。正文按真实归属写。
3. report SEMANTIC-4 的闸门清单漏了 `checkMonthlyBudget`(key-budget.ts:92, router.ts:1677) 这一道真实门，正文已补。
4. report SEMANTIC-8 「除 base/index 外 41 个 provider 文件」口径含糊：目录共 44 个 .ts，去 base/index 是 42，去 openai-compat 才是 41；正文改用统一事实表的四口径命令，不再写单一「文件数」。
5. report SEMANTIC-5 建议「标题里的 router.ts 我没有动」；本轮判断：§3.3 **保留概念示意**（真实序列跨 fallback-loop+proxy 两文件，逐行贴码不现实），但示意内容与源码阶段一一对应（route/dispatch/recordUpstreamSuccess/recordRetryableFailure/release@finally），行号全部为磁盘实测。
6. 任务简报「§3.2 标题与 mermaid」：02 全文没有涉及 §3.2 的 mermaid，只有伪码块；已按伪码处理。
7. 简报称 extractApiToken 在 routes/proxy.ts —— 实测 =routes/proxy.ts:81，正确，已按真实文件拆行。

## 落盘校验（编辑后磁盘回读）

02：L46 `compression() ... app.ts:351`；L81 `进入 runFallbackLoop 重试循环`；L101 标题 `routeRequest()+runFallbackLoop()`；L126 `### 3.2 限流预检：ratelimit.ts 的闸门串联`；L153 `### 3.3 ... runFallbackLoop()`；L209/L233/L246 §4.2/§5.1/§5.2 新标题；L275 图内 `≤20 次 / 默认 45s 墙钟`；L356 `| server/src/lib/system-prompt.ts | resolveAuth() | 56-70 |`；L357 proxy 行含 `extractApiToken()`；L360 ratelimit 行 98-1112；L371 model-state 行 override/tombstone。
07：L12 `betterSqliteFactory`；L28 `13 张表 ... wc -l → 44`；L109 `NODE_ENV !== 'development'（+6，=203）`；L151 `纯内存、不落行`；L158-160 `isInternalTable/EXCLUDED_TABLES/startDbBackupPump`；L184/L185/L187-190 索引行全部为新断言。
RULES2 第 7 条自检 grep（两文件合并跑）→ 无输出（exit=1）；扩展清单（recordFailure/libSqliteFactory/getChainCandidates/normalizeChunk）同样为空。
