# 本轮文档同步规范

- 日期：2026-11-08。
- 源码基准：本地 `adrian`，`823c496b19f1551f373a364219d86c673391c4c5`；未拉取远端。
- 范围：`docs/adrian/sourceReader/`、`docs/adrian/topics/`；历史审计目录不改，应用源码不改。
- 用户已确认：保留四层结构，逐篇深度同步，新增13–24；两篇专题同轮核实。
- 修改前备份：`/tmp/freellmapi-docs-adrian-823c496b-before-refresh.tar.gz`，仅供本轮回滚。

## 1. 已确认的漂移与勘误

| 项 | 已确认结果 | 边界 |
|---|---|---|
| 最新行号校准基准 | `68729729` 到当前只有一次文档提交，生产树无差异 | 不能据此推断正文已准确 |
| 专题声明的旧基准 | `c45fa7ef` 到当前123次提交，五个源码树152文件、3379新增行/229删除行 | 其中包含测试；不是152个新增功能 |
| 旧记法 | 24处 `@数字`、658处 `文件:数字` | 初审按文本计数，含代码块和文末索引 |
| 显式源码路径 | 72个唯一路径均存在 | 不覆盖裸文件名歧义 |
| 10–12函数标题 | 28个标题符号能在生产树定位 | 初审未证明所在文件和偏移正确 |
| 第一层计数自相矛盾 | 01开头写74个平台、模块表写84个平台 | 必须从TypeScript AST复计，不能复制历史报告 |
| 第二层越层 | 02混入失败重试、预算、风险表和错误的步骤概括 | 保留有效信息于其所属层，不把概念伪码当真实实现 |
| 任务类型 | `routeRequest` 参数只接受 `code` / `chat` | 02旧文的analysis/creative不能保留 |
| 路由覆盖参数 | `routeRequest` 当前含末尾 `strategyOverride` | 旧函数签名必须逐项核对位置 |
| 回退函数分层 | `runFallbackLoop`包裹追踪，真正循环在`runFallbackLoopAttempts` | 不能把attempt循环的偏移贴在外层函数上 |
| 图与术语 | 16篇都没有独立文末术语章 | 没有Mermaid不代表没有ASCII图 |

## 2. 统一定位写法

正文使用：`server/src/services/router.ts` · `routeRequest+0`。

连续区间使用：`server/src/services/router.ts` · `routeRequest+8~+13`。

方法必须带类名。嵌套命名函数带父符号。匿名路由用真实注册表达式：`server/src/routes/proxy.ts` · `proxyRouter.post('/chat/completions')+9`，从注册语句首行计算。不创造源码中不存在的函数名。

定位命令从仓库根运行：

```bash
python3 docs/adrian/sourceReader/.progress/sr_tools.py locate routeRequest
python3 docs/adrian/sourceReader/.progress/sr_tools.py outline server/src/services/router.ts --top
python3 docs/adrian/sourceReader/.progress/sr_tools.py offset server/src/services/router.ts routeRequest
python3 docs/adrian/sourceReader/.progress/sr_tools.py verify docs/adrian/sourceReader
python3 -B docs/adrian/sourceReader/.progress/test_sr_tools.py
```

定位器识别字符串、正则、数组路径的HTTP路由，也识别传入命名handler的注册；这三种形态已加入测试。注册接收者支持 `xxxRouter`、工厂内局部 `router`（如 `createUpdateRouter` 内部）与 `app`，`update.ts` 的工厂局部形态是第10项测试。统计HTTP注册数必须按表达式 `name` 全匹配（get/post/…）过滤，否则 `proxyRouter.post(...).res.on('close')` 这类嵌套事件回调会被误计。注册表达式的偏移从注册行起算，命名handler的内部逻辑则引用handler自身，不能把两者混用。

定位器使用仓库已安装的TypeScript解析器，只读源文件；生产树优先，测试/脚本仅作同名搜索后备。符号行范围由AST取得，不用正则猜花括号。文件索引仅扫描Git跟踪源文件，新增未跟踪源码需显式传入outline。

## 3. 每篇的固定要求

1. 开头注明层级、日期、基准和本篇边界。
2. 先人话定位，再给列表和图，再逐函数解释；不先堆缩写。
3. 函数写职责、签名/关键入参、输出、调用方、内部分步、异常与状态副作用。
4. 主调用链有双方定位；不能仅列函数名充当解释。
5. 每篇至少一张与真实文件/符号对应的图；多表关系用ER图。
6. 文末先给源码索引与导航，再给该篇术语表。术语解释包含意思、在本项目中的用途及容易混淆的边界。
7. 只使用四种不确定性标记：`[源码未确认]`、`[源码未找到]`、`[推断]`、`[待运行验证]`。
8. 运行样例明确是契约示例还是实际响应。历史实例观察必须保留原日期；本轮不向上游发计费请求，不修改数据库、不重启。
9. 自动符号扫描不等于完成函数走读；覆盖总表与state必须明确区分。

## 4. 校验口径

- `verify`检查统一格式的符号归属和AST偏移范围、文件链接、Markdown标题/显式锚点、源码链接越界，并对散文中的路径分类。以 `/` 开头的路径形 token（如 `/v1/openapi.json`）分类为「URL或绝对路径」，不当作仓库文件引用报警；第11项测试锁死该行为及其负向对照。
- `--strict`进一步将疑似失效路径视为错误，必须人工判读输出后修复，不能用删除引用消除报警。
- 围栏内的概念图、示例链接不当作真实链接扫描。
- 工具不能证明某个偏移对应的业务解释正确，不能证明某调用会在所有分支发生，也不证明Mermaid可渲染。
- 负向对照包括：不存在符号、跨文件误归属、偏移超函数、失效文档链接和锚点。
- 最终不得用已检查篇目的结果代表未检查篇目。
