# 05-API与接口设计.md 正文语义校正报告（第二轮）

仓库 `/Users/vincent/workspace/16_AI/freellmapi`（分支 adrian）。只改 `docs/adrian/sourceReader/05-API与接口设计.md`：227 行 → 340 行，章节 `## 0`~`## 12` 全部保留、编号未动（`grep -c "^## "` → 13）。未 commit、未 push、未改任何源码文件。

RULES2 第 7 条自检（改完后跑，期望为空）：

```
grep -nE '\b(checkAndReserve|recordResult|RateLimiter|StreamChunk|ChatResponse|listProviders|getAllModels|pickModel|convertMessages|RESERVED_TABLES|dbBackupPump|rotateEncryptionKey|getModelCapabilities|checkHealth|ChatRequest)\b' docs/adrian/sourceReader/05-API与接口设计.md
→ 无输出（exit=1）
```

禁用词自检：`grep -nE '等等|以此类推|待补|待核实|未实测|未逐条核实'` → 无输出；`grep -n '…'` 只剩 §1.2 认证图里 `Bearer …` 这类占位与 §12 的 `gemini.ts /v1beta/models…` 路径简写（均为上一轮既有、非「替代核心内容」）。

下文「文档:行」一律给改后磁盘上的行号（每条都 `grep -n` 回读确认落盘）。

## A 类（符号已消失 / 名字写错）

A  文档:226-230  `内部 ChatRequest` -> `InboundChatRequest` / `runInboundChat` / `runFallbackLoop`（证据：`grep -rw ChatRequest shared server/src cli/src` → 0 命中；真实符号 `InboundChatRequest`=server/src/lib/inbound-chat.ts:51、`runInboundChat`=165、其内 `await runFallbackLoop({`=228、`runFallbackLoop`=server/src/lib/fallback-loop.ts:1348，调用点 proxy.ts:1366/2300、anthropic.ts:681、responses.ts:1172、inbound-chat.ts:228；gemini.ts:199、ollama.ts:411、531）

A  文档:150  `settings.mcp_enabled` -> settings 表键 `enable_mcp`（证据：`grep -rn mcp_enabled server/src` 只命中 `MCP_ENABLED_FILENAME`/migration 文件名与 mcp.ts:384 的响应字段；真实常量 `export const MCP_ENABLED_SETTING = 'enable_mcp'`=server/src/routes/mcp.ts:656，`isMcpServerEnabled`=658，`mcpRouter.use` 门=666）

A  文档:269-276  `X-Execution-Id` -> `X-Request-ID`；`Routed-Model` 头 -> 删除（证据：`grep -rhoa "setHeader('[^']*'" server/src --exclude="*.test.ts" | sort -u` 的头名全集里没有这两个；execution id 载体 `res.setHeader('X-Request-ID', ...)`=proxy.ts:1235、1646、responses.ts:665；`observeServedModel`=server/src/lib/served-model.ts:61，该文件 `grep -na setHeader` → 0 命中，注释第 17 行「The response contract is untouched」）

A  文档:190  `/api/settings ... enable-mcp…` -> 点名 `PUT /api/settings/enable-mcp`（证据：settingsRouter.put('/enable-mcp')=server/src/routes/settings.ts:147，配套 GET=141）

## B 类（数字 / 事实过期）

B  文档:207-215  「33 个 provider 单例」-> 五个口径分表列出：73 / 74 / 43 / 34 / 44（证据：`grep -cE '^\s*register\(' server/src/providers/index.ts` → 73，首尾 index.ts:54-620；`Platform` 联合 `shared/types.ts:63-266` → 74 个成员；`grep -rhoE 'class [A-Za-z0-9_]+Provider' server/src/providers/*.ts | sort -u | wc -l` → 43；`grep -c 'new OpenAICompatProvider' server/src/providers/index.ts` → 34；`ls server/src/providers/*.ts | wc -l` → 44）

B  文档:217  73 vs 74 差额归因 -> `'sambanova'`（证据：`grep -rn sambanova server/src/providers/` → 0 命中，而 `| 'sambanova'`=shared/types.ts:131；`'custom'` 反而**有**注册，index.ts:616-620 是它的占位实例。用脚本把 73 个 `register()` 逐条解析成 platform（`platform:'x'` 字面量 + 子类的 `readonly platform='x'` / `super({platform:'x'})`），得 73 个 distinct，全部落在联合内）

B  文档:219  「契约三方法 + 两个可选」-> 抽象 5（`platform`:230、`name`:231、`chatCompletion`:238、`streamChatCompletion`:246、`validateKey`:254）+ 可选覆盖 3（`fetchQuota`:266、`hasQuotaProbe`:274、`supportsKeyValidation`:285）+ 非抽象字段 `keyless`:236（证据：`grep -n "abstract \|keyless = false\|async fetchQuota\|get hasQuotaProbe\|get supportsKeyValidation" server/src/providers/base.ts`）

B  文档:249  「21 个 agent」-> 20（证据：`metadata`=cli/src/tools.ts:1037-1058 共 20 个元组（`awk 'NR>=1037&&NR<=1058' | grep -c "^  \['"` → 20）；`export const tools: ToolDefinition[] = metadata.map(`=1060、块尾 `}));`=1080；`grep -cE ': GenerateContext\): Generation' cli/src/tools.ts` → 20 个生成器函数；顶层命令派发 index.ts:457/470/478/484/488/489/490）

B  文档:158-159  livez/readyz 描述 -> 按 handler 体重写（证据：200 体 `res.json({status:'ok', version, uptime_s})`=server/src/routes/status.ts:57、503 多带 `checks:{db, encryption_key}`=52、依赖检查两个函数调用=42-43；readyz 200 体 `{status:'ok', ready_upstreams}`=81，四个 `reason` 分支=66、89、91、93，出口=96）

B  文档:158  「livez 是 Docker HEALTHCHECK 的目标」-> Docker 打的是 `/api/ping`（证据：Dockerfile:83-84 与 docker-compose.yml:41 都 `fetch('http://127.0.0.1:'+(process.env.PORT||3001)+'/api/ping')`；CLI doctor 才打 livez：`probeGateway`=cli/src/doctor.ts:303-310）

B  文档:57  「createProxyRateLimiter(120 RPM) / createAdminRateLimiter」-> 补默认值出处（证据：`DEFAULT_RPM = 120`=server/src/middleware/rateLimit.ts:16、`ADMIN_DEFAULT_RPM = 600`=91、`EXPORT_RATE_LIMIT_RPM = 10`=server/src/app.ts:43）

B  文档:37、161、199、284  「/api/ping 未在挂载表出现 / 归属待补」-> 事实化：内联 `app.get('/api/ping', (_req,res) => { res.json({status:'ok',timestamp:...}) })` = server/src/app.ts:279-281，无 `requireAuth`（app.ts:278 注释），但仍在 `app.use('/api', adminRateLimiter)`（app.ts:233）覆盖范围内；`healthRouter` 只注册 `GET /`=13、`POST /check/:keyId`=64、`POST /check-all`=78、`POST /quota/:keyId`=89

## C 类（结构缺漏 / 小节内重写）

C  文档:10-53  §0 挂载树与 app.ts 逐行对齐，去掉 `... 其余 /api/* 全部 requireAuth` 这类省略写法；新增此前缺失的真实挂载：`app.use([ollama 7 条精确路径], createProxyRateLimiter)`=app.ts:215-218、`/api/search`（requireAuth, searchRouter）=263、`/api/decisions`（requireAuth, decisionsRouter）=264、内联 `/api/ping`=279-281；把原先合并写的 limiter/router 对（296/297、302/308/309/311/313、316/317、324/325）拆成逐条；`:244` 一行改成源码原样 `createAdminRateLimiter(EXPORT_RATE_LIMIT_RPM)`（证据：`grep -n "app.use('/api" server/src/app.ts` → 23 行：233、238、244、246、250、253、257-269、273、274、275、276；`grep -c "app.use('/api"` → 23、其中含 Router 的 21 条、带 requireAuth 的 20 条）

C  文档:65-78  §1 表补上 5 条此前缺失的真实 `/v1` 端点：`POST /v1/search`=proxy.ts:755（→`runSearch`=services/search.ts:483）、`GET /v1/search/engines`=799（→`listSearchEngines`=597）、`POST /v1/decisions`=876 与 `POST /v1/systemone`=877（同一个 `handleDecision`=835 → `runDecision`）、`GET /v1/decisions/models`=880（证据：`grep -n "proxyRouter\.\(get\|post\)" server/src/routes/proxy.ts` → 317、680、715、755、799、876、877、880、925、963、1019、1068、1232、1643）

C  文档:65、66、67、73  行为断言复核并落到具体行：`?available=true` 实为 `available`/`connected`/`ready` 三别名 + `1`/`true`/`yes`（proxy.ts:337-338）；auto 判定连 `auto:` 前缀一起算（`isAutoModel`=proxy.ts:53-57，注释起 47）；legacy `/completions` 的翻译函数点名 `completionPromptToMessages`=proxy.ts:1175（调用点 1259）、回写形态 `object:'text_completion'`（1217、1571）、`max_tokens` 缺省 128（1255-1256）；multer 上限常量确认存在且名字不变（`MAX_TRANSCRIPTION_BYTES`=services/media.ts:962=25 MiB，`limits:{fileSize:..., files:1}`=proxy.ts:1059）

C  文档:83、91  双 handler 的决胜机制改成事实：不是「不同鉴权头（x-api-key）」，而是 `if (!req.headers['anthropic-version']) return next();`=anthropic.ts:1165；别名暴露受设置项 `expose_cc_discovery_aliases` 控制（anthropic.ts:1170），`claudeFamilyDiscoveryEntries` 调用点=1176。挂载顺序 anthropic 在前的断言复核为**仍成立**（app.ts:308 vs 309，且 app.ts:303-307 注释即为此说明）

C  文档:140-150  §4 MCP 小节重写：三条路由 `POST /`=mcp.ts:676、`GET /`=700、`DELETE /`=703（证据：`grep -n "mcpRouter\.\(get\|post\|delete\|put\)" server/src/routes/mcp.ts` → 恰好这三条），GET/DELETE 都是恒 405 + `-32000` 的 stateless 说明；「工具目录 = 可用模型」改成真实的 `TOOLS`=mcp.ts:427-573 共 13 个（ask_freellmapi / healthcheck / list_models / provider_health / usage_summary / routing_info / set_routing_strategy / cache_stats / web_search / compression_stats / provider_list / clear_cache / quota_outlook；`awk 'NR>=427&&NR<=590' | grep -cE "^  [a-z_]+: \{"` → 13）；开关播种规则取自 migration 头注释（20260903_000001_mcp_enabled_default.ts：有 key 的老装 `1`、空库新装 `0`、已有值不覆盖）

C  文档:134  §3 共存说明补真实 limiter 挂载与 legacy `/api/embeddings` 的放行条件（证据：ollama.ts:601-607，`validateSession(dashboardToken)` 命中即 `next()`=606；app.ts:213-214 注释「key-required 模式没有这层就是可暴破的凭证检查」）

C  文档:167-199  §6 清单逐条加 app.ts 行号、补 `/api/search`+`/api/decisions`+内联 `/api/ping`，并把 `/api/health` 的行为描述换成 healthRouter 真实路径；`PUT /api/fallback/routing` 复核成立（fallback.ts:98，GET 在 34）。表尾加一段「21 条 router 挂载只有 /api/auth 不带 requireAuth」的口径说明

C  文档:245-251  §8 CLI 行内补齐 `keys` 六个端点各自的 keys.ts 行号（119、128、141、150、162、176）与四选一派发点（keys.ts:73）；「四种 merge 语义」改为点名 `renderFile`=config-files.ts:348 的四路分发（349-356）+ 六个 merge 函数行号（18/67/153/193/277/322）+ 两阶段提交的真实实现（`applyGeneratedFiles`=409、备份 396-397、临时文件 `renameSync` 400-401、`0o600` 400/402、父目录 `0o700` 393）

C  文档:267-276  §10 重写为按源码真实头名分组列出（`X-Routed-Via` 2082/2094/2130、`X-Fallback-Trail|Detail|Attempts` 由 `setFallbackHeaders`=fallback-loop.ts:842-864、`X-FreeLLM-Cache` 2083/2426、`X-FreeLLM-Compress` proxy.ts:1803/anthropic.ts:520、`X-FreeLLM-Routing-Strategy` proxy.ts:2298/anthropic.ts:679、`X-Provider`+`X-Model` proxy.ts:995-996/1135-1136、`Retry-After`+`X-RateLimit-*` rateLimit.ts:60-66 与 127-133），并说明 `observeServedModel` 只进日志与 `requests.served_model`

C  文档:284-285  §11 第 1 行从「待核实」改为已核实事实 + 真实残留风险（ping 无条件回 `{status:'ok',timestamp}`、不查依赖）；第 2 行的「靠挂载顺序决胜」补成「先挂的赢 + `anthropic-version` 头放行」的组合，并说明 proxy 版处理完即结束响应、不 `next()`（proxy.ts:317 handler 签名无 `next` 参数）

C  文档:291-340  §12 源码索引同步：app.ts 三行（挂载序列 206-334 / admin 21+2 / 内联 ping 279-281）、rateLimit 16/91、proxy 新增端点行与 `handleDecision`/`completionPromptToMessages`/multer、media+embeddings+rerank+search 的 service 函数行号、mcp 三行（656-666 门、427-573 工具、676/700/703 路由）、settings/search/decisions/health 四张 admin router、fallback-loop（1348/69/172/183/842-864/905）、inbound-chat（51/165/228）、header-value（38/53）、served-model（61/17）、router.ts:84、cli tools 1037-1058/1060-1080、config-files 348-356/409-416、index.ts 双查与命令派发、types.ts 63-266、Dockerfile 83-84 与 docker-compose.yml 41

## SKIP

SKIP 文档:237  fallback-loop.ts:2-17 头注释里的「三面曾各有 ~150 行 / 三类漂移 bug」是对**注释内容**的转述，上一轮已实测注释块恰为 2-17；本轮不改写（RULES2 的「不写历史叙述」约束的是我们新增的叙述，不是引用源码注释）
SKIP 文档:221  「同一 `routeRequest/streamChatCompletion` 内核服务 5 种入口协议」：`routeRequest`=services/router.ts:2152、`chatCompletion`/`streamChatCompletion`=base.ts:238/246 均存在，断言成立，保留
SKIP 文档:286（§11 第 3 行）、287（第 4 行）  前一行是 §3 已复核的挂载共存事实、后一行引 docs/en/architecture 的产品口径；本轮未测 docs 侧文本，不动
SKIP 文档:255-263（§9）  `summarizeExhaustion`=services/router.ts:84 的九个桶逐条数过（unsupported provider / no usable key configured / prompt too large / model lacks vision / model lacks tool-calling / cannot honor response_format / failed earlier this request / rate-limited or on cooldown / unavailable = 9）→「九桶摘要」成立；client/src/lib/api.ts:44-53 的 `type==='authentication_error'` 判定在 50 行，`lib/error-redaction.ts` 存在；无过期断言可改

## 推翻 report-05 / RULES2 清单的条目

1. 推翻 report-05 的 `OK L179 tools.ts:1037-1080`：锚点没错，但正文「21 个 agent」错。实测 metadata 是 20 个元组、20 个生成器函数、20 个 `setup-*` 命令，`tools = metadata.map`=1060-1080。report-05 自己在 SEMANTIC 附注里也写了「21-agent 元数据」，属同源过期计数。
2. 推翻 report-05 的 `OK L115 status.ts:41`：行号确实对，但同行正文声称 livez 是「Docker HEALTHCHECK 的目标」——Dockerfile:83-84 与 docker-compose.yml:41 打的都是 `/api/ping`。这条属于报告只查锚点没查语义的漏网。
3. 推翻 report-05 的 `OK 其他 L195 lib/header-value.ts、lib/served-model.ts 均存在`：文件存在，但正文写出的两个头名 `X-Execution-Id`、`Routed-Model` 在全仓 `setHeader` 名字集合里 0 命中；`observeServedModel` 也不写头。
4. 推翻 report-05 的 `SEMANTIC: L124-147 缺 /api/search 与 /api/decisions`「锚点范围 246-276 已覆盖它们」这一句的够用判断：范围覆盖不等于清单完整，且真实缺失不止两条——§0 树里还漏了 app.ts:215-218 这条 ollama limiter 挂载与 279-281 的内联 ping，`/api/keys/export` 那行写法（`app.use('/api/keys/export', EXPORT_RATE_LIMIT_RPM)`）也和源码 `createAdminRateLimiter(EXPORT_RATE_LIMIT_RPM)` 不符。
5. 推翻 report-05 的 `FIXED L155 -> 未动正文数字` 隐含口径：正文的「33」既不是 register 调用数也不是 class 数；同时** RULES2 事实表的「Platform 联合成员 74 / provider 注册调用 73」需要加一条口径警告**：73-74 的缺口是 `'sambanova'`（类型成员保留、无 provider 实例），不是 `'custom'`——`'custom'` 在 index.ts:616-620 有占位单例，真正的多实例语义在 `resolveProvider`（632-648）里现场构造。
6. 测量命令警告（给后续轮次）：`Platform` 联合计数不能用「首个以 `;` 结尾的行」做终止条件——注释里大量出现 `;`（如 types.ts:88「…without a top-up;」），朴素正则在第 13 个成员就截断。本会话实测：错误口径 → 13，剥注释后 → 74。
7. 补充口径（RULES2 事实表没有的）：`ADMIN_DEFAULT_RPM = 600` 在 rateLimit.ts:**91**（90 行是它的说明注释），写文档时按 90 会错位。
