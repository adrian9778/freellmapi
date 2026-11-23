# 本轮文档同步规范（2026-11-23 全量深度重刷）

- 日期：2026-11-23。
- 源码基准：本地 `adrian`，`3212ac117dd9cf3cc2e987273a1b72b60d75f3f0`（短 `3212ac11`）；未拉取远端。工作区干净。
- 上一轮基准：`823c496b`（2026-11-17）。本轮间隔 **111 commits / 518 文件**。
- 范围：`docs/sourceReader/`、`docs/topics/`；应用源码不改，`.progress/` 只存状态与工具。
- 用户已确认：**全量逐篇深度重刷**（29 篇全部按当前代码重新走查、重写漂移段落、补新能力）。
- 修改前备份：见 state.json `backup`。

## 0. 本轮关键变化（区别于上一轮）

| 项 | 上一轮 | 本轮 |
|---|---|---|
| 文档目录 | `docs/adrian/sourceReader/` | **`docs/sourceReader/`**（已从 adrian 子目录上移，所有自引用路径、`.progress` 工具调用路径、交叉链接都要相应改写） |
| topics 目录 | `docs/adrian/topics/` | **`docs/topics/`** |
| provider register 数 | 83 | **98**（新增 12 个 provider） |
| 迁移数 | 47 | **52**（新增 5 个迁移） |
| sr_tools root 上溯 | 4 层（错） | **3 层**（已修，否则 typescript 解析 + git ls-files 全失败） |

## 1. 本轮已确认的漂移与新增能力

### 1.1 新增 provider（register 83→98）

`OutcrawlProvider`(SearchOnly) / `PuterProvider`(Base) / `ZroProvider`(OpenAICompat) / `FreeInferenceProvider`(OpenAICompat) / `FreeModelProvider`(OpenAICompat) / `VarosityProvider`(Base) / `SpeechFlowProvider`(Base) / `MeldportProvider`(OpenAICompat) / `RimeProvider`(Base) / `TypecastProvider`+`CartesiaProvider`(NativeSpeech) / `SilvrProvider`(OpenAICompat) / `FreeTtsProvider`(Base)。

### 1.2 新增迁移（47→52）

`20261028_000001_custom_media_endpoint_identity`（media_models 重建 + requests.media_model_db_id）/ `20261104_000001_cloudflare_neuron_usage` / `20261105_000001_key_verification_basis`（api_keys.verification_basis）/ `20261111_000001_model_monthly_usage` / `20261111_000002_profile_routing_strategy`（profiles.routing_strategy）。

### 1.3 新增 server 服务 / lib

media 服务矩阵：`media-freetts` / `media-rime` / `media-varosity` / `media-voice-gateways` / `media-google-live` / `media-solaria`。其它：`specialist-text` / `keyless-defaults` / `codex-catalog` / `codex-base-instructions` / `cloudflare-neurons`。lib：`budget-input` / `upstream-watch` / `loopback`（抽出）/ 中间件 `doubled-v1`。

### 1.4 desktop / client / cli 新增

desktop：`agent-setup` / `agent-terminal` / `base-urls` / `gpu-recovery`+`gpu-recovery-host` 拆分。shared：`agent-setup`。client：`use-search-readiness`、apinex/keyless 通知组件、getting-started。cli：config-files/index/tools/types 改动。

## 2. 统一定位写法（沿用上一轮，路径前缀改为现目录）

正文使用：`server/src/services/router.ts` · `routeRequest+0`。连续区间：`+8~+13`。方法带类名，匿名路由用真实注册表达式。定位命令从仓库根运行：

```bash
python3 docs/sourceReader/.progress/sr_tools.py locate routeRequest
python3 docs/sourceReader/.progress/sr_tools.py outline server/src/services/router.ts --top
python3 docs/sourceReader/.progress/sr_tools.py offset server/src/services/router.ts routeRequest
python3 docs/sourceReader/.progress/sr_tools.py verify docs/sourceReader/某篇.md
```

## 3. 每篇的固定要求（沿用上一轮 8 条，追加 2 条）

1. 开头注明层级、日期（2026-11-23）、基准（`3212ac11`）和本篇边界。
2. 先生产视角（真实参与者/触发/可见结果），再开发视角；不先堆缩写。
3. 函数写职责、签名/关键入参、输出、调用方、内部分步、异常与状态副作用。
4. 主调用链有双方定位；不能仅列函数名充当解释。
5. 每篇至少一张与真实文件/符号对应的图。
6. 文末先源码索引与导航，再术语表。
7. 只用四种不确定性标记：`[源码未确认]`、`[源码未找到]`、`[推断]`、`[待运行验证]`。
8. 历史实例观察保留原日期；本轮不向上游发计费请求，不改数据库、不重启。
9. **本轮新增**：所有自引用路径、交叉链接、`.progress` 调用示例必须用 `docs/sourceReader/`（非 `docs/adrian/`）。
10. **本轮新增**：凡引用计数（provider 数、迁移数、表数、测试数、register 数）必须用当前代码复计，禁止沿用上一轮数字。

## 4. 校验口径

- 每篇落盘前跑 `verify <本篇>`，失效路径 = 0；`--strict` 报警逐条人工判读后修复，不得删引用消警。
- 全部篇目完成后跑一次全量 sweep + 复核日期一致性。
- 工具不能证明偏移的业务解释正确，也不证明 Mermaid 可渲染。
