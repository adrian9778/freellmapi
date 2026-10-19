# sourceReader 锚点核验 · 2026-10-19

本轮只做**行号核验**：`docs/adrian/sourceReader/` 12 篇里每一个 `文件名.ts:行号` 锚点都按当前 HEAD 源码重新定位，
正文一字未改（除 §「已改正文」一处）。逐条证据在同目录的 `report-*.md`（由校验脚本 `check3.py` 的输出驱动，
每条 FIXED 都写了「符号 = 真实行」的依据，并在改后回读文档确认落盘）。

- 校正量：257 行（改前行数 = 改后行数，纯原位替换），提交 `c801c802`。
- 复核脚本口径：锚点全部在文件行数范围内、起始行非空、`file.ts:NNN` 最近的真实符号定义行 Δ≤3。
  剩余 14 条告警是脚本口径误报（同一行里提到第二个符号，如 `base.ts:35-44` 的正文还提了 `MAX_RETRY_AFTER_MS`）。

## 待办：正文与源码不符（约 40 条，逐篇列在 report-*.md 的 SEMANTIC 段）

这一类不是行号错，而是**文档写的符号/数字/行为在当前源码里已不存在**。全部下述命中数由
`grep -rnw <符号> server/src client/src shared/src cli/src`（排除 `__tests__`）实测。

### A. 已消失的符号（hits=0，即整个仓库都搜不到）

| 文档位置 | 正文写的 | 当前源码 | 命中 |
|---|---|---|---|
| 01:113/153、02、03、10 | `Router` 类 / `pickModel()` | 函数式模块，入口 `routeRequest()`=router.ts:2152 | 0 |
| 01:154、02:344、03:225/281、10 | `RateLimiter` / `checkAndReserve()` / `recordResult()` | `canMakeRequest`=312、`canUseTokens`=334、`recordRequest`=821、`recordTokens`=833 | 0 |
| 01:155、02:345 | `StreamChunk` / `ChatResponse` / `getModelCapabilities` / `checkHealth` | `ChatCompletionChunk`/`ChatCompletionResponse` 在 `shared/src/types.ts`；抽象方法是 `chatCompletion`/`streamChatCompletion`/`validateKey` | 0 |
| 01:156、02:347 | `listProviders()` / `getAllModels()` | `getAllProviders()`=650、`hasProvider()`=654 | 0 |
| 01:159 | `rotateEncryptionKey()` | `scripts/rotate-encryption-key.ts` | 0 |
| 02:346 | `google.ts:convertMessages()` | 手写映射 `toGeminiContents()`，`streamChatCompletion`=647-836 | 0 |
| 02:354、03 索引 | `model-state.ts:getChainCandidates()` | 链读取在 `services/router.ts`（`resolveRoutingChain`=1437-1480、`getActiveChain`） | 0 |
| 07:160 | `dbBackupPump` | `startDbBackupPump` | 0 |
| 07:188 | `RESERVED_TABLES` | `isInternalTable` / `EXCLUDED_TABLES` | 0 |
| 06:34 | `getKeyConcurrency` | `getKeyConcurrencyLimit`=98 | 0 |
| 03/01 | `ChatRequest` 类型 | 无此名（`ChatMessage[]` + 原生 body） | 0 |

`recordFailure` 只在 `routes/auth.ts:79`（登录失败计数）和一个测试 helper 里，与限流无关 —— 文档拿它当限流记账函数。

### B. 数字/事实过期

- **「33 个 provider/适配器」**出现在 01:38/156、02:221、04:9/75/163、05:155、11:52。实测 `providers/index.ts` 里
  `register(...)` 调用 **73** 处，`new OpenAICompatProvider` **34** 个，`providers/*.ts` **44** 个文件。
- **07 §3 的开发/生产迁移分叉写反**：`initDb` 是 `NODE_ENV !== 'development'` 才跑迁移；开发环境只校验表存在并带提示退出。
- **07 §5**：provisional 用量并非「写成 kind 占位行」，而是纯内存 lease 求和。
- **07**：恢复安全阀覆盖 `users`/`sessions`/`url_tokens`（**不**含 `api_keys`）；baseline 建 **13** 张表；增量迁移 **43** 个文件（最新 `20261017_233153`）。
- **回退墙钟预算 45 s**，不是文档里多处写的 60 s（`FALLBACK_TIME_BUDGET_MS`，见 topics/model调度算法.md §5.3）。
- **401/402 冷却**：`AUTH_FAILURE_COOLDOWN_MS = 5min`、`PAYMENT_REQUIRED_COOLDOWN_MS = DAY`；03 §5.2 表写的是 10min / 60min。
- **03:129** `resolveTaskType()` 只返回 `code | chat | undefined`，没有 `analysis`/`creative`。
- **03 §1.2 / 05**：中间件注册顺序里 `compression()` 实际挂在所有 router **之后**（app.ts:351，仅静态资源用），目的是不缓冲 SSE。
- **04:323** 「传输错误绝不写 `status='error'`」已不成立：连续传输错误会把 key 停在 `error`（health.ts:100-120、349，#1510）。
- **04:204**「settings 表 8 个 routing key」→ 现约 13 个持久化键。
- **08** 的 P1 风险条目（「server-host-boot.test.ts 只比对调用清单不比对顺序」）**已经过时**：该测试现在断言完整有序调用列表（:163-165）。
- **09**：server 测试 347 个（文档 317）、desktop 测试文件 13 个（文档 12）、client 测试环境是 node 默认 + 文件级 docblock，不是全局 jsdom。
- **01:156/159 等模块表**里的「21 个 agent」实为 20 个 generator，且 generator 现在由 metadata 元组注入。

### C. 结构性问题（需要重写整段，不是改数字）

- **02 §3.3**：正文写「`streamChatCompletion()` (router.ts 约 800 行)」并贴了一段 `recordResult/recordFailure` 伪码 ——
  router.ts 里没有任何 generator。本轮已把标题与该代码块改成「回退主循环 `runFallbackLoop()` (lib/fallback-loop.ts:1348)」并
  **显式标注「概念示意（非逐行源码）」**，这是本轮唯一动过的正文。
- **03 §4.1** 同题（标题写 router.ts，实际内容是 routes/proxy.ts:2358-2833 的 provider 生成器调用 + fallback-loop 循环）；
  **03 §3.4** 的 mermaid 图节点名仍是 `checkAndReserve`；**03:330-343** 列的 BaseProvider 契约方法名与实际抽象方法不符。
- **05 挂载表**缺 `/api/search`、`/api/decisions`；`/api/ping` 的 handler 其实在 app.ts:279-281（文档写「待补」）；
  `mcp.ts` 还有 DELETE /（703）未列。
- **11** 里还有 5 处以 `+NNN` 形式写的绝对行号（`+499`、`577~581`、`+600~602`、`+609~+615`、`+395`），
  真实位置已在 report 里给出，但那是正文里的数字而非锚点，本轮未改。

## 建议下一步

1. **B 类**逐条改数字即可，风险低，可以脚本+人工各半。
2. **A 类**要选边：把符号名改成当前真实名（推荐，文档就该讲现状），或在开头声明这批发稿写于更早的架构。
3. **C 类**要重写小节，建议单独一轮，从 03、05、11 开始（这三篇语义债务最重）。
