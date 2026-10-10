# 规范与定位约定

本文档库统一使用以下记法，与 `source-doc-4layer` skill 的事实红线一致。

## 1. 源码锚点记法

### 函数内代码

`path/file.ts 函数：Foo 偏移：+24`

- `+0` = 函数签名行。
- 偏移 = 目标行号 − 签名行号。
- 连续片段：`Foo+0~+20`。

### 非函数代码

- 结构体 / 类：`Struct：Node`
- 常量：`Const：X`
- 模块：`Module：rpc`

### 调用关系

`调用方 Foo+6 ↓ 被调用方 makeNode`

### 第三方依赖

注明版本：`依赖：express@4.19.2`。

### 文末源码索引

可以给 `文件:函数:绝对行号` 方便跳转复核。正文锚点仍用符号 + 偏移。

## 2. 项目路径约定

| workspace | 源码根 | 构建产物 |
|-----------|--------|----------|
| shared | `shared/types.ts` | （无，纯类型） |
| server | `server/src/` | `server/dist/` |
| client | `client/src/` | `client/dist/` |
| cli | `cli/src/` | `cli/dist/` |
| desktop | `desktop/src/` | `desktop/build/` |

## 3. 事实红线

1. **严禁编造、臆测、空泛**。所有事实必须经 Grep / Read / 实测查证。无法证实的显式写「当前源码无法确定」或「未实测，待补」。
2. **禁止「同上 / 略 / 以此类推」替代核心内容**。
3. **图不能少**：每篇 ≥ 1 张图。逻辑流 / 报文 / 管道用 ASCII 字符图；架构用 Mermaid `flowchart`；调用用 `sequenceDiagram`；状态用 `stateDiagram-v2`；多表关系用 `erDiagram`。
4. **实测数据标注来源与日期**：写明库 / 环境实例名、日期、只读查询；无权限就写「未实测，待补」，绝不编数。
5. **未逐行阅读的反射 / 生成 / 内部实现**，显式标注「未读取，不臆测」。

## 4. 引用既有文档

本文档库聚焦源码阅读，与已有的 `docs/en/architecture/`（产品架构 deep-dive）互补：
- 产品定位与 ToS 评审 → `docs/en/architecture/00-high-level-index.md`
- 路由与 bandit 打分 → `docs/en/architecture/01-routing-and-bandit-scoring.md`
- 配额与 cooldown 引擎 → `docs/en/architecture/02-quota-and-cooldown-engine.md`
- 流式管线 → `docs/en/architecture/03-streaming-pipeline.md`
- 降级模式与故障转移 → `docs/en/architecture/04-degraded-mode-and-failover.md`
- 目录同步 → `docs/en/architecture/05-catalog-sync.md`
- 可观测性 → `docs/en/architecture/06-observability.md`