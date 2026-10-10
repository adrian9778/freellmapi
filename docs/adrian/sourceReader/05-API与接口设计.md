# 05 API 与接口设计

> 第四层 · 第 2 篇。`/v1` wire 面、`/v1beta` Gemini 原生面、Ollama 面、MCP 面、`/api/*` Dashboard 管理面、运维探针面的全量接口清单 + 认证分界 + 跨面契约。

---

## 0 一张路由挂载总图（`app.ts:204-330`，全部经源码核实）

```
app.ts 挂载顺序（顺序即优先级）
  app.use(clientContextMiddleware)                    :204
  app.use(ollamaRouter)                               :217   ← /api/tags 等，注意在 admin 门之前
  app.use('/api', adminRateLimiter)                   :231
  app.use('/api/auth', authRouter)                    :236   ← 无需 requireAuth（登录入口）
  app.use('/api/keys/export', EXPORT_RATE_LIMIT_RPM)  :242   ← 密码暴破上限 10/min
  app.use('/api/keys', requireAuth, keysRouter)       :244
  ... 其余 /api/* 全部 requireAuth                     :248-272
  app.use('/v1', docsRouter)                          :283   ← /v1/openapi.json, /v1/docs
  app.use('/v1', providersRouter)                     :289   ← /v1/providers, /v1/quota-forecast
  app.use('/v1/t/:token', rateLimiter, urlTokenRouter):292-293 ← URL 内嵌凭证（媒体类客户端）
  app.use('/v1', proxyRateLimiter, ...)               :298-309
      anthropicRouter → proxyRouter → moderationRouter → responsesRouter
  app.use('/v1beta', rateLimiter, geminiRouter)       :312-313
  app.use('/mcp', rateLimiter, mcpRouter)             :320-321
  app.use(statusRouter)                               :327   ← /livez /readyz（无认证无限流）
  app.use(errorHandler)                               :330
```

**两套限流器**（`middleware/rateLimit.ts`）：`createProxyRateLimiter(120 RPM)` 挂 wire 面、`createAdminRateLimiter` 挂 `/api`；export 路由再叠一层更严的 10/min。

---

## 1 `/v1` OpenAI 兼容面（`routes/proxy.ts` 等，逐条核实）

| 方法 | 路径 | 锚点 | 说明 |
|------|------|------|------|
| GET | `/v1/models` | proxy.ts:314 | 列表；`?available=true` 只回当前配额可用的（CLI 双查区分「不存在」vs「耗尽」） |
| POST | `/v1/chat/completions` | proxy.ts:1493 | 主入口。`model:"auto"` 或省略 = 自动路由（proxy.ts:44-54） |
| POST | `/v1/completions` | proxy.ts:1076 | legacy 补全，内部翻译为 chat 形态 |
| POST | `/v1/embeddings` | proxy.ts:677 | → `services/embeddings.ts:runEmbeddings` |
| POST | `/v1/rerank` | proxy.ts:712 | → `services/rerank.ts:runRerank`（非 OpenAI 标准，cohere 风格） |
| POST | `/v1/images/generations` | proxy.ts:769 | → `services/media.ts:runImageGeneration` |
| POST | `/v1/videos/generations` | proxy.ts:807 | → `runVideoGeneration` |
| POST | `/v1/audio/speech` | proxy.ts:863 | TTS |
| POST | `/v1/audio/transcriptions` | proxy.ts:912 | STT；multer 上传，`MAX_TRANSCRIPTION_BYTES` 封顶 |
| POST | `/v1/moderations` | moderation.ts:25 | #1155 |
| POST | `/v1/responses` | responses.ts:624 | OpenAI Responses API 形态（后台任务/流式事件） |
| POST | `/v1/messages` | anthropic.ts:444 | **Anthropic Messages 协议**，同一 router 复用 |
| POST | `/v1/messages/count_tokens` | anthropic.ts:1087 | Anthropic 计费预估 |
| GET | `/v1/models` (anthropic 形态) | anthropic.ts:1126 | 与 proxy 的 GET /models 同路径不同鉴权头（x-api-key） |
| GET | `/v1/providers` | status.ts:112 | 按 provider 汇总的健康/配额视图 |
| GET | `/v1/quota-forecast` | status.ts:221 | `services/quota-forecast.ts` 预测配额耗尽时间 |
| GET | `/v1/openapi.json` `/v1/docs` | docs.ts:14,20 | 内嵌 OpenAPI 文档 |
| * | `/v1/t/:token/*` | url-tokens.ts + routes/url-tokens.ts | 短期 URL 令牌（图片等无法带 header 的场景） |

### 1.1 Anthropic 双面共存的一个细节

`GET /v1/models` 有**两个 handler**（proxy.ts:314 与 anthropic.ts:1126），挂载顺序 anthropic 在前（app.ts:304 vs 305）——Anthropic SDK 拉模型列表时命中 anthropic 版，返回带 Anthropic 家族描述的形态；`anthropic-map.ts:claudeFamilyDiscoveryEntries` 负责把内部模型 id 映射成 Claude 风格 id。

### 1.2 认证统一（三头一验）

```
extractApiToken()  proxy.ts:78-89
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

**注意与 `/api/*` admin 面的路径共存**：ollamaRouter 先挂（app.ts:217），Ollama 面自带 token 校验逻辑；未命中 ollama 的 `/api/*` 落入 adminRateLimiter + requireAuth 分支（app.ts:231 之后）。

---

## 4 MCP 面（`routes/mcp.ts`）

`POST /mcp`（mcp.ts:587）+ `GET /mcp`（611）。把 gateway 作为 MCP server 暴露（工具目录 = 可用模型）；`settings.mcp_enabled` 开关（migration 20260903_000001）。

---

## 5 运维探针面（`routes/status.ts`，无鉴权无限流）

| 路径 | 锚点 | 返回 |
|------|------|------|
| GET `/livez` | status.ts:41 | `{status, version, uptime_s}` ——CLI doctor 与 Docker HEALTHCHECK 的目标 |
| GET `/readyz` | status.ts:64 | 依赖就绪（DB 等） |

Docker healthcheck 实际打 `/api/ping`（docker-compose.yml）——由 healthRouter 提供（routes/health.ts，挂在 `/api/health` 之外另有顶层 ping；当前源码未在挂载表出现独立 ping，**未逐条核实 /api/ping 的具体 handler 归属，待补**）。

---

## 6 `/api/*` Dashboard 管理面（全部 `requireAuth`，session token 认证）

挂载清单（app.ts:244-272，逐条核实）：

```
/api/auth            authRouter        登录/注册/session（唯一免 requireAuth）
/api/keys            keysRouter        provider keys CRUD、批量导入(.env 粘贴+预览+逐键选择)、
                                        导出(json/.env/csv，密码门 + 10/min)、per-key 代理、模型发现
/api/client-profiles clientProfilesRouter  profile key（带强制 system prompt 的发行 key）
/api/conversations   conversationsRouter   Playground 会话持久化
/api/logs            logsRouter            请求日志查询
/api/models          modelsRouter          模型目录 CRUD/override/tombstone/权重
/api/profiles        profilesRouter        fallback profile 管理
/api/fallback        fallbackRouter        主链编辑 + 路由策略 PUT /api/fallback/routing
/api/embeddings      embeddingsRouter      嵌入模型管理
/api/media           mediaRouter           图像/音频/视频模型管理
/api/analytics       analyticsRouter       统计聚合（延迟分位索引 migration 20260902）
/api/health          healthRouter          手动 check / checkAll / 状态读取
/api/free-tier       freeTierRouter        免费额度全景视图
/api/settings        settingsRouter        全局设置（策略/预算/代理/日志保留…）
/api/premium         premiumRouter         Premium 订阅/激活/live catalog
/api/backups         backupsRouter         DB 备份 CRUD/恢复
/api/cache           cacheRouter           响应缓存管理
/api/compression     compressionRouter     提示压缩管线配置
/api/update          updateRouter          自更新（docker watchtower 触发 / 桌面端配合）
```

**认证模型**：`users(email+password_hash)` → `sessions(token_hash 主键, expires_at_ms)`（legacy_baseline.ts:161-173）。首次启动 `userCount()===0` 时铸一次性 setup code 并打印（index.ts:70-72）：loopback 浏览器可免 code 完成 setup，远程调用必须带 code。

---

## 7 Provider 契约（跨面共享的抽象，`providers/base.ts`）

33 个 provider 单例注册进 `Map<Platform, BaseProvider>`（providers/index.ts:35-39）。契约三方法 + 两个可选（详见 [04](04-核心模块与类关系.md) §2）。

**wire 形态 × 面 的复用矩阵**——同一 `routeRequest/streamChatCompletion` 内核服务 5 种入口协议：

```
                    ┌─ proxy.ts        OpenAI Chat/Completions
                    ├─ responses.ts    OpenAI Responses
anthropic.ts        ├─ 请求翻译 → 内部 ChatRequest → router → 响应翻译回 SSE(event) 形态
gemini.ts  ────────►┤  (共享 lib/fallback-loop.ts 的 20 次/45s 预算记账，杜绝各面漂移)
ollama.ts  ────────►┘
```

fallback-loop 头注释（fallback-loop.ts:2-17）披露了这个设计的由来：三个面曾各有 ~150 行手工复制的 attempt loop，**已经漂移出三类 bug**（同一个 403 三个面 bench 一天、/v1/responses 只 bench 90s；exhaustion 体三个面回 400、messages 面恒 429；Retry-After 唯独 /v1/responses 不遵守）。收敛后各面只留薄 `dispatch` 翻译层。

---

## 8 CLI 契约（`cli/src/`，纯 HTTP，无 import server）

| CLI 命令 | 打到哪里 | 认证 |
|----------|----------|------|
| `setup-*` / `launch*`（21 个 agent） | 只读 `GET /v1/models?available=true` + `GET /v1/models`（双查区分不存在 vs 耗尽，index.ts:165-220） | `FREELLMAPI_API_KEY`（Bearer） |
| `keys add/list/remove/test` | `GET/POST/DELETE /api/keys`、`POST /api/health/check/{id}`、`GET /api/keys/providers`、`GET /api/models`（keys.ts:94-116） | `FREELLMAPI_DASHBOARD_TOKEN`（session） |
| `doctor` | `GET {url}/livez`（doctor.ts:303-345） | 无 |

**配置文件写入契约**（tools.ts:1037-1080 + config-files.ts:409-416）：四种 merge 语义（JSON deep-merge / YAML 结构化 merge 保注释键序 / TOML 分块 merge / ENV 按 key 替换），两阶段提交，写前备份，sensitive 0600。

---

## 9 错误响应契约（全 wire 面统一）

```jsonc
{ "error": { "message": "...", "type": "authentication_error | rate_limit_exceeded | routing_error | invalid_request_error", "code": null } }
```

- 401 语义纪律：client 端只在 `type==='authentication_error'` 时清 session（client/src/lib/api.ts:44-49）——provider key 坏掉的 401 不得把用户登出
- 429 exhaustion：body 携带 `summarizeExhaustion()` 的九桶摘要 + `Retry-After`（`setExhaustionHeaders`，fallback-loop）
- 错误文本经 `lib/error-redaction.ts` 消毒，绝不回显上游 key/内部 URL

## 10 响应头契约

`lib/header-value.ts`：`X-Routed-Via`（routedViaValue 安全化）、`X-Execution-Id`、缓存/幂等相关头（`setFallbackHeaders`）；`Routed-Model` 由 `lib/served-model.ts:observeServedModel` 观测回写。

---

## 11 已知缺口 / 待拍板

| # | 级别 | 描述 |
|---|------|------|
| 1 | 待核实 | `/api/ping`（Docker HEALTHCHECK 目标）的 handler 归属未逐条核实——写「待补」不臆测 |
| 2 | 风险 | `GET /v1/models` 双 handler 靠挂载顺序决胜，任何后续把 proxyRouter 挪到 anthropicRouter 之前都会翻转 Anthropic SDK 的列表形态 |
| 3 | 设计特性 | `/api/*` 与 Ollama `/api/*` 同前缀共存，靠先挂 ollamaRouter 解决——新人读挂载表易误判 |
| 4 | 风险 | n>1 多补全、多租户计费在 high-level-index 明示「未支持」；看到 README 之外有人实现需求应先对齐 |

---

## 12 源码索引

| 文件 | 符号 | 行号 |
|------|------|------|
| server/src/app.ts | 挂载序列 | 204-330 |
| server/src/routes/proxy.ts | `proxyRouter` 全部端点 | 314-1493 |
| server/src/routes/responses.ts | `/responses` | 624 |
| server/src/routes/anthropic.ts | `/messages` 群 | 444-1126 |
| server/src/routes/gemini.ts | `/v1beta/models…` | 80-231 |
| server/src/routes/ollama.ts | Ollama 端点群 | 96-602 |
| server/src/routes/mcp.ts | MCP | 587-611 |
| server/src/routes/moderation.ts | `/moderations` | 25 |
| server/src/routes/status.ts | `/livez` `/readyz` `/providers` `/quota-forecast` | 41-221 |
| server/src/routes/docs.ts | openapi/docs | 14-20 |
| server/src/lib/fallback-loop.ts | 双面漂移历史注释 | 2-17 |
| cli/src/keys.ts | CLI→API 映射 | 94-116 |
| cli/src/index.ts | 双查模型目录 | 165-220 |
| cli/src/doctor.ts | livez 探测 | 303-345 |
| shared/types.ts | wire 类型契约 | 410-540 |