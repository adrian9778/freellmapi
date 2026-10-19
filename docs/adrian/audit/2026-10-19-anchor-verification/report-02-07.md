# 02-简单例子-全路径走读.md + 07-状态存储与并发.md 锚点校正报告

HEAD = 778074b6 (branch adrian)。所有新行号都用 `grep -n` / `sed -n '<N>p'` 在磁盘源码上复核过；
每处编辑后立即回读文档行（见文末「落盘校验」）。未改动任何源码文件，未 commit / push。

---

## 02-简单例子-全路径走读.md

FIXED  L36   app.ts:115-140 -> app.ts:99-382        (证据: createApp=app.ts:99, 收尾 `}`=app.ts:382)
FIXED  L52   proxy.ts:66-73 -> routes/proxy.ts:69-76 (证据: function requireInferenceAuth=routes/proxy.ts:69, `}`=76；片段正文与源码逐行一致)
FIXED  L63   proxy.ts:78-89 -> routes/proxy.ts:78-92 (证据: 块首注释=78, extractApiToken=81, `}`=92)
FIXED  L65   db/index.ts:233 -> db/index.ts:231      (证据: export function regenerateUnifiedKey=231；`freellmapi-`+randomBytes(24)=48 hex 在 233)
FIXED  L71   proxy.ts 约 500 行起 -> routes/proxy.ts 约 1643 行起 (证据: proxyRouter.post('/chat/completions')=routes/proxy.ts:1643)
FIXED  L78   proxy.ts:102-107 -> routes/proxy.ts:105-110 (证据: export function getRequestGroupId=105, `}`=110)
FIXED  L88   proxy.ts:50-54 -> routes/proxy.ts:47-57 (证据: AUTO_MODEL_ID 块首注释=47, const=51, isAutoModel=53, `}`=57)
FIXED  L101  router.ts 约 500 行 -> router.ts 约 2152 行 (证据: export function routeRequest=services/router.ts:2152)
FIXED  L104  router.ts:600+ -> router.ts:2152+       (证据: routeRequest=2152；正文见 SEMANTIC-1)
FIXED  L116  router.ts:650+ -> router.ts:1437-1480   (证据: resolveRoutingChain=services/router.ts:1437, `}`=1480)
FIXED  L122  ratelimit.ts 约 200 行 -> services/ratelimit.ts 约 312 行 (证据: 限流预检实体现=canMakeRequest=services/ratelimit.ts:312)
FIXED  L125  ratelimit.ts:200+ -> services/ratelimit.ts:312+ (同上；正文见 SEMANTIC-3)
FIXED  L143  ratelimit.ts:30-50 -> services/ratelimit.ts:32-33 (证据: const MINUTE=32, const DAY=33 是现存的窗口常量)
FIXED  L152  router.ts:800+ -> lib/fallback-loop.ts:1348+ (证据: export async function runFallbackLoop=lib/fallback-loop.ts:1348；正文见 SEMANTIC-5)
FIXED  L179  google.ts 约 36000 行 -> 约 899 行       (证据: server/src/providers/google.ts 全文 899 行；streamChatCompletion=647-836≈190 行，「核心约 200 行」仍成立)
FIXED  L239  proxy.ts: 约 900 行 -> routes/proxy.ts: 约 2453 行 (证据: chat 处理器内 `const gen = route.provider.streamChatCompletion(`=2453, for await=2459, `data: [DONE]`=2482)
FIXED  L284  router.ts:186-237 -> router.ts:188-239  (证据: export interface RouteResult=188, `}`=239；实例字段与接口逐一对上)
FIXED  L305  router.ts:151-184 -> router.ts:153-186  (证据: export interface ChainRow=153, `}`=186；字段逐一对上，含 match_tier=185)
FIXED  L337  app.ts createApp() 97-400+ -> 99-382
FIXED  L338  middleware/rateLimit.ts createProxyRateLimiter() 1-80 -> 34-78 (证据: =34, `}`=78)
FIXED  L339  lib/client-context.ts clientContextMiddleware() 1-60 -> 39-50 (证据: =39, `}`=50)
FIXED  L340  lib/system-prompt.ts resolveAuth() 1-120 -> 56-70 (证据: resolveAuth=lib/system-prompt.ts:56, `}`=70；全文只有 82 行，1-120 越界。extractApiToken 不在此文件，见 SEMANTIC-9)
FIXED  L341  routes/proxy.ts 42-1200+ -> 45-1643+    (证据: proxyRouter=45, requireInferenceAuth=69, 主处理器=1643)
FIXED  L342  routes/anthropic.ts anthropicRouter 1-600+ -> 49-1194 (证据: export const anthropicRouter=routes/anthropic.ts:49, 文件尾=1194)
FIXED  L343  services/router.ts 500-1200+ -> 1437-2381 (证据: resolveRoutingChain=1437 … routeRequest 收尾=2381)
FIXED  L344  services/ratelimit.ts 200-500+ -> 127-845 (证据: acquireLease=127-138；recordTokens 收尾=845)
FIXED  L345  providers/base.ts 1-250 -> 229-525      (证据: export abstract class BaseProvider=229, 类收尾=525)
FIXED  L346  providers/google.ts 100-500 -> 647-836  (证据: async *streamChatCompletion=647, `}`=836；convertMessages 见 SEMANTIC-7)
FIXED  L347  providers/index.ts 1-360 -> 626-656     (证据: getProvider=626-628 … hasProvider 收尾=656；listProviders 见 SEMANTIC-9)
FIXED  L348  lib/crypto.ts decrypt() 50-100 -> 204-212 (证据: export function decrypt=204, `}`=212)
FIXED  L349  lib/fallback-loop.ts 1-300 -> 243-1365  (证据: newFallbackState=243-245, runFallbackLoop=1348-1365)
FIXED  L350  lib/content.ts normalizeOutboundContent() 1-150 -> 129-143 (证据: =129, `}`=143)
FIXED  L351  lib/image-normalize.ts normalizeMessageImages() 1-200 -> 282-320 (证据: export async function=282, `}`=320)
FIXED  L352  lib/tool-call-rescue.ts rescueInlineToolCalls() 1-150 -> 217-246 (证据: =217, `}`=246)
FIXED  L353  services/scoring.ts 1-300 -> 278-541    (证据: reliabilityPosterior=278-287, combineScore=534-541)

OK     L49   proxy.ts:requireInferenceAuth() +7      (offset 记法自洽：def=69，def+7=76 正是块尾)
OK     L54   lib/system-prompt.ts:resolveAuth        (确认在 lib/system-prompt.ts:56，非注释里的 proxy.ts)
OK     L42   middleware/rateLimit.ts IP 级 RPM 默认 120 (证据: middleware/rateLimit.ts:16 `const DEFAULT_RPM = 120`)
OK     L40   express.json 25MB 上限                    (证据: app.ts:198-201 用 cfg.requestBodyLimitBytes)
OK     L63   三种认证头（Bearer / x-api-key / x-goog-api-key）(证据: routes/proxy.ts:82-91)
OK     L143-147 区间落点（见 SEMANTIC-4：常量本身是错的，但 32-33 已是真实窗口常量行）
OK     L284-303 RouteResult 字段清单                   (与 services/router.ts:188-239 逐字段一致)
OK     L307-328 ChainRow 字段清单                      (与 services/router.ts:153-186 逐字段一致)
OK     L364  tool-validate.ts:invalidToolCallReasons   (=lib/tool-validate.ts:163，无数字锚点)
OK     L365  applyTokenBudget                          (=lib/guardrails.ts:89，无数字锚点)
OK     L366  summarizeExhaustion                       (=services/router.ts:84，无数字锚点)
OK     L367  isClientAbortError                        (=lib/error-classify.ts:272，无数字锚点)
OK     L363  最多 20 次                                (=lib/fallback-loop.ts:69 FALLBACK_MAX_RETRIES=20)

---

## 07-状态存储与并发.md

FIXED  L22   index.ts:82-87 -> db/index.ts:82-87     (路径消歧 + 复核：82 `journal_mode = WAL`、87 `busy_timeout = 5000`，数字本身没错)
FIXED  L28   legacy_baseline.ts:createTables+0~+160 -> +0~+174 (证据: createTables=58, `}`=232，232-58=174)
FIXED  L110  legacy_baseline.ts:1-55 -> db/migrations/20260101_000000_legacy_baseline.ts:36-43 (证据: 「V25 is the LAST model-data migration…」纪律注释=36-43；1-5 只是 import，55 是 down 的 throw)
FIXED  L182  db/node-sqlite.ts 1-40 -> 1-36          (证据: 类型/shim 头部=1-25, loadNodeSqlite=27-36)
FIXED  L184  legacy_baseline 58-198 -> 58-232        (证据: createTables=58, `}`=232)
FIXED  L188  backups.ts 24-26 -> 20-28               (证据: export interface BackupSchedule=20, `}`=28；intervalDays=25、backupPath=27)
FIXED  L188  backups.ts 64-68 -> 64-69               (证据: 理由注释=64-66, isInternalTable=67-69)

OK     L20   db/index.ts:31-38 工厂 + 报错文案         (证据: 块首注释=31, betterSqliteFactory=32, runtimeRequire('better-sqlite3')=35, 报错串=38；严格块尾是 43，此处按被引用的报错行收尾，数字无需改。文档已带 db/ 前缀)
OK     L14   db/index.ts:connectDb+0                 (connectDb=db/index.ts:49)
OK     L22   busy_timeout = 5000 / WAL 语义            (db/index.ts:82-87，注释 84-86 与正文「读不阻塞写」一致)
OK     L21   numberResult+0                          (=db/node-sqlite.ts:38-44，bigint→number 且 !Number.isSafeInteger 抛错)
OK     L102  CREATE_MIGRATIONS_TABLE_SQL+0            (=db/migrate/runner.ts:35-41)
OK     L103  runPendingMigrations / runMigrations / runMigrationsSync (runner.ts:43-62 异步、64-82 同步；runPendingMigrationsSync=153)
OK     L108  down 抛错「第 55 行」                     (=20260101_000000_legacy_baseline.ts:55 throw new Error('Legacy baseline is irreversible - restore from backup'))
OK     L183  runner.ts 35-41 追踪表；43-82 runMigrations/runMigrationsSync (逐条核实无误)
OK     L181  db/index.ts 31-38 / 82 / 87 + connectDb(49)/initDb(197)/shouldHardenDataDir(122)/restrictDataDir(153)/getSetting(239)/setSetting(245)
OK     L184  55 down；1964/2032/2074/2083 后置表段      (1964 embedding_models、2032 media_models、2074 quirks、2083 quirk_targets 全部命中)
OK     L186  crypto.ts 全部 8 段区间：7-27 / 29-37 / 45-56 / 63-84 / 94-153 / 173-176 / 182-212 / 227-231 (证据: ALGORITHM=7、KEY_BYTES=18、KEY_FILE_NAME=27、parseHexKey=29-37、isDevFallbackAllowed=45-47、missingKeyError=49-56、keyFilePathFor=63-68、writeKeyFileAtomic=75-84、initEncryptionKey=94-153、encryptionKeyFingerprint=173-176、encrypt=182-196、AUTH_TAG_BYTES=202、decrypt=204-212、maskKey=227-231 —— 全对)
OK     L131-137 §4 五条设计决策 + 全部 `+0` 符号（KEY_FILE_NAME=27 / KEY_BYTES=18 / parseHexKey=29 / AUTH_TAG_BYTES=202 / encryptionKeyFingerprint=173 / maskKey=227 / keyFilePathFor=63）：16 字节 IV=184、sha256 截 16 hex=64bit=175、<5 全遮 ≤8 露 2=228-229、tag 4–16 字节 2^32=198-201 全部与源码一致
OK     L146  LEASE_MAX_AGE_MS+0 = 2min                (=services/ratelimit.ts:76 `2 * MINUTE`)
OK     L145  模块级 `windows: Map` / L146 `leases: Map` (=services/ratelimit.ts:14 / :69)
OK     L152  idx_rate_limit_usage_lookup 五列复合索引 + prune 节流 (=20260101_000000_legacy_baseline.ts:178；ratelimit.ts:194-203 注释与 USAGE_PRUNE_INTERVAL_MS=MINUTE)
OK     L159  恢复安全阀「第 454 行附近」                (=services/backups.ts:451-457，抛错文案在 454)
OK     L160  startBackupScheduler+0                    (=services/backups.ts:524)
OK     L165  shouldHardenDataDir+0 / restrictDataDir+0 / restrictDbFilePermissions+0 (=db/index.ts:122 / 153 / 187；FREEAPI_DB_DIR_HARDENING 三态=db/index.ts:140-147)
OK     L189  index.ts 顺序 restoreDbBackupIfNeeded(43/45) -> initDb(47) -> applyDeclarativeConfigFromEnv(48)，onReady 内 startDbBackupPump(87)/startBackupScheduler(88)
OK     L92   `request_attempts` 迁移确实存在            (db/migrations/20260726_000002_request_attempts.ts)
OK     L171  `analytics_latency_percentile_index` 迁移存在 (db/migrations/20260902_000001_analytics_latency_percentile_index.ts)

---

## SEMANTIC（正文断言与源码不符，均未改动正文）

### 02
SEMANTIC-1 L104-113 routeRequest 片段：真实签名是同步的
  `export function routeRequest(estimatedTokens = 1000, skipKeys?, preferredModelDbId?, requireVision = false, requireTools = false, skipModels?, prefetchedChain?, requireStructured = false, skipPlatforms?, exactOutputReserve = 0, task?): RouteResult`
  (services/router.ts:2152-2381)，不是 `async ... (req: ChatRequest, opts: RouteOptions): Promise<ResolvedChain>`；
  链取自 `getActiveChain(db)`（services/router.ts:2158，定义 1328），不是 `await resolveRoutingChain(db, req, opts)`。
SEMANTIC-2 L116-120 resolveRoutingChain 真实签名 `resolveRoutingChain(modelString: string | undefined): ResolvedChain`
  (=1437)，入参是模型字符串而非 (db, req, opts)。
SEMANTIC-3 L122-140 `checkAndReserve()` 全仓不存在。现役预检拆成：canMakeRequest(312 RPM/RPD)、canUseTokens(334 TPM/TPD)、
  canUseKeyConcurrency(120)+acquireLease(127)、canUseProvider(665)/canUseProviderMinute(689)/canUseProviderTokens(783)、
  getCooldownDecisionForLimit(1112)；返回 boolean/结构体，不存在 `{ok, reason?, retryAfterMs?}` 单一入口。
SEMANTIC-4 L143-147 常量名全部不存在：RPM_WINDOW_MS / RPD_WINDOW_MS / TPM_WINDOW_MS / TPD_WINDOW_MS /
  COOLDOWN_BASE_MS / COOLDOWN_MAX_MS / KEY_CONCURRENCY_LIMIT。真实：MINUTE(32)/DAY(33)；冷却时长 COOLDOWN_DURATIONS(879)、
  上限走 settings 键 COOLDOWN_CEILING_KEY(896)/MIN_COOLDOWN_CEILING_MS(897)/MAX_COOLDOWN_CEILING_MS(898)；
  并发上限是 opt-in 的 `getKeyConcurrencyLimit(platform)`(98)，默认 null（无上限），「每 key 3」这一数字源码里没有。
SEMANTIC-5 L149-172 §3.3：services/router.ts 内没有任何 generator（grep `function*`/AsyncGenerator 零命中），
  「streamChatCompletion() (router.ts 约 800 行)」这一函数不存在。选中路由后的流式尝试循环是
  lib/fallback-loop.ts:1348 runFallbackLoop（1367 runFallbackLoopAttempts），provider 生成器在 /chat/completions
  的派发闭包里被消费（routes/proxy.ts:2453/2459）。标题里的 `router.ts` 我没有动（改文件名等于改归属断言）。
SEMANTIC-6 L152-172 片段正文（`recordResult()` / `recordSuccess()` / `release()` 的 try/catch 形状）与实际不符：
  记账是 recordRequest(821)/recordTokens(833)，惩罚是 router 侧 recordModelFailure(285)/recordRateLimitHit(303)/recordSuccess(310)。
SEMANTIC-7 L179-201 §4.1 片段：google.ts 不再用 `new GoogleGenerativeAI()`（文件里无 @google/generative-ai import，
  走 API_BASE=https://generativelanguage.googleapis.com/v1beta + proxyFetch），且 `convertMessages()` 全仓不存在，
  真实换格式的是 toGeminiContents(406)/userContentToParts(382)；「normalizeChunk」也非现存符号。
SEMANTIC-8 L206-219 §4.2：`StreamChunk`、`ChatResponse` 两个接口全仓不存在（流式帧类型是 @freellmapi/shared/types 的
  ChatCompletionChunk），providers/base.ts 里是 `export abstract class BaseProvider`(229)，不是 `Provider` abstract；
  「所有 33 个 provider」也与现状不符（server/src/providers 下除 base/index 外 41 个 provider 文件）。
SEMANTIC-9 L227-234 §5.1：`ratelimit.recordResult()` / `recordFailure()` 在 services/ratelimit.ts 不存在（见 SEMANTIC-6）。
  L236-245 §5.2：`router.streamChatCompletion(...)` 不存在，SSE 帧由 routes/proxy.ts:2453-2482 的派发闭包写出。
SEMANTIC-10 L340 行：`server/src/lib/system-prompt.ts | resolveAuth(), extractApiToken()` —— extractApiToken 实际在
  routes/proxy.ts:81（system-prompt.ts 只有 resolveAuth=56）。L347 行：`listProviders()` 不存在，
  真实是 getAllProviders(650)/hasProvider(654)。L354 行：`services/model-state.ts | getChainCandidates()`
  该符号不存在（model-state.ts 是 catalog/override/tombstone 的集合），候选链来自 router.ts:1328 getActiveChain。
  这三行我只改了行号，符号名保留，等主线决定。
SEMANTIC-11 L363 「60s 墙钟预算」：真实默认 DEFAULT_FALLBACK_TIME_BUDGET_MS = 45_000
  (lib/fallback-loop.ts:172)，可被 settings 的 fallback_time_budget_ms(181)/env 覆盖。
SEMANTIC-12 L36-47 中间件顺序图把 `compression()` 列在 helmet 之后第二位：现状是 app.ts:351 才挂载，
  位置在所有 API/proxy 路由与 error handler 之后，且只包裹静态/SPA 回落响应（注释 345-350 明确说是为了
  不让 SSE 被缓冲）。helmet(130)→cors(182)→json(198/202)→clientContext(206)→proxyRateLimiter(215/296/302/316/324)
  →路由挂载(287-325) 的相对顺序与文档一致，仅 compression 这一行错位。

### 07
SEMANTIC-13 L12 mermaid `libSqliteFactory`：真实工厂名是 `betterSqliteFactory`（db/index.ts:32），
  并由 `defaultDbFactory(platform)`(45-47) 在 android 时切到 nodeSqliteFactory。
SEMANTIC-14 L28 与 L184 「一次建齐 12 张表」：createTables(58-232) 实际建 13 张 —— models(60)、api_keys(79)、
  requests(92)、rate_limit_usage(105)、rate_limit_cooldowns(116)、fallback_config(125)、profiles(133)、
  profile_models(146)、settings(155)、users(161)、sessions(168)、provider_quota_state(182)、
  provider_quota_observations(201)。
SEMANTIC-15 L28 与 L185 「后续 38 个迁移」/「38 个增量迁移（20260627_000001 … 20260930_000001）」：
  db/migrations 现有 44 个 .ts，即基线 + 43 个增量；首个增量仍是 20260627_000001_custom_provider_modalities.ts，
  最新是 20261017_233153_request_failure_attribution.ts。计数与末位文件名一起过期，故我没动这一行。
SEMANTIC-16 L109 「dev 与 prod 行为不同：开发环境允许新建迁移文件后直接生效，生产环境要求迁移已编入 bundle」——
  与 initDb(db/index.ts:197-223) 恰好相反：`process.env.NODE_ENV !== 'development'`(203) 时才 runMigrationsSync(204)；
  development 分支只探测 `migrations` 表，缺表即 console.error + `npm run db:migration:up` 提示后 process.exit(1)(206-218)。
SEMANTIC-17 L151 「provisional usage：预留行先以 `kind` 占位写入，成功后转实账」：真实实现是纯内存 ——
  provisionalRequests(163)/provisionalTokens(172)/provisionalProvider*(183/187) 直接累加 `leases` Map，
  注释 150-161 说明租约「live in memory only」，闭合的正是 check-then-act 竞态；`rate_limit_usage` 里的
  kind('request'|'tokens') 是实账，不是占位。
SEMANTIC-18 L158 与 L188 `RESERVED_TABLES` 这个常量不存在。真实是 `isInternalTable`(services/backups.ts:67-69，
  排除 migrations/backups/sqlite_*)，另有一个不同用途的 `EXCLUDED_TABLES`(62 = users/sessions/url_tokens)。
  文档「dump 时排除 migrations/backups/sqlite_*」这一断言本身正确。
SEMANTIC-19 L159 「dump 若声称要写回账号/会话表（users/sessions/api_keys 之外还盯 sessions）」：安全阀盯的是
  users/sessions/url_tokens（EXCLUDED_TABLES=62 + EXCLUDED_STATEMENT_RE 兜底，判定在 451-457）；
  api_keys 并不在排除名单，它会被 dump/restore，只是 restore 前用 key 指纹拦截（438-449）。
SEMANTIC-20 L160 `dbBackupPump` 名字与位置：真实是 `startDbBackupPump`，定义在 server/src/lib/db-backup.ts:263
  （不在 services/backups.ts），在 server/src/index.ts:87 的 onReady 里启动；`FREEAPI_DB_BACKUP_TARGET` 也确实被
  lib/db-backup.ts 使用。
SEMANTIC-21 L110 「头部注释」：V25 纪律注释实际在 up() 函数体内(36-43)，文件 1-5 行是 import。
  我只把区间改成 36-43，「头部」这个措辞保留（区间仍在文件靠前处）。

---

## 落盘校验

两份文档逐条 `grep -n` 回读结果（编辑后磁盘上的真实内容）：

02：L36 `app.ts:99-382`；L52 `// routes/proxy.ts:69-76`；L63 `routes/proxy.ts:78-92`；L65 `db/index.ts:231`；
L71 `约 1643 行起`；L78 `routes/proxy.ts:105-110`；L88 `routes/proxy.ts:47-57`；L104 `router.ts:2152+`；
L116 `router.ts:1437-1480`；L125 `services/ratelimit.ts:312+`；L143 `services/ratelimit.ts:32-33`；
L152 `lib/fallback-loop.ts:1348+`；L179 `约 899 行`；L239 `routes/proxy.ts: 约 2453 行`；L284 `router.ts:188-239`；
L305 `router.ts:153-186`；L337-354 表格 18 行全部为新数字（L354 model-state 行按 SEMANTIC-10 保留原样）。

07：L22 `db/index.ts:82-87`；L28 `createTables+0~+174`；L110 `db/migrations/20260101_000000_legacy_baseline.ts:36-43`；
L182 `1-36`；L184 `58-232`；L188 `20-28 / 64-69`。

另：02 L149 标题 `(router.ts 约 800 行)` 与 07 L185 `38 个增量迁移`、L28/L184 `12 张表`、L158/L188 `RESERVED_TABLES`、
L160 `dbBackupPump` 均按「只改行号/路径前缀」的约束原样保留，交由主线处理。
