# GUI Fluent 全量换壳 — 设计规格

日期：2026-11-24
状态：已获用户批准（范围 A · 全量换壳 / 默认浅色保留切换 / 独立设置页 / 执行方案 A1）
上游参考：https://github.com/zhiyiYo/PyQt-Fluent-Widgets（qfluentwidgets 默认窗口与默认风格）

> 注意：本仓库当前不是 git 仓库，本规格无法按惯例 commit；在推入 git 托管时应随首次提交一并入库。

## 1. 背景与目标

用户对当前 GUI 观感不满意。当前实现为「原生 QWidget + Fusion + 手写 QSS」的自绘 Virtuoso 风（色板 #1E1E1E/#4A90D9、圆角 ≤2px），与 PyQt-Fluent-Widgets 官方默认观感（#F5F5F5 浅色底/#202020 深色底、#60CDFA 强调色、圆角 8px、NavigationInterface 侧栏）是两套设计语言。

目标：**按 qfluentwidgets 的默认窗口（FluentWindow）与默认风格重做 GUI**，达到官方 demo 的完成度。

## 2. 已锁定的约束（用户问答结论，逐字）

1. 范围：A · 全量换壳 —— FluentWindow + NavigationInterface + 三页控件全 Fluent 化。
2. 主题：**默认浅色**，保留浅/深切换能力。
3. 设置入口：独立「设置」导航页（SettingCard：语言 zh/en + 主题 浅/深），删除旧顶部设置条。
4. 执行方案：A1 · 直换 + spike 定夺（见 §5）。

## 3. 核心承诺：换皮肤不换逻辑

`epc_gui/services/` 全部零改动（job_runner 的 QProcess 子进程、audit_parse 正则解析、db_reader、trend、yaml_io、compare_views、export_compare、history、run_job_api、sugar）。三页业务行为（载入 YAML → 预检 → 运行 → 预览 → 对比）保持不变。引擎层（epc_engine/）零改动。全量 pytest（79 例）零影响。

唯一允许的 services 接触：若 smoke 断言需要读取页面内部状态而现有 API 不足，优先在页面对象上提供只读访问方法，不改 services 行为。

## 4. 架构

```
FluentWindow (MainWindow 重写)
├─ NavigationInterface（左上，4 项，FluentIcon）
│    ├─ 配置 ConfigPage（重建为 Fluent 控件）
│    ├─ 预览 PreviewPage（重建）
│    ├─ 对比 ComparePage（重建）
│    └─ 设置 SettingsPage（新增）
└─ QStackedWidget（addSubInterface 路由）
```

- 窗口标题「EPC Desktop」与初始尺寸保持不变。
- `epc_gui/pages/settings_page.py` 新增：SettingCardGroup + ComboBoxSettingCard（语言 zh/en）+ SwitchSettingCard（「深色模式」开关；开=DARK、关=LIGHT）。切换立即生效（qconfig.setTheme + set_locale(emit=True)）。
- 三页重建组件映射：分组容器 → CardWidget；主操作 → FilledPushButton/PrimaryPushButton；次要操作 → PushButton；选择器 → ComboBox；文本输入 → LineEdit；表格 → TableWidget（Fluent 样式注入）；状态灯 → IconWidget（FluentIcon.ACCEPT / CLOSE）+ InfoBadge。

## 5. 主题与 headless 策略（spike 门槛）

`epc_gui/theme.py` 重写：

- 删除全部手写 QSS 与自绘 token（约 400 行）。
- `apply_theme(app, name)` 薄封装：`qconfig.setTheme(Theme.LIGHT | Theme.DARK)` + `setThemeColor("#60CDFA")`。
- 默认主题 = LIGHT（settings 缺省 `theme="light"`；历史 settings 里 `dark` 值的迁移策略：首次启动时若读到旧值 `dark` 则照常应用，不强制）。

**Spike（实施第一步，先于任何页面改动）**：安装 qfluentwidgets 后，本机 Windows `QT_QPA_PLATFORM=offscreen` 下创建最小 FluentWindow 并退出，记录是否崩溃。

- 结论 A（稳）：不写任何降级代码。
- 结论 B（崩）：新增薄降级路径 —— `run()` 检测 offscreen/`EPC_GUI_HEADLESS` 时，用最小 QMainWindow 包裹同一批页面对象（页面组件仍为 Fluent 控件），正常桌面路径始终用 FluentWindow。冒烟断言两种壳下保持一致（页面级断言，不依赖壳）。

启动失败行为保留现状：捕获异常 → 报错 + 非零退出。

## 6. 删除清单（The Algorithm 步骤 2）

- `theme.py`：全部 QSS 常量、`_repolish`/`set_label_state`/`restyle` 辅助（由 Fluent 控件原生状态取代）。
- `app.py`：`_rgba` 助手、手写导航高亮 QSS、旧顶部 Settings strip（语言/主题下拉）。
- `config_page.py` / `compare_page.py`：所有 objectName+QSS 状态样式残留随页面重建自然删除。
- `epc_gui/requirements.txt`：qfluentwidgets 从注释的 optional 转为正式依赖并钉版本。

## 7. 测试策略（随设计同步）

1. 更新 `smoke_p1.py` 中旧 DESIGN 浅色 token 断言（EEF1F5/2E6BB0/AccentBlue 检查）→ 新断言：默认浅色生效（qconfig.theme == LIGHT）、主题可切（setTheme 往返）、导航 4 项存在且文案正确（zh/en）。
2. `smoke_headless.py` / `smoke_p2.py` 行为断言不动（行为未变）；如遇壳相关崩溃按 §5 结论 B 处理。
3. `capture_screenshots.py` / `capture_p1.py` / `capture_p2.py` 重跑，重生成全部 19 张截图（新观感证据，供用户目视）。
4. 引擎 pytest 79 例全量复跑必须全绿；`run_all_tests.ps1` 与 `.github/workflows/epc-ci.yml` 的 GUI 依赖安装行补 qfluentwidgets（钉版本），其余不动。
5. 终验：真实桌面启动（进程 + MainWindowTitle/MainWindowHandle 证据），用户目视截图确认。

## 8. 文档更新

- 本规格：`docs/superpowers/specs/2026-11-24-gui-fluent-redesign-design.md`。
- `epc_gui/DESIGN.md`、`epc_gui/FRONTEND_DESIGN.md` 头部加「superseded by <本规格路径>」标注（不删历史）。
- `epc_gui/requirements.txt`：`PyQt-Fluent-Widgets` 正式依赖 + 钉版本。

## 9. 验收标准（Definition of Done）

1. 桌面实启：FluentWindow + 默认浅色 + 四导航（配置/预览/对比/设置）。
2. 设置页：语言 zh/en、主题浅/深切换即时生效。
3. 三套 headless 冒烟（smoke_headless/p1/p2）EXIT=0。
4. 全量 pytest 79 例全绿。
5. 19 张截图重生成，用户目视通过。
6. CI workflow 与 run_all_tests.ps1 含 qfluentwidgets 依赖。

## 10. 已知风险与缓解

| 风险 | 缓解 |
| --- | --- |
| FluentWindow 在 offscreen 崩溃（历史 Linux xvfb 记录） | §5 spike 前置；结论 B 有降级壳设计 |
| 页面重建引入行为回归 | services 零改动 + 三套 headless 冒烟行为断言不动 |
| qfluentwidgets 与 PyQt5 5.15.2 版本兼容 | 安装时钉版本并跑 spike 验证 |
| smoke_p1 旧 token 断言失效 | 属设计内变更，§7.1 同步更新 |
