# 锚点校正报告 · 10 / 11 / 12（函数级走读三篇）

所有修改仅为行号数字与文件路径前缀消歧；正文语义未动。每处均已 grep 当前源码确认，并回读文档确认落盘。

## 第 10 篇（10-函数级走读-路由限流与回退.md）

FIXED  10:55  router.ts:1144 -> router.ts:1204  (证据: orderChain=1204, 1204-1272)
FIXED  10:72  router.ts:1031 -> router.ts:1091  (证据: scoreChainEntry=1091, 1091-1158)
FIXED  10:93  router.ts:1522 -> router.ts:1582  (证据: selectKeyForModel=1582, 1582-1726)
FIXED  10:136 ratelimit.ts:1109 -> ratelimit.ts:1112  (证据: getCooldownDecisionForLimit=1112, 1112-1168)
FIXED  10:157 fallback-loop.ts:1336/1355 -> fallback-loop.ts:1348/1367  (证据: runFallbackLoop=1348, 1348-1365; runFallbackLoopAttempts=1367, 1367-1660)
FIXED  10:189 fallback-loop.ts:438 -> fallback-loop.ts:440  (证据: recordRetryableFailure=440, 440-617)
FIXED  10:227 router.ts:1436-1512 -> router.ts:1496-1555  (证据: orderKeysByScore=1496-1513, orderKeysByRemainingQuota=1548-1555；原 1436 落在 resolveRoutingChain=1437 头上，确系错锚)
FIXED  10:234 router.ts 索引行整行重打：1091-1158 scoreChainEntry；1167-1189 applyReliabilityFloor；1204-1272 orderChain；1273-1480 链缓存与 resolveRoutingChain(=1437-1480)；1486-1555 key 排序与配额；1573-1580 cachedDecrypt(=1574-1580)；1582-1726 selectKeyForModel；1743-1785 hasOtherUsableKey；1866-1886 fitsContextWindow*(strict=1866-1869, fitsContextWindow=1878-1886)；2152-2381 routeRequest；2403+ getRoutingScores(=2403)
FIXED  10:235 ratelimit.ts 索引行：18-45→18-40（getWindow 18-25、pruneTimestamps 27-30、msSinceUtcMidnight 38-40）；358-590→358-549（#899 段以 modelWindowUsedFraction 族结尾 549，551 起是 #162 provider caps）；900-1098→900-1102（getCooldownDurationForLimit 1093-1102 收尾）；1109-1165→1112-1168；1167-1250→1170-1239（persistedCooldownExpiry 1170 → cleanupExpiredCooldowns 止于 1239）；1238-1287→1241-1276（setCooldown 1241-1253、isOnCooldown 1255-1276）；1481-1530→1510-1520（learnLimitFromError=1510-1520）
FIXED  10:236 fallback-loop.ts 索引行：93-155→95-157（noteModelFailure 95-117、benchKeyAcrossPlatform 133-157）；181-195→183-197；208-241→210-245（FallbackState=210、newFallbackState 243-245）；299-353→301-341（cooldownForError 301-303、cooldownDecisionForError 315-341）；395-437→397-409（consumeSkipBenchExemption 397-409）；438-620→440-617；639-706→651-689（recordAuthFailure 651-655、recordUpstreamSuccess 663-689）；1336-1353→1348-1365；1355-1700+→1367-1660（文件全长 1660，原「1700+」不可能成立）

OK  10:116 ratelimit.ts:312/334  (canMakeRequest=312, canUseTokens=334, 312-332/334-356)
OK  10:128 ratelimit.ts:286/299  (requestCount=286, tokenCount=299 —— 已核实无误；注意 RULES/机器提示给的 "requestCount=274" 本身是错的，274 是 memoryRequestCount)
OK  10:210 ratelimit.ts:18/27  (getWindow=18, pruneTimestamps=27)
OK  10:235 未改动子区间 163-193 / 195-230 / 232-310 / 312-356 全部复核仍准确（provisionalProviderTokens 止 193、Retention-sweep 注释起 195、recordUsage 止 230、tokenCount 止 310、canUseTokens 止 356）
OK  10:234 中 1031→1091 等符号行另见 FIXED

## 第 11 篇（11-函数级走读-Provider与流式.md）

FIXED  11:9   base.ts:~300 -> base.ts:326  (证据: fetchWithTimeout=326, 326-375)
FIXED  11:34  base.ts:~352/~395 -> base.ts:392/422  (证据: readWithStallTimeout=392, firstByteBudgetMs=422)
FIXED  11:45  base.ts:~410~506 -> base.ts:458-524  (证据: readSseStream=458-463, readSseFrames=465-524)
FIXED  11:70  base.ts:~253 -> base.ts:295  (证据: validationResult=295, 295-324)
FIXED  11:81  openai-compat.ts:296 -> openai-compat.ts:322  (证据: chatCompletion 方法=322, 322-451; class OpenAICompatProvider=102)
FIXED  11:112 openai-compat.ts:425 -> openai-compat.ts:453  (证据: streamChatCompletion=453, 453-520)
FIXED  11:122 openai-compat.ts:570/587 -> openai-compat.ts:603/634  (证据: validateKey=603-620, fetchQuota=634-689)
FIXED  11:135 openai-compat.ts:654 -> openai-compat.ts:701  (证据: normalizeChoices=701, 701-732)
FIXED  11:165 base.ts 索引行整行重打：295-324 validationResult；326-375 fetchWithTimeout；380-408 readWithStallTimeout 与 #584/#553 注释（注释起 380）；422-431 firstByteBudgetMs(422-425)/firstByteTimeoutMessage(429-431)；458-524 readSseStream/readSseFrames（521-523 截断抛错：521 `if (!sawFinishReason)`、522 throw）；525 文件尾（文件现长 525 行）
FIXED  11:166 openai-compat.ts 索引行整行重打：103-120 spec 字段；122-145 timeoutMs 解析（构造函数 122-145，#547 env 覆盖在 139-140）；151-154 resolveParallelToolCalls；166-189 rescueFailedGeneration；206-212 upstreamErrorText；255-320 messagesForPlatform；322-451 chatCompletion；453-520 streamChatCompletion；532-552 guardInBandCreditsError；603-620 validateKey；630-689 hasQuotaProbe/fetchQuota；701-732 normalizeChoices
FIXED  11:167 provider-timeout.ts 1-70 -> 1-75  (文件 75 行，旋钮函数 43-73)
FIXED  11:168 providers/index.ts：42-60 -> 51-54（google 注释 51-53、register 54）；NVIDIA (145-152) -> (160-174)（注释 160-167 含 #584、register 168-174、timeoutMs:180_000=173）；CUSTOM_PROVIDER_TIMEOUT_MS (604) -> (624)

OK  RULES 给的 base.ts 参考行全部复核成立：parseRetryAfterMs=35、providerHttpError=152、readSseStream=458、readSseFrames=465

SEMANTIC: doc11:118/120 —— 「(+481~+486)」「(+470~+476)」「`guardInBandCreditsError`（+499）」里的 `+499` 实为写作时的**绝对行号**（guardInBandCreditsError 当时定义在 499），现定义在 532（517 为 yield* 调用点）。带 `+` 号无法按相对读法成立，未改动，请主线决定表述。
SEMANTIC: doc11:130 —— 「（577~581 注释）」指「quota probe fails says nothing about the key」注释，现已在 openai-compat.ts:627-628（注释块 622-629）。
SEMANTIC: doc11:131 —— 「(+600~602)」(data 包裹层/顶层都查) 现为 647-648；「(+609~+615 注释)」(SiliconFlow 数字字符串) 现为 656-658。均为旧绝对行号写作 `+` 形式。
SEMANTIC: doc11:133 —— 「hasQuotaProbe（+583）」同上，def 现为 630-632。
SEMANTIC: doc11:43 —— 「(+395 起注释)」first-byte 预算的 #584 rationale 注释现为 base.ts:409-420。
SEMANTIC: doc11:52 —— 「全部 33 个 provider 共用」：providers/index.ts 现共 73 个 `register(new …)`，其中 `new OpenAICompatProvider` 34 个（含 custom）；「33」口径（是否含非 OpenAI 线格式适配器/custom）需主线确认后定稿。

## 第 12 篇（12-函数级走读-存储配置与请求入口.md）

FIXED  12:87  proxy.ts:1493 -> routes/proxy.ts:1643  (证据: proxyRouter.post('/chat/completions')=1643；按消歧表加 routes/ 前缀防 lib/proxy.ts)
FIXED  12:89  「1493 起」->「1643 起」(同上)
FIXED  12:97  handler 内 1493~2050 -> 1643~3097  (证据: 处理器闭包 1643-3097，3097 后仅 re-export)
FIXED  12:99  （66）->（69）  (证据: requireInferenceAuth=69 in routes/proxy.ts)
FIXED  12:100 （1506~1524）->（1656~1674）  (证据: safeParse=1656, 400 响应块止 1674)
FIXED  12:101 （1528~1544）->（1681~1696）  (证据: max_completion_tokens 别名注释 1681，pickSamplingParams=1690，段止 1693/1696)
FIXED  12:102 （1546~1635）->（1695~1785）；（1552）->（1702）  (证据: 配对状态机注释起 1695、takeToolCallId=1702、messages.map 止 1785)
FIXED  12:107 （1637~1660）->（1786~1810）  (证据: cacheControlPrefixLength=1786、compressRequest=1797、prependSystemPrompt=1810)
FIXED  12:108 （1662~1718）->（1812~1869）  (证据: 降尺度注释起 1812、normalizeMessageImages=1815、估算止于预算护栏注释 1870 前)
FIXED  12:109 （1720~1733）->（1870~1883）  (证据: 「Guardrail: per-request token budget」=1870)
FIXED  12:110 （1735~1752）->（1884~1902）  (证据: 断连注释 1884-1894、clientAbort=1895、res.on('close')=1896，fusion 注释 1903 前结束)
FIXED  12:111 （1883~1950）->（2034~2101）（── Response cache=2034）；（1951）->（2102）（── Idempotency-Key=2102）；（257/270）->（260/273）（getSessionKey=260、getStickyModel=273）；（2038~2043）->（2191~2194）（"Explicit model field pins…/Sticky-session is the fallback"=2191/2194）；（2009）->（2162）（"Context handoff only applies to auto-routed"=2162）
FIXED  12:138 proxy.ts:287~312 -> routes/proxy.ts:273~313  (证据: getStickyModel 273-288、setStickyModel 290-313；原 287 是 setStickyModel 之前的残留行、287~312 起止均不中)
FIXED  12:144 db/index.ts 索引行：20-26→20-29（getDb 20-25、getDefaultDbPath 27-29）；138-151→137-147（头注释 137-138、def 140-147）；225-246→225-251（getUnifiedApiKey 225-229、regenerateUnifiedKey 231-236、getSetting 239-243、setSetting 245-251）
FIXED  12:146 declarative-config 索引行：22-131→25-136（modelEntrySchema=25 … DeclarativeConfigResult 止 136）；151-158→151-159（readConfigFromEnv 151-159）；~300-464→185-464（upsertApiKey=185 起，applyFallback 止 464）；「1460 附近」→「460 附近」（证据: `entry.priority ?? i + 1` 在 460；文件全长仅 582 行，1460 必错）
FIXED  12:147 routes/proxy.ts 索引行整行重打：53/69/105/260/273/290 辅助函数（isAutoModel 53、requireInferenceAuth 69、getRequestGroupId 105、getSessionKey 260、getStickyModel 273、setStickyModel 290，原编号统一 +3）；1643 起 POST /chat/completions：1644-1674 auth+validate；1681-1696 旋钮；1695-1785 消息归一+takeToolCallId；1786-1810 压缩+注入；1812-1869 估算与闸门；1870-1902 预算与断连；1903+ fusion；2034-2101 缓存；2162-2270 sticky/pin/handoff

OK  12:7  db/index.ts:49  (connectDb=49, 49-93 —— 机器提示怀疑越界，实测无误)
OK  12:25 db/index.ts:197  (initDb=197, 197-223；文件 251 行，无越界；NODE_ENV 分叉/initEncryptionKey 语义与源码一致)
OK  12:34 db/index.ts:122  (shouldHardenDataDir=122, 122-136 —— 机器提示把它和 server/src/index.ts 的 keepAliveTimeout 混淆了；按消歧表 db/index.ts=server/src/db/index.ts，锚点本就正确)
OK  12:50 db/migrate/runner.ts:64  (runMigrationsSync=64, 64-82; runPendingMigrationsSync=153, 153-171)
OK  12:64 declarative-config.ts:466  (applyDeclarativeConfig=466, 466-537；注意：实际路径是 **server/src/services/declarative-config.ts**，不存在 lib/declarative-config.ts —— RULES 里的 "lib/" 提示有误，文档索引行本来就写 services/，未动)
OK  12:85 （569）  (applyDeclarativeConfigFromEnv=569, 569-582)
OK  12:145 runner.ts 索引行 35-41 / 43-82  (CREATE_MIGRATIONS_TABLE_SQL 35-41、runMigrations 43-62、runMigrationsSync 64-82 —— 复核无误，未改)

SEMANTIC: doc12:89 —— 「~500 行」：/chat/completions 处理器现为 1643-3097（约 1455 行），早已远超 ~500 行；只改了「1493 起」的数字，行数描述留给主线。
SEMANTIC: doc12:32 —— 「+23」指 initEncryptionKey 挂点，实际在 initDb+24（221 行）；属相对偏移微漂，未动（相对偏移整体不在本次范围）。
SEMANTIC(通用): 三篇正文里「符号名+N」形式的相对锚（如 routeRequest+215、runFallbackLoopAttempts+158~+171、orderChain+4~+33）在函数体内部插行后可能 ±几行漂移；按任务约定只校绝对锚 `file.ts:NNN`，未逐一核对。
SEMANTIC(RULES 勘误供主线): RULES.md「requestCount=274」实为 memoryRequestCount=274，requestCount=286；「applyDeclarativeConfig=lib/declarative-config.ts:466」路径应为 services/。
