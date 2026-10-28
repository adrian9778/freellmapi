# 05 API 与接口设计

> 第四层 · 第 2 篇。`/v1` wire 面、`/v1beta` Gemini 原生面、Ollama 面、MCP 面、`/api/*` Dashboard 管理面、运维探针面的全量接口清单 + 认证分界 + 跨面契约。

---

## 0 一张路由挂载总图（`app.ts:206-334`，全部经源码核实）

```
app.ts 挂载顺序（顺序即优先级，与源码逐行对齐，无省略项）
  app.use(clientContextMiddleware)                         :206
  app.use([ollama 的 7 条精确 /api/* 路径], createProxyRateLimiter) :215-218
  app.use(ollamaRouter)                                    :219   ← 在 admin 门之前
  app.use('/api', adminRateLimiter)                        :233
  app.use('/api/auth', authRouter)                         :238   ← 唯一免 requireAuth 的 router（登录入口）
  app.use('/api/keys/export', createAdminRateLimiter(EXPORT_RATE_LIMIT_RPM)) :244 ← 密码暴破上限 10/min
  app.use('/api/keys', requireAuth, keysRouter)            :246
  app.use('/api/client-profiles', requireAuth, clientProfilesRouter) :250
  app.use('/api/conversations', requireAuth, conversationsRouter)    :253
  app.use('/api/logs', requireAuth, logsRouter)            :257
  app.use('/api/models', requireAuth, modelsRouter)        :258
  app.use('/api/profiles', requireAuth, profilesRouter)    :259
  app.use('/api/fallback', requireAuth, fallbackRouter)    :260
  app.use('/api/embeddings', requireAuth, embeddingsRouter):261
  app.use('/api/media', requireAuth, mediaRouter)          :262
  app.use('/api/search', requireAuth, searchRouter)        :263
  app.use('/api/decisions', requireAuth, decisionsRouter)  :264
  app.use('/api/analytics', requireAuth, analyticsRouter)  :265
  app.use('/api/health', requireAuth, healthRouter)        :266
  app.use('/api/free-tier', requireAuth, freeTierRouter)   :267
  app.use('/api/settings', requireAuth, settingsRouter)    :268
  app.use('/api/premium', requireAuth, premiumRouter)      :269
  app.use('/api/backups', requireAuth, backupsRouter)      :273
  app.use('/api/cache', requireAuth, cacheRouter)          :274
  app.use('/api/compression', requireAuth, compressionRouter) :275
  app.use('/api/update', requireAuth, updateRouter)        :276
  app.get('/api/ping', inline handler)                     :279-281 ← 无鉴权、非 router
  app.use('/v1', docsRouter)                               :287   ← /v1/openapi.json, /v1/docs
  app.use('/v1', providersRouter)                          :293   ← /v1/providers, /v1/quota-forecast
  app.use('/v1/t/:token', createProxyRateLimiter(...))     :296
  app.use('/v1/t/:token', urlTokenRouter)                  :297   ← URL 内嵌凭证（媒体类客户端）
  app.use('/v1', createProxyRateLimiter(...))              :302
  app.use('/v1', anthropicRouter)                          :308
  app.use('/v1', proxyRouter)                              :309
  app.use('/v1', moderationRouter)                         :311
  app.use('/v1', responsesRouter)                          :313
  app.use('/v1beta', createProxyRateLimiter(...))          :316
  app.use('/v1beta', geminiRouter)                         :317
  app.use('/mcp', createProxyRateLimiter(...))             :324
  app.use('/mcp', mcpRouter)                               :325
  app.use(statusRouter)                                    :331   ← /livez /readyz（无认证无限流）
  app.use(errorHandler)                                    :334
```

`docsRouter`（:287）与 `providersRouter`（:293）刻意挂在线 limiter 之前：两者只拥有各自那两条只读路径，探活与文档轮询不扣调用方的请求预算。

**两套限流器**（`middleware/rateLimit.ts`）：`createProxyRateLimiter` 默认 120 RPM/IP（`DEFAULT_RPM`=rateLimit.ts:16，`PROXY_RATE_LIMIT_RPM` 可调、0 关闭）挂 wire 面与 ollama 面；`createAdminRateLimiter` 默认 600 RPM/IP（`ADMIN_DEFAULT_RPM`=rateLimit.ts:91）挂 `/api`；export 路由再叠一层更严的 10/min（`EXPORT_RATE_LIMIT_RPM`=app.ts:43）。

---

## 1 `/v1` OpenAI 兼容面（`routes/proxy.ts` 等，逐条核实）

| 方法 | 路径 | 锚点 | 说明 |
|------|------|------|------|
| GET | `/v1/models` | proxy.ts:317 | 列表；`?available=true` 只回当前可服务的（`available` = enabled 且有 enabled key 能服务它）。查询参数接受 `available`/`connected`/`ready` 三个别名，值 `1`/`true`/`yes`（proxy.ts:337-338）；CLI 双查区分「不存在」vs「耗尽」（见 §8） |
| POST | `/v1/chat/completions` | proxy.ts:1643 | 主入口。`model:"auto"` 或省略 = 自动路由；`auto:` 前缀同样算 auto（`isAutoModel`=proxy.ts:53-57，注释起于 47） |
| POST | `/v1/completions` | proxy.ts:1232 | legacy 补全：`prompt`/`suffix` 经 `completionPromptToMessages`（proxy.ts:1175，调用点 1259）翻成 messages 走同一条 chat 链路，响应回写为 `object:'text_completion'` 形态（proxy.ts:1217、1571）；`max_tokens` 缺省 128（proxy.ts:1255-1256） |
| POST | `/v1/embeddings` | proxy.ts:680 | → `services/embeddings.ts:runEmbeddings`（embeddings.ts:384） |
| POST | `/v1/rerank` | proxy.ts:715 | → `services/rerank.ts:runRerank`（rerank.ts:89；非 OpenAI 标准，cohere 风格） |
| POST | `/v1/images/generations` | proxy.ts:925 | → `services/media.ts:runImageGeneration`（media.ts:849） |
| POST | `/v1/videos/generations` | proxy.ts:963 | → `runVideoGeneration`（media.ts:888） |
| POST | `/v1/audio/speech` | proxy.ts:1019 | TTS；→ `services/media.ts:runSpeech`（media.ts:1226） |
| POST | `/v1/audio/transcriptions` | proxy.ts:1068 | STT；multer 内存上传（proxy.ts:1059 `limits:{fileSize:MAX_TRANSCRIPTION_BYTES, files:1}`），上限常量 `MAX_TRANSCRIPTION_BYTES`=media.ts:962（25 MiB）；→ `runTranscription`（media.ts:1181） |
| POST | `/v1/search` | proxy.ts:755 | 网页检索（#1174）；→ `services/search.ts:runSearch`（search.ts:483），可按 `engine` 指定引擎 |
| GET | `/v1/search/engines` | proxy.ts:799 | 可 pin 的检索引擎列表；→ `listSearchEngines`（search.ts:597） |
| POST | `/v1/decisions` | proxy.ts:876 | 结构化决策；与 `/v1/systemone` 同为 `handleDecision`（proxy.ts:835）→ `services/decision.ts:runDecision` |
| POST | `/v1/systemone` | proxy.ts:877 | `/v1/decisions` 的别名注册 |
| GET | `/v1/decisions/models` | proxy.ts:880 | 可 pin 的决策模型列表；→ `listDecisionModels` |
| POST | `/v1/moderations` | moderation.ts:25 | #1155 |
| POST | `/v1/responses` | responses.ts:657 | OpenAI Responses API 形态（后台任务/流式事件） |
| POST | `/v1/messages` | anthropic.ts:456 | **Anthropic Messages 协议**，同一 router 复用 |
| POST | `/v1/messages/count_tokens` | anthropic.ts:1125 | Anthropic 计费预估 |
| GET | `/v1/models` (anthropic 形态) | anthropic.ts:1164 | 与 proxy 的 GET /models 同路径；靠请求头 `anthropic-version` 决胜，缺头即 `next()` 落回 proxyRouter（anthropic.ts:1165） |
| GET | `/v1/providers` | status.ts:112 | 按 provider 汇总的健康/配额视图 |
| GET | `/v1/quota-forecast` | status.ts:221 | `services/quota-forecast.ts` 预测配额耗尽时间 |
| GET | `/v1/openapi.json` `/v1/docs` | docs.ts:14,20 | 内嵌 OpenAPI 文档 |
| * | `/v1/t/:token/*` | services/url-tokens.ts + routes/url-tokens.ts | 短期 URL 令牌（图片等无法带 header 的场景） |

### 1.1 Anthropic 双面共存的一个细节

`GET /v1/models` 有**两个 handler**（proxy.ts:317 与 anthropic.ts:1164），挂载顺序 anthropic 在前（app.ts:308 vs 309）。决胜靠请求头而非鉴权头：anthropic 版第一件事就是 `if (!req.headers['anthropic-version']) return next();`（anthropic.ts:1165），OpenAI 客户端不带这个头即落回 proxyRouter；带 `anthropic-version` 的 Claude 系 SDK 命中 anthropic 版，拿到 `type:'model'` + `display_name` 的 Anthropic 家族形态。`claudeFamilyDiscoveryEntries`（`services/anthropic-map.ts`，调用点 anthropic.ts:1176）负责把内部模型 id 映射成 Claude 风格 id，且只在有模型真正可服务时才追加这些条目；额外别名是否暴露由设置项 `expose_cc_discovery_aliases` 控制（anthropic.ts:1170）。

### 1.2 认证统一（三头一验）

```
extractApiToken()  proxy.ts:78-92
  Authorization: Bearer …   → OpenAI 习惯
  x-api-key: …              → Anthropic SDK
  x-goog-api-key: …         → Gemini SDK
  ↓
resolveAuth()  lib/system-prompt.ts
  统一 key (settings.unified_api_key, 'freellmapi-'+48hex)
  或 client-profile key（可携带服务端强制 system prompt；#411：profile key 只在 /v1 有效，永不接受于 /api）
```

---

## 2 `/v1beta` Gemini 原生面（`routes/gemini.ts`）

| 方法 | 路径 | 锚点 |
|------|------|------|
| GET | `/v1beta/models` | gemini.ts:80 |
| GET | `/v1beta/models/<id>` | gemini.ts:95（正则路由） |
| POST | `/v1beta/models/<id>:generateContent` | gemini.ts:227 |
| POST | `/v1beta/models/<id>:streamGenerateContent` | gemini.ts:229 |
| POST | `/v1beta/models/<id>:countTokens` | gemini.ts:231 |

`<id>` 支持 `models/gemini-2.5-flash` 与 `auto`；wire↔内部翻译在 `services/gemini-map.ts` + `lib/gemini-wire.ts`。

---

## 3 Ollama 原生面（`routes/ollama.ts`，挂在根路径）

| 方法 | 路径 | 锚点 |
|------|------|------|
| GET | `/api/tags` | ollama.ts:96 |
| GET | `/api/version` | ollama.ts:119 |
| POST | `/api/show` | ollama.ts:127 |
| POST | `/api/chat` | ollama.ts:386 |
| POST | `/api/generate` | ollama.ts:501 |
| POST | `/api/embed` | ollama.ts:595 |
| POST | `/api/embeddings` | ollama.ts:602（legacy） |

**注意与 `/api/*` admin 面的路径共存**：这 7 条精确路径先过一层 proxy limiter（`app.use(['/api/tags','/api/version','/api/show','/api/chat','/api/generate','/api/embed','/api/embeddings'], createProxyRateLimiter(cfg.proxyRateLimitRpm))`=app.ts:215-218），再挂 `ollamaRouter`（app.ts:219）——挂载注释给出的理由是「key-required 模式没有这层就是个可暴破的凭证检查」。ollamaRouter 只拥有上面这 7 条精确路径，其余 `/api/*` 继续落到 `adminRateLimiter`（app.ts:233）+ 逐条 `requireAuth` 的 admin 面（app.ts:238-276，见 §6）；其 legacy `/api/embeddings`（ollama.ts:602）在识别到合法 dashboard session 时显式 `next()` 放行，好让 dashboard 与 Ollama 客户端共用这一条路径。

---

## 4 MCP 面（`routes/mcp.ts`）

三条注册在 `mcpRouter` 上的路由（`grep -n "mcpRouter\.\(get\|post\|delete\|put\)" server/src/routes/mcp.ts` 实测只有这三条）：

| 方法 | 路径 | 锚点 | 行为 |
|------|------|------|------|
| POST | `/mcp` | mcp.ts:676 | JSON-RPC 单消息入口。数组批次直接 400 `-32600`；`tools/list`、`tools/call`、`initialize`、`ping` 走 `handleRpc`；通知（无返回）回 202 |
| GET | `/mcp` | mcp.ts:700 | 恒 405 + `-32000`「This MCP server is stateless」：stateless 服务端不开了服务器主动推的流 |
| DELETE | `/mcp` | mcp.ts:703 | 恒 405 + `-32000`「there is no session to delete」：没有会话可销毁 |

工具目录是固定的 13 个内省工具（`TOOLS`=mcp.ts:427-573），不是「可用模型」：`ask_freellmapi`、`healthcheck`、`list_models`、`provider_health`、`usage_summary`、`routing_info`、`set_routing_strategy`、`cache_stats`、`web_search`、`compression_stats`、`provider_list`、`clear_cache`、`quota_outlook`。

开关是 settings 表里的键 `enable_mcp`（常量 `MCP_ENABLED_SETTING`=mcp.ts:656），由 migration `20260903_000001_mcp_enabled_default.ts` 播种：升级时库里已有 provider key 的装默认 `1`（保持原有无条件开启），空库新装默认 `0`；已有值不覆盖。读它是每请求一次的 `isMcpServerEnabled()`（mcp.ts:658），改完不需重启。门开在 router 级、覆盖所有动词（`mcpRouter.use`=mcp.ts:666）：关闭时 POST/GET/DELETE 一律 403 + `-32000`，且该门跑在鉴权之前，免得 disabled 状态反过来给探测者提示 key 是否有效。打开路径是 Dashboard 的 Keys → Agent compatibility，或 `PUT /api/settings/enable-mcp`（settings.ts:147，配套 GET 在 141）。

---

## 5 运维探针面（`routes/status.ts`，无鉴权无限流）

| 路径 | 锚点 | 返回 |
|------|------|------|
| GET `/livez` | status.ts:41 | 存活。查 `isDbReachable()` + `isEncryptionKeyInitialized()`：全通过回 200 `{status:'ok', version, uptime_s}`（status.ts:57），否则 503 且多带 `checks:{db, encryption_key}`（status.ts:48-53）——CLI doctor 的目标（doctor.ts:303-310 的 `probeGateway` 打 `${baseUrl}/livez`） |
| GET `/readyz` | status.ts:64 | 就绪。DB 可达后看「至少一个上游此刻可服务」（enabled 且 status 为 healthy/unknown 的 platform 数 > 0），200 回 `{status:'ok', ready_upstreams}`（status.ts:81）；503 回机器可读 `reason`，四取值 `db_unreachable`（66）/ `no_upstreams_configured`（89）/ `all_upstreams_rate_limited`（91）/ `all_upstreams_unhealthy`（93），出口在 96 |

Docker 的探活打的不是这两条：`Dockerfile:83-84` 的 `HEALTHCHECK` 与 `docker-compose.yml:41` 都 `fetch('http://127.0.0.1:<port>/api/ping')`。`/api/ping` 的 handler 内联在 `app.ts:279-281`（`app.get('/api/ping', ...)`，函数体只有一行 `res.json({ status:'ok', timestamp:new Date().toISOString() })`），不属于 `healthRouter`：后者（routes/health.ts）只注册 `GET /`（13）、`POST /check/:keyId`（64）、`POST /check-all`（78）、`POST /quota/:keyId`（89），全部挂在 `/api/health` 前缀下且都要 `requireAuth`。`/api/ping` 无 `requireAuth`（app.ts:278 注释「Health check — no auth required」），但仍走 :233 那层 `/api` admin limiter——这正是 admin 面注释声明的设计：鉴权按子路径逐个 gate，限流器宽宽地罩住整个 `/api`。

---

## 6 `/api/*` Dashboard 管理面（router 全部 `requireAuth`，session token 认证）

挂载清单（`grep -n "app.use('/api" server/src/app.ts` 实测 23 条：21 条带 router、2 条只挂 limiter；右侧为 app.ts 行号）：

```
/api/auth            authRouter              :238   登录/注册/session（唯一免 requireAuth 的 router）
/api/keys/export     createAdminRateLimiter(EXPORT_RATE_LIMIT_RPM) :244  只加限流，路由本身在 keysRouter
/api/keys            keysRouter              :246   provider keys CRUD、批量导入(.env 粘贴+预览+逐键选择)、
                                                    导出(json/.env/csv，密码门 + 10/min)、per-key 代理、模型发现
/api/client-profiles clientProfilesRouter    :250   profile key（带强制 system prompt 的发行 key）
/api/conversations   conversationsRouter     :253   Playground 会话持久化
/api/logs            logsRouter              :257   请求日志查询
/api/models          modelsRouter            :258   模型目录 CRUD/override/tombstone/权重
/api/profiles        profilesRouter          :259   fallback profile 管理
/api/fallback        fallbackRouter          :260   主链编辑 + 路由策略 GET/PUT /api/fallback/routing（fallback.ts:34、98）
/api/embeddings      embeddingsRouter        :261   嵌入模型管理
/api/media           mediaRouter             :262   图像/音频/视频模型管理
/api/search          searchRouter            :263   Models → Search 页（#1174）：GET /engines（search.ts:11）、
                                                    PATCH /engines/:id（22）改 enabled/priority
/api/decisions       decisionsRouter         :264   Models → Decision 页：GET /models（decisions.ts:11）、
                                                    PATCH /models/:id（17）、POST /try（43）
/api/analytics       analyticsRouter         :265   统计聚合（延迟分位索引 migration 20260902_000001）
/api/health          healthRouter            :266   GET /（health.ts:13）、POST /check/:keyId（64）、
                                                    POST /check-all（78）、POST /quota/:keyId（89）
/api/free-tier       freeTierRouter          :267   免费额度全景视图
/api/settings        settingsRouter          :268   全局设置；含 MCP 开关 PUT /api/settings/enable-mcp（settings.ts:147）
/api/premium         premiumRouter           :269   Premium 订阅/激活/live catalog
/api/backups         backupsRouter           :273   DB 备份 CRUD/恢复
/api/cache           cacheRouter             :274   响应缓存管理
/api/compression     compressionRouter       :275   提示压缩管线配置
/api/update          updateRouter            :276   自更新（docker watchtower 触发 / 桌面端配合）
/api/ping            内联 app.get            :279-281  无鉴权（见 §5），不是 router
```

21 条 router 挂载里只有 `/api/auth`（:238）不带 `requireAuth`（另 20 条全部带）；`/api/ping` 压根不挂 router。剩下的 `:233`（`app.use('/api', adminRateLimiter)`）与 `:244`（export 的独立 limiter）是两条纯限流挂载，先于以上全部，覆盖含 `/api/ping` 在内的整个 `/api` 前缀。Ollama 面那 7 条精确 `/api/*` 路径在 :215-219 抢先命中，永远不会走到这张表（见 §3）。

**认证模型**：`users(email+password_hash)` → `sessions(token_hash 主键, expires_at_ms)`（legacy_baseline.ts:161-173）。首次启动 `userCount()===0` 时铸一次性 setup code 并打印（index.ts:70-72）：loopback 浏览器可免 code 完成 setup，远程调用必须带 code。

---

## 7 Provider 契约（跨面共享的抽象，`providers/base.ts`）

注册表本体是 `const providers = new Map<Platform, BaseProvider>()`（providers/index.ts:45）+ `function register(provider)`（index.ts:47-49，按 `provider.platform` 一键一实例）。下面几个计数口径各不相同，别混成一句：

| 口径 | 数值 | 测量命令（HEAD 实测） |
|------|------|----------------------|
| `register()` 调用 = 注册进 Map 的单例数 | 73 | `grep -cE '^\s*register\(' server/src/providers/index.ts` → 73；首尾分布在 index.ts:54-620（末条 616-620 是 `'custom'` 占位实例），全部顶层逐条调用、无循环批量注册 |
| `Platform` 联合成员数 | 74 | `shared/types.ts:63-266` 的 `export type Platform`，只数行首 `|` 后的字面量（注释里的 `;` 会截断朴素正则） |
| `class *Provider` 定义数（去重） | 43 | `grep -rhoE 'class [A-Za-z0-9_]+Provider' server/src/providers/*.ts \| sort -u \| wc -l` → 43 |
| 直接 `new OpenAICompatProvider` 实例化数 | 34 | `grep -c 'new OpenAICompatProvider' server/src/providers/index.ts` → 34 |
| `server/src/providers/*.ts` 文件数 | 44 | `ls server/src/providers/*.ts \| wc -l` → 44 |

73 vs 74 的差额只有一个：`'sambanova'`（types.ts:131）作为类型成员还留在联合里，`providers/index.ts` 已不为它注册实例（该目录里 `grep -rn sambanova` 无命中）。反过来 73 个注册实例的 platform 全部落在这 74 个成员之内。类型侧的 43 个 class 少于 73 个实例，是因为 `OpenAICompatProvider` 一个类被 34 处 `new` 用不同 `{platform,name,baseUrl}` 复用，其余平台才有自己的子类（如 `SpekaProvider` 也只是 `extends OpenAICompatProvider` 后在 `super()` 里钉 platform 并覆写 `validateKey`）。

`BaseProvider`（base.ts:229）的契约形状：抽象成员 5 个 —— 属性 `platform`（230）、`name`（231），方法 `chatCompletion`（238）、`streamChatCompletion`（246）、`validateKey`（254）；带默认实现、子类可选覆盖的 3 个 —— `fetchQuota`（266，配额探针，默认 `false`）、`hasQuotaProbe`（274）、`supportsKeyValidation`（285，默认 `true`）；另有非抽象字段 `keyless`（236，默认 `false`，免 key 平台用）。详见 [04](04-核心模块与类关系.md) §2。

**wire 形态 × 面 的复用矩阵**——同一 `routeRequest/streamChatCompletion` 内核服务 5 种入口协议：

```
                      ┌─ proxy.ts       OpenAI Chat / legacy Completions
                      ├─ responses.ts   OpenAI Responses
  anthropic.ts ───────┤  三面各自只做「请求翻译 → routeRequest → provider.chatCompletion/
                      │  streamChatCompletion → 响应翻译回 SSE(event)」，
  gemini.ts ─────────►│  重试/cooldown/预算记账一律交给 runFallbackLoop（lib/fallback-loop.ts:1348）
  ollama.ts ─────────►┘  调用点：proxy.ts:1366（legacy /completions）、proxy.ts:2300（/chat/completions）、
                         anthropic.ts:681、responses.ts:1172
```

`gemini.ts` 与 `ollama.ts` 这两个非 OpenAI 入站协议再多走一层：它们的 wire 翻译层调用 `runInboundChat`（`lib/inbound-chat.ts`:165，入站形态是 `InboundChatRequest`，同文件 51；调用点 gemini.ts:199、ollama.ts:411、531），由它去驱动同一个 `runFallbackLoop`（inbound-chat.ts:228）。文件里 159-163 的注释把这层定位说得很直白：协议路由负责校验与 wire 翻译，`runInboundChat` 负责「与既有 OpenAI/Anthropic/Responses 面相同的 routing、retry、cooldown、accounting、pinning、disconnect」。

所以五个面共享的记账常量只有一份：`FALLBACK_MAX_RETRIES = 20`（fallback-loop.ts:69）与 `DEFAULT_FALLBACK_TIME_BUDGET_MS = 45_000`（fallback-loop.ts:172，`getFallbackTimeBudgetMs`=183 读取）。

fallback-loop 头注释（fallback-loop.ts:2-17）披露了这个设计的由来：三个面曾各有 ~150 行手工复制的 attempt loop，**已经漂移出三类 bug**（同一个 403 三个面 bench 一天、/v1/responses 只 bench 90s；exhaustion 体三个面回 400、messages 面恒 429；Retry-After 唯独 /v1/responses 不遵守）。收敛后各面只留薄 `dispatch` 翻译层。

---

## 8 CLI 契约（`cli/src/`，纯 HTTP，无 import server）

| CLI 命令 | 打到哪里 | 认证 |
|----------|----------|------|
| `setup-<tool>`（20 个，见下）/ `launch` / `launch-codex` | 只读 `GET /v1/models?available=true` + `GET /v1/models`（双查区分不存在 vs 耗尽，`catalog`=index.ts:162-187、`catalogs`=index.ts:209-220） | `FREELLMAPI_API_KEY`（Bearer） |
| `keys add/list/remove/test`（四选一派发，keys.ts:73） | `GET /api/keys`（119）、`POST /api/keys`（150）、`DELETE /api/keys/{id}`（176）、`POST /api/health/check/{id}`（128）、`GET /api/keys/providers`（141）、`GET /api/models`（162）（keys.ts:118-176） | `FREELLMAPI_DASHBOARD_TOKEN`（session） |
| `doctor` | `GET {url}/livez`（doctor.ts:303-345 的 `probeGateway`） | 无 |

「agent 数」的可复跑口径：CLI 的工具清单是 `metadata` 这 20 个元组（tools.ts:1037-1058，`grep -c "^  \['" ` 实测 20），`export const tools = metadata.map(...)`（tools.ts:1060-1080）把第 7 项 `command` 变成命令名，所以 20 个 `setup-*` 一一对应 20 个生成器函数（`grep -cE ': GenerateContext\): Generation' cli/src/tools.ts` → 20：claude、codex、cline、continueDev、aider、opencode、goose、qwen、roo、kilo、crush、dsh、mimo、atomcode、openclaw、hermes、pi、reasonix、cursor、generic）。顶层命令面则是这 20 个 `setup-*` 再加 `keys`（index.ts:470）、`list`（478）、`doctor`（488）、`launch`（489）、`launch-codex`（490）、`help`（457）。`configType` 第 4 项区分 `file`（真写配置文件）与 `guide`（只出步骤，cursor 与 generic）。

**配置文件写入契约**（tools.ts:1037-1080 + config-files.ts:409-416）：`renderFile`（config-files.ts:348）按 `file.format` 四路分发（349-356）——JSON deep-merge（`mergeJson`=18）、YAML 结构化 merge 保注释与键序（`mergeYamlDocument`=67、`mergeYaml`=193、Continue 专用 `mergeContinueYaml`=153）、TOML 按表分块 merge（`mergeToml`=277）、ENV 按 key 原地替换再追加缺失项（`mergeEnv`=322）。`applyGeneratedFiles`（409）是两阶段：先把所有目标读完并 merge 完才落第一笔写，任一文件 merge 失败即整批中止；每文件写前 `copyFileSync` 出 `.backup-<timestamp>`（396-397），临时文件写完 `renameSync`（400-401），`sensitive` 文件 mode `0o600`（400、402），父目录 `0o700`（393）。

---

## 9 错误响应契约（全 wire 面统一）

```jsonc
{ "error": { "message": "...", "type": "authentication_error | rate_limit_exceeded | routing_error | invalid_request_error", "code": null } }
```

- 401 语义纪律：client 端只在 `type==='authentication_error'` 时清 session（client/src/lib/api.ts:44-53）——provider key 坏掉的 401 不得把用户登出
- 429 exhaustion：body 携带 `summarizeExhaustion()` 的九桶摘要 + `Retry-After`（`setExhaustionHeaders`，fallback-loop）
- 错误文本经 `lib/error-redaction.ts` 消毒，绝不回显上游 key/内部 URL

## 10 响应头契约

按源码里真实出现的 `res.setHeader(...)` 名字列（`grep -rhoa "setHeader('[^']*'" server/src --exclude="*.test.ts"` 实测）：

- `X-Routed-Via`：值由 `routedViaValue(platform, modelId)`（`lib/header-value.ts`:53）生成、`safeHeaderValue`（同文件 38）截断+消毒；缓存命中回 `cache`（proxy.ts:2082、2094）、幂等命中回 `idempotency`（proxy.ts:2130）。
- `X-Request-ID`：execution id 的头载体（proxy.ts:1235、1646，responses.ts:665），错误体里的同值是 `execution_id` 字段。
- `X-Fallback-Attempts` / `X-Fallback-Trail` / `X-Fallback-Detail`：`setFallbackHeaders`（fallback-loop.ts:842-864）；trail/detail 分别受 `TRAIL_HEADER_MAX_LENGTH`=1024、`DETAIL_HEADER_MAX_LENGTH`=2048 约束，最多展示 10 跳（`TRAIL_MAX_SHOWN`=747）。
- `X-FreeLLM-Cache`（`HIT`/`MISS`/`OFF`，proxy.ts:2083、2426）、`X-FreeLLM-Compress`（proxy.ts:1803、anthropic.ts:520）、`X-FreeLLM-Routing-Strategy`（proxy.ts:2298、anthropic.ts:679）：缓存/压缩/bandit 策略的可观测回写。
- `X-Provider` + `X-Model`：媒体类端点直接回写路由结果（proxy.ts:995-996、1135-1136）。
- `Retry-After` + `X-RateLimit-Limit/Remaining/Reset`：两层 limiter 各写一份（rateLimit.ts:60-66 为 proxy 面、127-133 为 admin 面），429 exhaustion 路径也带 `Retry-After`（见 §9）。

`served-model` 不参与响应头：网关把上游返回的 `model` 字段改写为「被路由到的那个 id」后对外发出，`observeServedModel`（`lib/served-model.ts`:61）拿的是改写前捕获的原始上游值，只产出两样东西——每 `(platform, requested, served)` 元组每进程一次的 `[ServedModel]` 结构化 warn（注释所述见 served-model.ts:13-14），以及给 `requests.served_model` 落库的字符串（匹配则 NULL，served-model.ts:15-16）。该文件头注释第 17 行写明「The response contract is untouched: callers keep seeing the routed model.」，即这条观测链只进日志与 `requests` 表，不碰任何响应头。

---

## 11 已知缺口 / 待拍板

| # | 级别 | 描述 |
|---|------|------|
| 1 | 已核实 + 风险 | `/api/ping` 归属已确认：内联 `app.get` 于 app.ts:279-281，非 healthRouter（见 §5）。残留风险是该 handler 无条件 `res.json({status:'ok', timestamp})`，不查 DB 也不查 key，Docker HEALTHCHECK 只要进程能应答就判健康——真正的依赖检查在 `/livez`（status.ts:42-43）与 `/readyz`（status.ts:65、71-96），两条都没被容器用到 |
| 2 | 风险 | `GET /v1/models` 双 handler 靠「先挂的赢 + `anthropic-version` 头放行」这套组合决胜（app.ts:308 先于 309，见 §1.1）。把 proxyRouter 挪到 anthropicRouter 之前就会翻转：proxy 版处理完即结束响应、不 `next()`，Anthropic SDK 再也拿不到家族形态 |
| 3 | 设计特性 | `/api/*` 与 Ollama `/api/*` 同前缀共存，靠先挂 ollamaRouter 解决——新人读挂载表易误判 |
| 4 | 风险 | n>1 多补全、多租户计费在 high-level-index 明示「未支持」；看到 README 之外有人实现需求应先对齐 |

---

## 12 源码索引

| 文件 | 符号 | 行号 |
|------|------|------|
| server/src/app.ts | 挂载序列 | 206-334 |
| server/src/app.ts | 21 条 admin router 挂载 + 2 条纯 limiter 挂载 | 233、238、244、246、250、253、257-269、273-276 |
| server/src/app.ts | 内联 `/api/ping` handler（无鉴权） | 279-281 |
| server/src/app.ts | `EXPORT_RATE_LIMIT_RPM = 10` | 43 |
| server/src/middleware/rateLimit.ts | `DEFAULT_RPM = 120` / `ADMIN_DEFAULT_RPM = 600` | 16 / 91 |
| server/src/routes/proxy.ts | `proxyRouter` 全部端点 | 317-1643 |
| server/src/routes/proxy.ts | `/search` `/search/engines` `/decisions` `/systemone` `/decisions/models` | 755、799、876、877、880 |
| server/src/routes/proxy.ts | `handleDecision` / `completionPromptToMessages` / multer limits | 835 / 1175 / 1059 |
| server/src/services/media.ts | `MAX_TRANSCRIPTION_BYTES` / `runImageGeneration` / `runVideoGeneration` / `runSpeech` / `runTranscription` | 962 / 849 / 888 / 1226 / 1181 |
| server/src/services/embeddings.ts | `runEmbeddings` | 384 |
| server/src/services/rerank.ts | `runRerank` | 89 |
| server/src/services/search.ts | `runSearch` / `listSearchEngines` | 483 / 597 |
| server/src/routes/responses.ts | `/responses` | 657 |
| server/src/routes/anthropic.ts | `/messages` 群 | 456-1164 |
| server/src/routes/anthropic.ts | `GET /models` 的 `anthropic-version` 决胜 + 别名开关 | 1165 / 1170 / 1176 |
| server/src/routes/gemini.ts | `/v1beta/models…` | 80-231 |
| server/src/routes/ollama.ts | Ollama 端点群 | 96-602 |
| server/src/routes/mcp.ts | `MCP_ENABLED_SETTING` / `isMcpServerEnabled` / 全动词门 `mcpRouter.use` | 656 / 658 / 666 |
| server/src/routes/mcp.ts | `TOOLS` 工具目录（13 个） | 427-573 |
| server/src/routes/mcp.ts | `POST /` `GET /` `DELETE /` | 676、700、703 |
| server/src/routes/settings.ts | `GET` / `PUT` `/enable-mcp` | 141 / 147 |
| server/src/routes/search.ts | `GET /engines` `PATCH /engines/:id` | 11 / 22 |
| server/src/routes/decisions.ts | `GET /models` `PATCH /models/:id` `POST /try` | 11 / 17 / 43 |
| server/src/routes/health.ts | `GET /` `POST /check/:keyId` `POST /check-all` `POST /quota/:keyId` | 13 / 64 / 78 / 89 |
| server/src/routes/moderation.ts | `/moderations` | 25 |
| server/src/routes/status.ts | `/livez` `/readyz` `/providers` `/quota-forecast` | 41-221 |
| server/src/routes/status.ts | livez 200 体 / readyz 200 体 / 4 个 `reason` | 57 / 81 / 66、89、91、93 |
| server/src/routes/docs.ts | openapi/docs | 14-20 |
| server/src/providers/index.ts | `providers` Map / `register()` | 45 / 47-49 |
| server/src/providers/index.ts | 73 处 `register()` 调用分布（末条 `'custom'` 占位在 616-620） | 54-620 |
| server/src/providers/base.ts | `BaseProvider` 抽象 5 + 可选覆盖 3 + `keyless` / `CompletionOptions` | 229-285 / 163 |
| server/src/lib/inbound-chat.ts | `InboundChatRequest` / `runInboundChat` / 其内的 `runFallbackLoop` 调用 | 51 / 165 / 228 |
| server/src/lib/fallback-loop.ts | 双面漂移历史注释 | 2-17 |
| server/src/lib/fallback-loop.ts | `runFallbackLoop` / `FALLBACK_MAX_RETRIES = 20` / `DEFAULT_FALLBACK_TIME_BUDGET_MS = 45_000` / `getFallbackTimeBudgetMs` | 1348 / 69 / 172 / 183 |
| server/src/lib/fallback-loop.ts | `setFallbackHeaders` / `setExhaustionHeaders` | 842-864 / 905 |
| server/src/services/router.ts | `summarizeExhaustion`（九桶） | 84 |
| server/src/lib/header-value.ts | `safeHeaderValue` / `routedViaValue` | 38 / 53 |
| server/src/lib/served-model.ts | `observeServedModel` + 「response contract untouched」注释 | 61 / 17 |
| cli/src/keys.ts | CLI→API 映射 | 118-176 |
| cli/src/index.ts | 双查模型目录（`catalog` / `catalogs`） | 162-187 / 209-220 |
| cli/src/index.ts | 顶层命令派发（keys / list / setup- / doctor / launch / launch-codex） | 470 / 478 / 484 / 488 / 489 / 490 |
| cli/src/tools.ts | `metadata` 20 元组 / `tools = metadata.map` | 1037-1058 / 1060-1080 |
| cli/src/config-files.ts | `renderFile` 四路 merge 分发 / `applyGeneratedFiles` | 348-356 / 409-416 |
| cli/src/doctor.ts | livez 探测 | 303-345 |
| shared/types.ts | `Platform` 联合（74 成员） | 63-266 |
| shared/types.ts | wire 类型契约 | 445-575 |
| docker-compose.yml / Dockerfile | `/api/ping` 健康检查 | 41 / 83-84 |