# 报告 · 04-核心模块与类关系.md（正文语义债，第二轮）

文档：docs/adrian/sourceReader/04-核心模块与类关系.md（改前 389 行 → 改后 399 行，均为小节内增句，未增删章节、未改编号）
所有改动改前逐一 grep/Read 源码，改后立即 `grep -n` 回读磁盘确认落盘。
RULES2 第 7 条自检 grep 最终为空（exit=1）。

## A（符号已消失/错名 → 真实名+真实位置）

- A 文档:9  `RateLimiter` -> `RateLimit`（模块名） (证据: `grep -rnw RateLimiter server/src` hits=0；RULES2 自检清单含该词，不除名则自检不为空)
- A 文档:251(原) `## 4 RateLimiter 模块` -> `## 4 RateLimit 模块（services/ratelimit.ts）`，编号 4 未动 (证据: 同上)
- A 文档:72(类图)  `+hasPlatform(platform)` -> `+hasProvider(platform)` (证据: `hasProvider`=providers/index.ts:654；全仓无 `hasPlatform` 定义)
- A 文档:类图 registry 节点 补 `+getAllProviders()` (证据: `getAllProviders`=providers/index.ts:650)
- A 文档:99(类图)  `BANDIT_PRESETS: Record~Strategy, Weights~` -> `Record~PresetStrategy, RoutingWeights~` (证据: scoring.ts:25 `interface RoutingWeights`、39 `type PresetStrategy`、49 `export const BANDIT_PRESETS: Record<PresetStrategy, RoutingWeights>`)

## B（数字/断言过期 → 实测口径）

- B 文档:9  「33 个上游适配器」-> 「73 个上游适配器单例」，口径=providers/index.ts 顶层 `register()` 调用数 (证据: `grep -cE '^\s*register\(' server/src/providers/index.ts` → 73；`register()` 即 `providers.set(provider.platform, provider)`，index.ts:45-49，一平台一单例。并新增一句§0 口径说明：Platform 联合 74（python3 逐行解析 shared/types.ts:63 的 `| 'x'` 成员 → 74 unique）、`new OpenAICompatProvider` 34（grep -c → 34）、`class *Provider` 43（grep -rhoE … | sort -u | wc -l → 43）；四口径分列、不混写)
- B 文档:75  「持有 33 个单例」-> 「持有 73 个单例（register() 调用口径）」 (证据: 同上)
- B 文档:163 「33 个适配器共用」-> 「经基类继承供全部 73 个注册适配器共用」（register() 口径） (证据: `providerHttpError`=base.ts:152 基类 protected，实际调用文件 29 个（`grep -rln providerHttpError server/src/providers/ | wc -l`），全部注册适配器继承可用)
- B 文档:170 「覆盖 20+ 平台」-> 「`new OpenAICompatProvider` 共 34 个实例，含 custom 占位」（附口径命令） (证据: `grep -c 'new OpenAICompatProvider' server/src/providers/index.ts` → 34；custom 真实例由 `resolveProvider`=index.ts:636 按 key 行 base URL 临时构造，注释=index.ts:613-615)
- B 文档:204 「settings 表 8 个 routing key」-> 14 个，全部键名+定义行列表（不再用「peak 三件」这类归组省略） (证据: `grep -oE "'routing_[a-z_]+'" server/src/services/router.ts server/src/services/scoring.ts | sed 's/.*://' | sort -u | wc -l` → 14；逐个常量行：strategy=367 / custom_weights=368 / explore_enabled=369 / peak_hours_adjust=370 / peak_start_hour=371 / peak_end_hour=372 / peak_timezone=373 / community_prior=374 / community_prior_enabled=375 / headroom_ramp_start=380 / headroom_floor=381 / min_reliability_floor=417 / provider_moment_attribution=447 / task_weight_share=484，均在 router.ts；peak 实为四件含 timezone，与 report-04 一致)
- B 文档:378(§9)  `register(...)` ×33 -> ×73 (证据: 同 :9 口径)
- B 文档:351 「tools.ts 21 个 `generate(ctx): Generation`」-> 20 个生成器函数 + 注入方式 (证据: `grep -cE '^function [A-Za-z]+\(_?ctx: GenerateContext\): Generation \{' cli/src/tools.ts` → 20；`metadata`=tools.ts:1037-1058 共 20 行，生成器是元组最后一个（第 9 项）元素，`export const tools: ToolDefinition[] = metadata.map(...)`=tools.ts:1060 解构 id/name/category/configType/protocol/baseUrlSupport/command/docsUrl/generate 共 9 字段；调用点=cli/src/index.ts:301 `tool.generate(context)`)

## C（行为断言失效，小节内重写）

- C 文档:323 「三态探活」行：原「传输错误绝不写 error、绝不加失败计数」已不成立，重写为当前行为 (证据: health.ts:337-346 首次传输错误不写 status 的注释；#1510 注释=347-353；`transportFailures` Map=92；`getTransportParkAfter`（env `HEALTH_TRANSPORT_PARK_AFTER`，默认 0=关闭）=88-89；建议值 `SUGGESTED_TRANSPORT_PARK_AFTER = 6`=85；`recordTransportFailure`=102-125，达到 streak 阈值执行 `UPDATE api_keys SET status = 'error'`（115 行），park 仍每轮复探、可自愈；429 清零 streak=`transportFailures.delete`=354；仍成立部分：只有 401/403 递增自动禁用用的 `failureCount`（64），`CONSECUTIVE_FAILURES_TO_DISABLE`=3（16），`recordInvalidFailure`→`enabled=0`=157-174)
- C 文档:§5 头注释段后 补一句类型域说明：`RoutingStrategy` 七值含 `'decision'`（scoring.ts:36，#1354）、`PresetStrategy` 仅四 preset（39）、`BANDIT_PRESETS: Record<PresetStrategy, RoutingWeights>`（49） (证据: sed 读取 scoring.ts:25-64 原文注释)
- C 文档:§2.1 抽象成员区：表头 `base.ts:229-276` → `base.ts:229-287（成员声明区）`，逐成员补真实行号并新增 `supportsKeyValidation` 行（可选覆盖，getter，#1459 探活豁免）；§9 同步行区间 (证据: platform=230 / name=231 / keyless=236 / chatCompletion=238 / streamChatCompletion=246 / validateKey=254 / fetchQuota=266-268 / hasQuotaProbe=274-276 / supportsKeyValidation=285-287，grep+sed 原文核对；类体实际至 525)

## 复核后无需改动（report-04 提示项自查）

- SKIP 文档:§4（251-291 区） `checkAndReserve`/`recordResult` 在文中从未出现；类图 ratelimit 节点全部符号真实 (证据: canMakeRequest=ratelimit.ts:312、canUseTokens=334、canUseKeyConcurrency=120、acquireLease=127、releaseLease=142、canUseProvider=665、recordRequest=821、recordTokens=833、setCooldown=1241、isOnCooldown=1255、learnLimitFromError=1510、getKeyConcurrencyLimit=98（§4.3 锚 85-106 覆盖）、`CooldownSource`=863、`leases` Map=69、recordUsage=208)
- SKIP 文档:§8 风险表（360-370 区） 无任何条目引用上述计数，无需同步（引用的是 rateLimitPenalties=269 / recordUsage=208-230 / ratelimit 85-106 / orderChain 1204-1243 / index.ts:57-65，均为第一轮已校准锚点）
- SKIP 文档:344 「KeysPage 34 子组件」——与四个 provider 口径无关，不在本轮待办
- SKIP 文档:177-194 注册示例代码块 未逐字对应单一注册块（nvidia 字段 + openrouter 的 extraHeaders/quotaProbe 拼接），文中已标注「注册示例」；本轮待办未含此项，不改

## 推翻 report-04 的地方

- report-04 SEMANTIC 称 cli/tools.ts「现有 20 个 `(ctx: GenerateContext): Generation` 生成器、由元组第 10 项注入」：实测生成器函数的签名匹配是 19 + 1（`cursor` 用 `_ctx`，`grep -c "(ctx: GenerateContext): Generation"` → 19；含 `_?ctx` → 20）；且注入元素是元组第 **9**（最后）项而非第 10 项（tools.ts:1060 的解构共 9 个字段）。文档按 20 个/第 9 项写。
- report-04 SEMANTIC 对 :9 只给了「73 个 register、其中 33 个 compat」两个数，未提 `new OpenAICompatProvider` 实测是 **34**（含 custom 占位），33 已不再是任何成立口径——本轮按 34 实例口径写并附命令。
