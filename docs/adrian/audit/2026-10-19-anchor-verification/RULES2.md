# sourceReader 正文校正规则（第二轮：A/B/C 三类语义债）

仓库：/Users/vincent/workspace/16_AI/freellmapi（分支 adrian）
**不要 commit、不要 push、不要改任何源码文件。** 只改分配给你的 md。

## 背景
第一轮已把 12 篇走读文档的 `文件名.ts:行号` 锚点全部按当前 HEAD 重新定位（提交 `c801c802`）。
第二轮要修的是**正文本身**：文档写的符号名 / 数字 / 行为在当前源码里已经不存在或已变更。
逐篇的证据在同目录 `docs/adrian/audit/2026-10-19-anchor-verification/report-*.md` 的 SEMANTIC 段
（README.md 是汇总表）。**那些报告是提示，不是事实来源** —— 每一条都要你自己回源码验证后才写进正文。

## 三类任务
- **A 类：符号已消失** → 把正文里的旧符号名改成当前真实名字，并保证配套的行号也重新核对过。
  已实测 hits=0（`grep -rnw <符号> server/src client/src shared types.ts cli/src`，排除 `__tests__`）：
  `pickModel` `RateLimiter` `checkAndReserve` `recordResult` `StreamChunk` `ChatResponse` `convertMessages`
  `listProviders` `getAllModels` `getChainCandidates` `RESERVED_TABLES` `dbBackupPump` `libSqliteFactory`
  `rotateEncryptionKey` `getKeyConcurrency` `checkHealth` `getModelCapabilities` `ChatRequest`；
  `recordFailure` 只在 `routes/auth.ts:79`（登录失败计数）与一个测试 helper 里，与限流无关；
  `Router` / `Provider` 作为类名不存在（是 `BaseProvider`，函数式模块）。
  改名的同时**必须给出新名字的真实位置**，例如 `canMakeRequest`=services/ratelimit.ts:312。
- **B 类：数字/事实过期** → 用下面「统一事实表」的口径，并且自己跑一遍测量命令。
- **C 类：整段结构错误** → 需要重写小节（把错误的归属、伪码、缺失条目补全）。重写要短、贴源码，
  不写「曾经/现在改为」这类历史叙述，直接描述当前实现。

## 统一事实表（本轮主线实测，子代理必须自己复跑一遍命令再引用）
| 事实 | 数值 | 测量命令 |
|---|---|---|
| Platform 联合成员 | 74 | `python3` 解析 `shared/types.ts:63` 的 `export type Platform` |
| provider 注册调用 | 73 | `grep -cE '^\s*register\(' server/src/providers/index.ts` |
| `class *Provider` 定义 | 43 | `grep -rhoE 'class [A-Za-z0-9_]+Provider' server/src/providers/*.ts \| sort -u \| wc -l` |
| `new OpenAICompatProvider` | 34 | `grep -c 'new OpenAICompatProvider' server/src/providers/index.ts` |
| providers 目录文件数 | 44 | `ls server/src/providers/*.ts \| wc -l` |
| 迁移文件 | 44（含 `20260101_000000_legacy_baseline.ts`，最新 `20261017_233153_request_failure_attribution.ts`） | `ls server/src/db/migrations/*.ts \| wc -l` |
| server 测试**文件**数 | 347 | `find server/src -name '*.test.ts' \| wc -l`（注意：这是文件数，不是用例数；文档若要写用例数必须实跑 vitest，否则写文件数） |
| client 测试文件数 | 56 | `find client/src -name '*.test.ts*' \| wc -l` |
| desktop 测试文件数 | 13 | `find desktop -name '*.test.ts*' -not -path '*/node_modules/*' \| wc -l` |
| `routing_*` 持久化键 | 14 | `grep -oE "'routing_[a-z_]+'" server/src/services/router.ts server/src/services/scoring.ts \| sed 's/.*://' \| sort -u \| wc -l` |
| 回退墙钟预算 | 45_000 ms（默认） | `server/src/lib/fallback-loop.ts:172 DEFAULT_FALLBACK_TIME_BUDGET_MS` |
| 401 冷却 | 5 min | `server/src/lib/fallback-loop.ts:627 AUTH_FAILURE_COOLDOWN_MS` |
| 402 冷却 | `DAY` | `server/src/services/ratelimit.ts:963 PAYMENT_REQUIRED_COOLDOWN_MS` |
| 真实限流入口 | `canMakeRequest`=312、`canUseTokens`=334、`recordRequest`=821、`recordTokens`=833、`getCooldownDecisionForLimit`=1112、`getKeyConcurrencyLimit`=98 | `server/src/services/ratelimit.ts` |
| provider 侧真实类型 | `ChatCompletionResponse`/`ChatCompletionChunk`/`TokenUsage` 在 `shared/types.ts`（约 531/546/559） | `grep -n 'export interface Chat\|export interface TokenUsage' shared/types.ts` |
| BaseProvider | `providers/base.ts:229`，抽象方法 `platform`/`name`/`chatCompletion`/`streamChatCompletion`/`validateKey`（230/231/238/246/254），可选 `fetchQuota` 266-268、`hasQuotaProbe` 274-276、`supportsKeyValidation` 285 | 同上 |
| 链读取 | `resolveRoutingChain`=services/router.ts:1437-1480、`getActiveChain`、`getChainByProfileName`；入口 `routeRequest`=2152 | 同上 |
| provider 注册表导出 | `getAllProviders`=providers/index.ts:650、`hasProvider`=654、`getProvider`=626 | 同上 |
| 备份 | `startDbBackupPump`=lib/db-backup.ts:263；`EXCLUDED_TABLES`=`services/backups.ts:62`（users/sessions/url_tokens）、`isInternalTable`=67 | 同上 |
| Gemini 映射 | `toGeminiContents`（google.ts），`streamChatCompletion`=google.ts:647-836；无 `convertMessages` | 同上 |
| key 轮换 | `scripts/rotate-encryption-key.ts`（不在 lib/crypto.ts） | `find . -name 'rotate-encryption-key*' -not -path '*/node_modules/*'` |

## 写作红线（沿用 00-docs-style-guide.md）
1. 严禁编造。查不到的写「未实测，待补」，绝不猜数。
2  禁止「同上/略/以此类推」替代核心内容。
3. 锚点记法：正文用 `符号名 +偏移`，文末源码索引可写 `文件:函数:绝对行号`。**行号一律用第一轮校准后的值**，
   你新改的地方必须再 grep 一次。
4. 中文正文，符号/文件/错误码保持英文原样。
5. 每处改动都要能指出你查过的源码行；报告里写「证据: 符号=真实行」或「证据: 测量命令 → 输出」。
6. 不新增章节、不删章节、不改章节编号（编号动了会破 §交叉引用）。C 类重写只在小节内部进行。
7. 改完整个文件后跑一次自检：`grep -nE '\b(checkAndReserve|recordResult|RateLimiter|StreamChunk|ChatResponse|listProviders|getAllModels|pickModel|convertMessages|RESERVED_TABLES|dbBackupPump|rotateEncryptionKey|getModelCapabilities|checkHealth|ChatRequest)\b' <你的md>`
   期望结果为空（除了明确要说明「旧名」的地方——本轮不写历史，所以应为空）。

## 报告格式（写到 /tmp/docval/prose-<章节号>.md）
- `A  文档:行  旧符号 -> 新符号 (证据: 新符号=文件:行)`
- `B  文档:行  旧数字/断言 -> 新 (证据: 命令 -> 输出)`
- `C  文档:行  重写说明 (证据: ...)`
- `SKIP 文档:行 原因`
