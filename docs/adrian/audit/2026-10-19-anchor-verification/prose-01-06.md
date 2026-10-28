# 01 + 06 正文语义校正报告（第二轮 prose 轮 · 中断任务收尾 + 第三方复核）

范围：只改 `docs/adrian/sourceReader/01-简单框架-系统骨架.md` 与 `06-配置与数据流.md`。未动源码、未 commit/push、未增删章节、未改章节编号。
基线：分支 adrian，HEAD = `783301fd`（`c801c802` 是其祖先，`git merge-base --is-ancestor` 通过）。
方法：前一轮的 diff（01 约 102 行、06 约 20 行改动）**逐条**回源码复验；RULES2 统一事实表的每条测量命令在本机复跑一遍；每个新写行号用 `sed -n 'Np'` 抽读；每处编辑后用 `grep -n`/`sed -n` 从磁盘回读。
前一轮自述未采信：它留下的 4 处行号偏移、2 处口径歧义、1 处前后矛盾都由本轮改掉（见「推翻前一轮」）。

---

## 一、前一轮已改内容的复核结论（逐条）

### 01-简单框架-系统骨架.md

OK   L7/L9   「74 个平台标识」+ 口径（`Platform+0`=63、尾部 `| 'custom';`=266、含 custom 与 6 个搜索平台）——复跑 python 解析 **74**；`custom` 在场；tavily/exa/firecrawl/linkup/parallel/serpsearch 分别在 138-143。搜索平台「只服务 `/v1/search`」由 `providers/search-only.ts:5-10` 注释 + `proxyRouter.post('/search')`=routes/proxy.ts:755（挂 `/v1`，app.ts:309）双向印证 (证据: shared/types.ts:63/266；search-only.ts:7)
OK   L15-18  「默认只绑定 127.0.0.1」三层拆分 —— `host: process.env.HOST ?? '::'`=lib/config.ts:76；`server.on('error')`=index.ts:130、回退分支 135-141（`EAFNOSUPPORT`/`EADDRNOTAVAIL` → `app.listen(PORT,'0.0.0.0')`=137）、handler 闭合 144；desktop `const host = cfg.lanAccess ? '0.0.0.0' : '127.0.0.1'`=desktop/src/main.ts:271；compose `"${HOST_BIND:-127.0.0.1}:${PORT:-3001}:3001"`=docker-compose.yml:25。四个断言全部命中 (证据: 逐行 sed 抽读)
OK   L37/L38/L42/L44/L51-56  mermaid：routerSvc 不做重试/流式、新增 `lib/fallback-loop.ts` 节点与三条边、providers 节点计数、crypto 由「信封加密」改「对称加密 + 落库前加密」——`encrypt()` 每次 `crypto.randomBytes(16)` 新 IV(184) + `getAuthTag()`(189)，`ALGORITHM`='aes-256-gcm'(7)，api_keys 落库前 `encrypt()` 见 routes/keys.ts:207；`express --> ratelimitSvc` 边成立（routes/models.ts:25 import recordRequest/recordTokens）(证据: crypto.ts:182-196；keys.ts:207)
OK   L66    desktop 走读指向 08 篇（`08-启动生命周期.md` 存在）
OK   L76    shared 行的全部类型行号：`Platform`=63、`Model`=279、`ApiKey`=349、`ChatMessage`=489、`ChatCompletionRequest`=506、`TokenUsage`=531、`ChatCompletionResponse`=546、`ChatCompletionChunk`=559、`ProviderQuotaState`=634（`grep -nE '^export (interface|type) ...'` 一次命中全部）
OK   L79    「20 个 coding agent」+ 口径命令 `grep -c "^  \['" cli/src/tools.ts` → **20**；`metadata`=1037-1058、`tools` 映射=1060-1080
OK   L102   cli 依赖补 `cross-spawn@7`（cli/package.json dependencies: cross-spawn ^7.0.6、jsonc-parser ^3.3.1、yaml ^2.9.0）
FIX  L116-125/L135-147 §3.2 图内数字全部复验：createApp=99、proxy `/chat/completions`=1643、requireInferenceAuth=69、resolveRoutingChain=1437、routeRequest=2152、runFallbackLoop=1348、BaseProvider=229、canMakeRequest=312/canUseTokens=334/recordRequest=821/setCooldown=1241、checkAllKeys=497、syncCatalog=1021、decrypt=204、边标 proxy.ts:2300 与 2453 均命中
FIX  L14   前一轮没动的旧断言「单请求最多 20 次重试」不精确：循环是 `for (let attempt = 0; attempt < maxRetries; attempt++)`=fallback-loop.ts:1407，即 **20 次尝试**（首发 + 最多 19 次重试）；已改写并补 `hooks.maxRetries` 覆盖点=1368
OK   L151-152 步骤 1/2 全部锚点：createProxyRateLimiter=middleware/rateLimit.ts:34、`/v1` 挂载=app.ts:302、extractApiToken=proxy.ts:81（三种头 82-91）、`freellmapi-<48 hex>`=db/index.ts:233（`randomBytes(24).toString('hex')`）、chatCompletionSchema=602/safeParse=1656、CompletionOptions=base.ts:163、ChatMessage=489 (证据: 逐行)
FIX  L153  步骤 3：前一轮写「调用点 1366 / 2300」未区分归属，易读成一次请求两处调用 → 现写明 2300 属 `/chat/completions`=1643、1366 属 legacy `/completions`=1232；并把「`getActiveChain()`（1328，直接 JOIN …）」改成真实两分支 SQL（1336-1346 profile_models JOIN models；1348-1357 fallback_config JOIN models）+ 1330-1333 的 `CHAIN_CACHE_TTL_MS`=1_000（1322）缓存 (证据: router.ts:1322-1360)
FIX  L154  步骤 4 闸门链缺最后一道门：源码在 `canUseProviderTokens`(1672) 之后还有 `checkMonthlyBudget`(services/key-budget.ts:92)@router.ts:1677 → 已补；其余 8 个调用点行号（1660/1661/1665/1669/1670/1671/1672/1681）与 ratelimit 定义行（665/689/120/312/334/783）全部复验 (证据: router.ts:1651-1690)
OK   L155-156 步骤 5/6：`route.provider.streamChatCompletion`=proxy.ts:2453；成功记账 `recordUpstreamSuccess`=663 内部 `recordRequest`(673)/`recordTokens`(674)；失败 `recordRetryableFailure`=440 → `setCooldown`=535、`recordAuthFailure`=651 → `setCooldown`=653（`AUTH_FAILURE_COOLDOWN_MS`=627=5min）
OK   L166  app.ts 行：`grep -cE '^\s*app\.use\(.*Router' server/src/app.ts` → **32**，`grep -cE '^\s*app\.use\(' ` → **49**；createApp=99
FIX  L167  模块职责表「主代理路由」行前一轮没清：原句把 `/v1/responses` 记在 proxy.ts 名下，但 proxy.ts 全文无 `/responses` 路由，它属于 `routes/responses.ts` 的 `responsesRouter.post('/responses')`=657（app.ts:313 挂载）→ 改成 proxy.ts 真实 wire 面 11 条路由 + 行号，并注明 responses.ts 复用 proxy.ts 的 helper（responses.ts:24-32 import extractApiToken/getRequestGroupId/getStickyModel/setStickyModel/streamReasoningText/completionReasoningText/traceRouteEvent/logRequest）。「工具调用救援」保留：`repairToolArguments`=proxy.ts:2609/2623/2897
FIX  L169  路由器行的「模型失败惩罚」原无锚 → 补 `recordModelFailure`=285、`DECAY_INTERVAL_MS`=275（2 分钟一档、`DECAY_AMOUNT`=1）
OK   L170  回退循环行 6 个符号（1348/243/440/663/651/315）+ `FALLBACK_MAX_RETRIES`=20(69) + `DEFAULT_FALLBACK_TIME_BUDGET_MS`=45_000(172) 命中；本轮把「最多 20 次」改成「20 次尝试」与 L14 口径统一
OK   L171  限流账本行 9 个锚全部命中：98/120/312/334/665/689/783/821/833/963(`DAY`)/1112/1241/1255，文件 1576 行；`rate_limit_usage` 落库=ratelimit.ts:218，租约段 50-81 (`leases`=69、`LEASE_MAX_AGE_MS`=76)
FIX  L173  Provider 注册表行有两处口径/算术错（详见「推翻前一轮」1、2）→ 重写为：73 次 `register()`（命令 → 73；`register()`=47 只做 `providers.set(provider.platform, provider)`，表=`Map<Platform, BaseProvider>`=45），其中 33 次是 `register(new OpenAICompatProvider({...}))`（`grep -c '^register(new OpenAICompatProvider'` → 33）、40 次平台专属类；`grep -c 'new OpenAICompatProvider'` → 34，多出的是 `resolveProvider()` 给 `custom` 现场实例化（640），不是注册项；74 个 Platform 里只有 `sambanova` 无 provider 模块（V23 下线，types.ts:61-62 注释），所以恰好 73；44 个文件里 index/base/openai-compat/search-only 是共用设施、其余 40 个一平台一文件；43 个 `class *Provider` 中 `BaseProvider`(229) 与 `SearchOnlyProvider`(search-only.ts:14) 是 abstract，**41 个具体类**（不是 42）
OK   L172  base.ts 行 14 个锚全中（19/163/192/210/227/229/230/231/238/246/254/266/274/285/326），类体 229-525=文件全长
OK   L176  加密行：ALGORITHM=7、KEY_BYTES=18、jsdoc 86-93、initEncryptionKey=94、fingerprint=173、isInitialized=178、encrypt=182、decrypt=204、maskKey=227；key 文件 `.encryption-key`=crypto.ts:27、`{ mode: 0o600 }`=78；轮换脚本 `server/src/scripts/rotate-encryption-key.ts` + `server/package.json:16` 的 `npm run rotate-encryption-key`
OK   L178  数据库行：WAL=82、busy_timeout=5000=87、shouldHardenDataDir=122-136、parseDirHardeningOverride=140-147、restrictDataDir=153-172、initDb=197、getDb=20、connectDb=49、getDefaultDbPath=27、getUnifiedApiKey=225、regenerateUnifiedKey=231、getSetting=239、setSetting=245；`runMigrationsSync` 定义=db/migrate/runner.ts:64、db/index.ts:6 import、204 调用（203 判 NODE_ENV）
OK   L186-197 环境变量表：PORT=3001(config.ts:72)、HOST='::'(76)、dbPath null(77)、dashboardOrigins `[]`(78-81)、clientDist(82)、proxyRateLimitRpm 120=`DEFAULT_RPM`(1)+parse(22-28)、REQUEST_BODY_LIMIT_MB 25=`DEFAULT_REQUEST_BODY_LIMIT_MB`(20)+parse(30-36)、TRUST_PROXY(100-112)、CSP(114-121)、NODE_ENV(85/203)；`DEFAULT_DASHBOARD_ORIGINS`=app.ts:51-55、并集=app.ts:108-111
FIX  L205-226 文末源码索引：前一轮只改了 router/ratelimit/base/index 四行，其余仍带 `1-800+` / `1-550+` / `1-300+` 这类低估且 `db/index.ts` 行把 197-251 当成 getDb/connectDb 的范围。本轮把 207/208/214/215/216/217/218 七行换成实测值：proxy.ts 1-3102、anthropic.ts 1-1194、health.ts 1-645、catalog-sync.ts 1-1240、crypto.ts 1-231、config.ts 1-121、db/index.ts 1-251，并把符号级行号补进表内；保留并复验 index.ts main()=31-145、app.ts createApp()=99-382、base.ts 229-525、providers/index.ts 626-628/636-648/650-652/654-656、legacy_baseline createTables()=58-232、desktop/main.ts 1-382、server-host.ts startServer()=94-174、bundle-server.mjs build()=13-31、cli/index.ts main()=455-492、tools.ts 1037-1058/1060-1080、client/App.tsx App()=464-520

### 06-配置与数据流.md

OK   L78  `getKeyConcurrencyLimit`=ratelimit.ts:98：先读 `MAX_CONCURRENT_REQUESTS_PER_KEY_<PLATFORM>`(99) 回落全局(100)，非正整数/未设 → `return null`(105)；「源码注释明确拒绝内置每平台默认值」=91-93；消费方 `canUseKeyConcurrency`=120（122 对 null 直接放行）、`inFlightForKey`=109 (证据: ratelimit.ts:90-124)
FIX  L147-153 降级分支表（前一轮新增，逐条复验）：
     - readConfigFromEnv=151，裸 `JSON.parse`=153(内联)/156(文件)；`main().catch` → console.error + `process.exit(1)`=index.ts:147/152/153 ✓
     - schema 不过 → `applyDeclarativeConfig+2~+4`=468-470 throw ✓；`.strict()`=118 ✓
     - 交易内 throw 点：`upsertApiKey+6`=191 unknown provider platform、`+8`=193 key is required、`+13`=198 baseUrl is required ✓；`resolveDeclaredModel+14/+20/+24`=360/366/370 ✓（346 起，三条分别是 endpoint 无匹配 / endpoint 多匹配 / 模型多端点歧义）；`db.transaction`=486、`apply()`=526 在 try 之外 ✓ 回滚冒泡
     - `fallback` 跳过：`applyFallback+5`=458 `if (!row) return;`，457 是 `resolveDeclaredModel` ✓
     - admin 段：见「推翻前一轮」4；keys 段：见「推翻前一轮」3；license 段：见「推翻前一轮」5
FIX  L155 `declarative-config.ts:166-172` → **166-171**（172 已是 `const MISSING_KEY_HINTS`）；并补「全文件 `warnings.push` 仅 2 处：493 与 500」（`grep -n 'warnings.push'` 实测）
FIX  L171 段落与前表自相矛盾：原句仍写「`warnings` 是 per-entry skip 清单（坏 key、**未知 platform** 等）」，而未知 platform 在 191 是 throw → 改为「只可能来自两条降级分支；未知 platform 与 endpoint 歧义不在其中，它们是 throw」，并补 `DeclarativeConfigResult`=122
OK   L169 routing 行：`z.enum`=declarative-config.ts:108 **7 个成员**（priority/balanced/smartest/fastest/reliable/custom/decision），与 router.ts:513 `VALID_STRATEGIES` 逐项一致；`routing` 出现时 strategy 必填（无 `.optional()`），weights/keySelectionStrategy 可省（113/116）；应用顺序 setCustomWeights(518)→setRoutingStrategy(519)→setKeySelectionStrategy(520-522)，定义分别=router.ts:626/522/598，三者都写 settings（522/598/626 函数体内 setSetting）
FIX  L204 开关总表把声明式 `routing` 标成「仅首装」，与 §5.2「配置一次语义」+ §8 P2「重启会被 JSON 再次覆盖」矛盾：`applyDeclarativeConfigFromEnv` 在 index.ts:48 每次启动都跑 → 改为「每次启动都重放一遍，不是只在首装生效」
OK   L141 调用点 index.ts:47 initDb → 48 applyDeclarativeConfigFromEnv → 78 createApp → 126 listen，listener 之前 ✓
OK   L163/165/175 admin/keys 段与 5.3：adminSchema=93（注释 87-92 即「窗口不是被缩短而是被消除」的原文）、`userCount() === 0` 判在 declarative 之后（index.ts:70）✓、`encrypt()` 落 api_keys ✓
OK   L111-124 4.1 段：`getFallbackTimeBudgetMs`=183-197、+0~+13=183-196 ✓；引用注释原文 =170-171 ✓；`DEFAULT_FALLBACK_TIME_BUDGET_MS`=45_000(172)、settings 键 `fallback_time_budget_ms`(181)、try 包裹 getSetting(185-189)、空串跳过(192)、`n >= 0`(194) 全部命中
OK   L128 restoreProxySettings=lib/proxy.ts:391-397，五个 apply 从 392 起、`proxy_enabled !== '0'`=395 ✓
OK   L75-94 provider-timeout：`providerTimeoutEnvName`=43（大写 + `[^A-Z0-9]`→`_`，44 行）、`providerTimeoutMs`=51、`DEFAULT_STREAM_STALL_TIMEOUT_MS`=90_000(55)、`streamStallTimeoutMs`=66；`fetchWithTimeout`=base.ts:326，默认参数 `providerTimeoutMs(this.platform, 15000)`=331 ✓
OK   L225-235 源码索引 11 行全部复验：config.ts 1-20/22-36/38-68/70-93/100-112/114-121、env-drift 11-26(白名单 11、patterns 23)/65-76/108-130（文件 130 行）、fallback-loop 159-181/183-197、proxy 392-396、provider-timeout 1-70（文件 75 行）、base 326-333、ratelimit 95-100、model-weight-overrides 119-185（函数=119、文件 185 行）、declarative-config 25-54/56-85/93-96/98-118/122-136/151-159/466/569、db/index getSetting=239/setSetting=245
SKIP L29-36 四层表与 L57「CORS/CSRF 白名单」措辞：dashboardOrigins 用于 CORS 已验（app.ts:108-111）；CSRF 侧本轮未逐行读取，不在本次三类清单内，未改（不新增断言）

---

## 二、推翻前一轮（前一轮写错/写歪，本轮已改成磁盘现值）

1. **01:173「其中 33 次直接 `new OpenAICompatProvider({...})`」** —— 数字本身对（`grep -c '^register(new OpenAICompatProvider' index.ts` → 33），但它把 RULES2 事实表的 34（`grep -c 'new OpenAICompatProvider'` → 34）当成了另一个不可复现的数：读者按事实表命令复跑会得 34，与正文「33」冲突且无解释。**改成**：33 次是 `register(new OpenAICompatProvider({...}))`、40 次平台专属类；并显式说明「文件里 `new OpenAICompatProvider` 共 34 处，多出的一处是 `resolveProvider()` 为 `custom` 现场实例化（640），不是注册项」——两个口径都能复跑。
2. **01:173「43 个类（含 BaseProvider，即 42 个可实例化类，其中 OpenAICompatProvider/SearchOnlyProvider 是复用实现而非单一平台）」** —— 算术与事实都错：43 个 `class *Provider` 里 **2 个是 abstract**（`BaseProvider`=base.ts:229、`SearchOnlyProvider`=search-only.ts:14），具体类是 **41 个而不是 42**；且 `OpenAICompatProvider` 不是抽象复用而是被 33 个平台直接 `new` 的具体类，把它和 `SearchOnlyProvider` 并列成「复用实现」掩盖了真正的复用关系（6 个搜索平台 extends SearchOnlyProvider）。**改成**：43 个类 / 2 个 abstract / 41 个具体类，另加「44 个文件里 index/base/openai-compat/search-only 是共用设施、其余 40 个一平台一文件」与「74 个 Platform 成员里只有 `sambanova` 没有 provider 模块（V23 下线，types.ts:61-62），所以注册表恰好 73」。
3. **06:150「`applyDeclarativeConfig+30~+36`=496-502 `warnings.push` + `continue`」** —— 496 是 **上一个 admin 块的收尾 `}`**，497 才是 keys 循环开头，真正的 `warnings.push`/`continue` 在 **500-502**。**改成**：「`applyDeclarativeConfig+31`=497 的循环里 +34~+36=500-502」。
4. **06:151「`applyDeclarativeConfig+24~+28`=490-494」** —— 490 是 **成功路径** `result.admin = true;`，降级分支（else）是 **491-494**。**改成**：+25~+28=491-494，并注明 488 判 `userCount() === 0`、489-490 是创建成功路径。
5. **06:153「`void activateConfiguredLicense(…)`=545」** —— 545 是**函数定义**行，调用点在 **534**（533 置 `result.license = true`）；照原文读者会以为 532-535 的分支里有 545。**改成**：「532-535：533 置 `result.license = true`，534 `void activateConfiguredLicense(...)` 起后台激活（函数定义=545）」，并把「连不上 / 被拒 / 异常只 console.warn」落到具体行 **551 / 555 / 565**。
6. **06:155「注释在 `declarative-config.ts:166-172`」** —— 172 已是 `const MISSING_KEY_HINTS`，注释块是 **166-171**。**改成** 166-171（本轮 L171 新写的句子也用 166-171，两处一致）。
7. **06:171 段落未改完、与新表直接冲突** —— 前一轮在 5.1 建了「未知 platform 是 throw」的表格，却把紧跟其后的总结句留着原文「`warnings` 是 per-entry skip 清单（坏 key、**未知 platform** 等）」。**改成**：warnings 只来自那两条降级分支，未知 platform / endpoint 歧义不在其中（`warnings.push` 实测仅 493、500 两处）。
8. **06:204「声明式 `routing`（仅首装）」** —— 与它自己新加的 §5.2 句子和 §8 P2（重启再次覆盖）矛盾；`applyDeclarativeConfigFromEnv` 在 index.ts:48 每次启动都执行。**改成**「每次启动都重放一遍，不是只在首装生效，见第 8 节 P2」。
9. **01:14/01:170 残留旧断言**（前一轮没扫到的同类）：「单请求最多 20 次重试」按源码是 20 次**尝试**（attempt 0..19），已统一为「最多 20 次尝试（首发 + 最多 19 次重试）」并挂 1407/1368 锚。
10. **01:167 模块归属错**（前一轮没改）：`/v1/responses` 记在 `routes/proxy.ts` 名下，实际 proxy.ts 无该路由，属 `routes/responses.ts:657`（app.ts:313 挂载）。已改并补 proxy.ts 真实 11 条路由行号。
11. **01:153/154 数据流小节两处「不完整/易误读」**（前一轮改到一半）：runFallbackLoop 两个调用点未区分归属；`getActiveChain` 写成「直接 JOIN」却漏了 1330-1333 的 1 秒缓存；闸门链漏 `checkMonthlyBudget`。三处均已补齐。
12. **01:76「被 server + cli 引用」口径不全**：client 也有 4 个源文件 `import '@freellmapi/shared'`（且 client/package.json 未声明该依赖）。已补，并写明根 workspaces = shared/server/client/cli、desktop 不在其中也不引用它。
13. **01:205-226 源码索引未收尾**：`1-800+`/`1-600+`/`1-550+`/`1-300+`/`1-200+` 是对 3102/1194/645/1240/231 行文件的低估，`db/index.ts` 行 197-251 覆盖不到它列出的 `getDb()`(20)/`connectDb()`(49)。七行全部改为实测值。

---

## 三、报告 / 事实表纠错（本轮亲自复跑后推翻上游）

1. **RULES2 事实表「`new OpenAICompatProvider` = 34」口径含糊**：34 是**文件内出现次数**（含 `resolveProvider()` 640 的 custom 现场实例化），**注册级别只有 33**。任何写「73 次 register 中 N 次是 compat」的正文都必须注明命令，否则与 34 打架（见「推翻前一轮」1）。
2. **RULES2 事实表「Platform 联合成员 74：python3 解析 shared/types.ts:63」**有个坑：联合里每条成员前都有 `//` 注释，而注释文本里有分号（line 68 `…attached; usage beyond…`）。按「读到 `;` 为止」朴素解析只会得 **3** 个成员。本轮改用「跳过 `//` 行、只取以 `|` 开头的字面量、直到该行以 `;` 结尾」得 74，尾部行 266 `| 'custom';`。
3. **report-01-06-08-09 SEMANTIC 01:38/01:156「现有 41 个平台模块（除 index.ts / base.ts）」两头都不对**：目录共 44 个 .ts，除 index/base 是 **42**，再除 openai-compat.ts 与 search-only.ts 才是 **40**（一平台一文件）。「41」应是只减了三个特殊文件却漏数了 openai-compat。正文不再写这个口径，只写 44 文件 + 40 一平台一文件 + 43 类。
4. **report 只点了 `getKeyConcurrency` 与 `routing.strategy` 两个 06 的符号问题**，漏掉 §5.1 的降级/失败分界本身被写成「单条目坏值只降级为 warning」的过度概括（真实是 3 条 throw 分支 + 4 条降级分支），以及 §7 开关表「仅首装」的错误生效方式。两处本轮已按源码重写/改正。
5. **RULES2 关于「第一轮已把锚点全部校准」的前提**对本轮两个文件成立：本轮没有发现任何一处**未被前一轮改动**的行号失效（§5 环境变量表、§6 源码索引旧行、06 §4/§4.1/§4.2/源码索引 11 行全部复跑命中），只发现旧**语义**归属错（01:167 `/v1/responses`）与旧**口径**不全（01:76、01:205-226 的 `+` 区间）。

---

## 四、落盘校验（编辑后磁盘回读）

本轮两文件改动行数：`git diff --stat` → 01 = 120 行（前一轮 102）、06 = 24 行（前一轮 20）。

01 关键行磁盘回读：
- L14 `- **故障转移**：单请求的回退循环最多 20 次尝试（\`FALLBACK_MAX_RETRIES\`=20，即首发 + 最多 19 次重试；\`for (let attempt = 0; attempt < maxRetries; attempt++)\`=lib/fallback-loop.ts:1407）…`
- L76 shared 行含 `包名 \`@freellmapi/shared\`…被 server、cli 引用；client 也有 4 个源文件 import 它`
- L153 含 `另一个调用点 1366 属于 legacy \`/completions\`=1232` 与 `1330-1333 命中 \`CHAIN_CACHE_TTL_MS\`=1_000（1322）`
- L154 含 `→ \`checkMonthlyBudget\`(key-budget.ts:92)=1677`
- L167 含 `\`/chat/completions\`=1643 … \`/audio/transcriptions\`=1068` 与 `responses.ts:24-32`
- L169 含 `模型失败惩罚（\`recordModelFailure\`=285 加权记分，2 分钟衰减一档 \`DECAY_INTERVAL_MS\`=275）`
- L170 含 `上限 \`FALLBACK_MAX_RETRIES\`=20 次尝试（\`hooks.maxRetries\` 可覆盖，1368）`
- L173 含 `33 次是 \`register(new OpenAICompatProvider({...}))\` … \`grep -c 'new OpenAICompatProvider' index.ts\` → 34` 与 `41 个具体类`
- L207/208/214/215/216/217/218 = `1-3102` / `1-1194` / `1-645` / `1-1240` / `1-231` / `1-121` / `1-251`

06 关键行磁盘回读：
- L150 `… \`applyDeclarativeConfig+31\`=497 的循环里 +34~+36=500-502 \`warnings.push\` + \`continue\``
- L151 `\`applyDeclarativeConfig+25~+28\`=491-494（else 分支；488 判 \`userCount() === 0\`，489-490 是创建成功路径）`
- L153 `\`applyDeclarativeConfig+66~+69\`=532-535：533 置 \`result.license = true\`，534 \`void activateConfiguredLicense(...)\` 起后台激活（函数定义=545）… 连不上 551 / 被拒 555 / 抛异常 565`
- L155 `…（全文件 \`warnings.push\` 仅 2 处：493 与 500）…（\`declarative-config.ts:166-171\`）`
- L171 `\`warnings[]\` 只可能来自上面表格里那两条降级分支 … **未知 platform 与 endpoint 歧义不在其中**`
- L204 `或声明式 \`routing\`（每次启动都重放一遍，不是只在首装生效，见第 8 节 P2）`

自检（RULES2 第 7 条，两文件合并跑，期望空）：
`grep -nE '\b(checkAndReserve|recordResult|RateLimiter|StreamChunk|ChatResponse|listProviders|getAllModels|pickModel|convertMessages|RESERVED_TABLES|dbBackupPump|rotateEncryptionKey|getModelCapabilities|checkHealth|ChatRequest|getKeyConcurrency)\b' 01….md 06….md` → **无输出（exit=1）**。
扩展残留清单 `grep -c`：`33 个` 0/0、`Router 类` 0/0、`pickModel` 0/0、`六枚举` 0/0、`60+` 0/0、`21 个` 0/0、`29 个` 0/0、`信封加密` 0/0、`曾经` 0/0、`旧名` 0/0；`RateLimiter` 在 01 命中 2 处均为真实符号 `createProxyRateLimiter`（L116/L151，非 `\bRateLimiter\b`）；`127.0.0.1` 在 01 命中 3 处全部是合法断言（desktop 默认 271、compose HOST_BIND 25、dev CORS origin）。
历史叙述检查：两文件均无「曾经叫 X / 现在改为 / 旧名」句式（`曾经`=0、`旧名`=0）。
