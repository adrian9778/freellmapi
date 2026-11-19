# 覆盖清单 — 基准 823c496b → HEAD 1a64da55

核对日期：2026-11-17。漂移：85 commits / 387 文件。verify 基线：16 文档 / 1023 符号引用。
首轮 verify：19 错误 → 修正 2 个真实漂移簇后 14 错误，全部为指向未落盘计划篇（15/16/17/18/19/21）的前向链接。

## A. 已修正的既有篇目漂移

| 主题 | 证据 | 当前文档 | 处置 | 状态 |
|---|---|---|---|---|
| 租约老化 `LEASE_MAX_AGE_MS`（固定 2min）→ `leaseMaxAgeMs(platform)`（按平台计算） | `server/src/services/ratelimit.ts` · `leaseMaxAgeMs+0`（92）、`pruneLeases+0`（98）、`LEASE_BACKSTOP_FLOOR_MS+0`（88）、`LEASE_BACKSTOP_MARGIN_MS+0`（89） | 04/06/07 | 改节（语义重写） | 完成 |
| Ollama `isLoopback` 变为 `lib/loopback.ts` 单行委托，`+0~+13` 偏移越界 | `server/src/routes/ollama.ts` · `isLoopback+0`（26）、`server/src/lib/loopback.ts` · `isLoopbackRequest+0`（35）、`forwardedPeerAddress+0`（25）、`isLoopbackAddress+0`（14） | 05 | 改节（锚点+语义） | 完成 |

## B. 新增能力覆盖缺口（代码已存在，文档未覆盖）

### B1. 应并入既有篇目

| 能力或机制 | 代码与测试证据 | 需求来源 | 当前文档 | 处置 | 状态 |
|---|---|---|---|---|---|
| 9 个新 provider（zro/freeinference/freemodel/varosity/rime/typecast/cartesia/silvr/freetts/outcrawl） | `server/src/providers/*.ts`、注册于 `server/src/providers/index.ts` | 可观察行为 | 11-Provider与流式 | 改节（provider 清单与契约） | 待办 |
| 语音/媒体出站服务（media-freetts/rime/varosity/voice-gateways） | `server/src/services/media-*.ts` | 可观察行为 | 11 或 17 | 改节 | 待办（依赖 17 是否落盘） |
| `collapseDoubledV` doubled-v1 中间件 | `server/src/middleware/doubled-v1.ts`、`__tests__/routes/doubled-v1-prefix.test.ts` | 可观察行为 | 05-API与接口设计 | 改节（路由前缀规范化） | 待办 |
| Codex catalog / base-instructions | `server/src/services/codex-catalog.ts`、`codex-base-instructions.ts` | 可观察行为 | 05 或 18 | 改节 | 待办 |
| 5 个新迁移（media_models 重建、cloudflare_neuron_usage、api_keys.verification_basis、model_monthly_usage、profiles.routing_strategy） | `server/src/db/migrations/2026{1028,1104,1105,1111}*.ts`（总数 47→52） | 可观察行为 | 06-配置与数据流、07-状态存储与并发 | 改节（迁移计数与表清单） | 待办 |
| Cloudflare neurons 用量 | `server/src/services/cloudflare-neurons.ts` | 可观察行为 | 06/07 或 21 | 改节 | 待办 |

### B2. 计划篇（15–24）全部未落盘

15 桌面端（含新 gpu-recovery、base-urls、desktop-login-item）、16 多协议入口、17 搜索与多模态（含 search-readiness）、18 模型与端点管理、19 认证与安全、20 会话与内容处理、21 后台探测与配额、22 日志与备份、23 类型与配置契约、24 函数覆盖总表。
→ 这些是 plannedAdditions，属于既有计划的补全，非本轮漂移引入。13/14 已为它们预留前向链接（当前 verify 的 14 个错误即此）。

## B1 完成记录（2026-11-17）

B1 各项已并入既有篇目：9 新 provider + media 服务 → 11；迁移 47→52 + Cloudflare neurons → 07；doubled-v1/Codex → 16/05/18。provider 注册 83→94、OpenAICompatProvider 34→35 已实测更新。

## C. 待用户确认

覆盖缺口默认必须处理（用户要求"同步到最新代码"）。但 B2 的 10 篇计划篇是独立的大体量新增，且 13/14 已为其预留链接——需确认本轮是「只把新能力并入既有 00–14 + topics」还是「同时补写计划篇 15–24」。