# 本轮覆盖清单（基准 823c496b → HEAD 3212ac11，111 commits）

逐项判定「代码有、文档没有」的能力。处置待用户确认深度后回填状态。

## server 端新增

| 能力或机制 | 代码与测试证据 | 当前文档 | 处置 | 状态 |
|---|---|---|---|---|
| 12 个新 provider（Outcrawl/Puter/Zro/FreeInference/FreeModel/Varosity/SpeechFlow/Meldport/Rime/Typecast/Cartesia/Silvr/FreeTts） | `server/src/providers/index.ts` register 数 83→98 | 01 篇 §结论表写死「83 次 register」；24 篇覆盖表 | 改 01/24 计数 + 视深度补 11 篇 | 待办 |
| 5 个新迁移（custom_media_endpoint_identity / cloudflare_neuron_usage / key_verification_basis / model_monthly_usage / profile_routing_strategy） | `server/src/db/migrations/` 47→52；`defaults.ts` import 47→52 | 07 篇「47 迁移」 | 改 07 计数 + 列 5 个新迁移 | 待办 |
| media 服务矩阵扩展（media-freetts/media-rime/media-varosity/media-voice-gateways/media-google-live/media-solaria） | `server/src/services/media-*.ts` 新增 6 个 | 17 篇搜索与多模态 | 改 17 篇 | 待办 |
| voice-gateways（Typecast/Cartesia 语音网关）+ freetts provider | `server/src/providers/voice-gateways.ts`、`freetts.ts` | 17/11 篇 | 改 11/17 篇 | 待办 |
| specialist-text 服务 | `server/src/services/specialist-text.ts` 新增 | 无独立篇 | 视深度定 | 待办 |
| keyless-defaults 服务 | `server/src/services/keyless-defaults.ts` 新增 | 11/19 篇提及 keyless 字段 | 视深度补 | 待办 |
| codex-catalog + codex-base-instructions 服务 | `server/src/services/codex-*.ts` 新增 | 18 篇提及 codex-catalog | 改 18 篇 | 待办 |
| cloudflare-neurons 服务 + neuron usage 迁移 | `server/src/services/cloudflare-neurons.ts` | 21 篇提及 cloudflare-daily-quota | 改 21 篇 | 待办 |
| budget-input 库 + budget 改动 | `server/src/lib/budget-input.ts` 新增 | 10/21 篇预算 | 视深度补 | 待办 |
| upstream-watch 库 | `server/src/lib/upstream-watch.ts` 新增 | 无 | 视深度补 | 待办 |
| loopback 库（从别处抽出） | `server/src/lib/loopback.ts` 新增 | 19 篇 loopback 判定（引用 partial-path） | 改 19 篇引用 | 待办 |
| doubled-v1 中间件 | `server/src/middleware/doubled-v1.ts` 新增 | 16/19 篇提及 | 核对引用 | 待办 |

## desktop 端新增

| 能力或机制 | 代码与测试证据 | 当前文档 | 处置 | 状态 |
|---|---|---|---|---|
| agent-setup + agent-terminal | `desktop/src/agent-setup.ts`、`agent-terminal.ts`；`shared/agent-setup.ts` | 15 篇桌面端未覆盖 | 改 15 篇 | 待办 |
| gpu-recovery 拆分（gpu-recovery + gpu-recovery-host） | `desktop/src/gpu-recovery*.ts` | 15 篇已有 gpu-recovery 自愈阶梯 | 改 15 篇 | 待办 |
| base-urls 独立模块 | `desktop/src/base-urls.ts` | 15 篇提及 base-urls | 核对 | 待办 |

## client 端新增

| 能力或机制 | 代码与测试证据 | 当前文档 | 处置 | 状态 |
|---|---|---|---|---|
| use-search-readiness hook + search-readiness-notice | `client/src/hooks/use-search-readiness.ts` | 17 篇提及 use-search-readiness | 核对 | 待办 |
| apinex-checkin-notice / keyless-notice / provider-visibility 等组件 | `client/src/components/keys/*` 新增多个 | 13 篇仪表盘未逐一覆盖 | 视深度定 | 待办 |
| getting-started 组件 | `client/src/components/getting-started.tsx` | 13 篇 | 视深度定 | 待办 |

## strict verify 已暴露的引用失效（无论深度都要修）

| 文档:行 | 问题 | 处置 |
|---|---|---|
| 00:131 | 断链 `../../en/architecture/00-high-level-index.md` | 改或删 |
| 05:71 | partial-path `docs/adrian/sourceReader/.progress/sr_symbols.cjs`（旧 adrian 路径） | 改为现路径 |
| 11:157-161 | media-varosity/rime/voice-gateways/freetts partial-path | 补 `server/src/` 前缀 |
| 11:254 | `docs/adrian/topics/model调度算法.md` 旧路径 | 改现路径 |
| 16:84、19:118 | `lib/loopback.ts` partial-path | 补前缀 |
| 23:52、23:59、23:65 | `providers/base.ts`、`@freellmapi/shared/types.js` partial-path | 核对 |
| 24:113 | `cli/src/main.ts` partial-path | 核对 |
| topics/premium:10 | 断链 `../../en/architecture/05-catalog-sync.md` | 改或删 |

## 已知漂移计数声明（需逐篇复计，不能沿用旧数字）

- provider register：文档写 83 → 实际 98
- 迁移数：文档写 47 → 实际 52
- OpenAICompatProvider 直接创建数：文档写 33 → 待复计
- Platform 成员数：文档写 84 → 待复计
