# EPC GUI — Virtuoso 清新专业审美 · 需求 v0

**状态：** 2026-10-23 Kai 口述拍板开改（「不太喜欢 TEXT 下面有文本突出颜色」「清新干净」「主流 EDA / 类似 Cadence Virtuoso」）。
**范围：** 仅视觉 / QSS / token / 图表配色与状态着色策略；**不改**业务逻辑、门禁语义、对比页 IA、i18n key 结构（文案内容可微调语气）。
**覆盖：** `theme.py`、`DESIGN.md`、必要的 page 内 `setStyleSheet`、pyqtgraph 系列色；三页 + 壳。

---

## 问题（用户原意）

1. 标题 / 区段下的辅助说明、读数、侧栏短句不要用醒目强调色（琥珀 / 青绿 / 玫红大面积上字）。
2. 整体偏「探针台琥珀」营销感，不够主流 EDA 工具的冷静专业感。
3. 目标参考：**Cadence Virtuoso** 一类 — 冷灰基座、克制蓝强调、状态色仅用于真状态。

---

## Must

### M1 · 辅助文本去强调色
- 凡 `Mute` / 区段说明 / 对话框旁注 / 图一侧栏 `对齐`·`中位差`·`均值差` / `约束达标 n/m`（非 PASS·FAIL 灯）一律 **中性灰**（`MuteFog` / `Chalk`），**禁止** TraceAmber / PvtCyan / PassTeal / FailRose 上色。
- `audit` 摘要框内正文与标题同色阶，**不对** `PASS`/`FAIL` 单词做彩色高亮或底色块（可用字重；彩色留给左侧灯 + 一句总状态）。

### M2 · Virtuoso 冷静色板（替换现 TraceAmber 主强调）
暗色默认（Virtuoso CIW 感）：

| Token | 建议 Hex | 角色 |
|---|---|---|
| InkWell | `#1E1E1E`～`#252526` | 画布 |
| PanelSteel | `#2D2D30` | 轨 / 组 |
| RuleLine | `#3E3E42` | 发丝线 |
| Chalk | `#D4D4D4` | 主文字 |
| MuteFog | `#9A9A9A` | 次文字 |
| AccentBlue | `#4A90D9`（或 `#3B82C4`） | **唯一**强调：选中导航、焦点环、主按钮、构造曲线 |
| PassTeal | `#6A9F6A`（克制绿） | **仅** PASS 灯 / 真通过态 |
| FailRose | `#C75B5B`（克制红） | **仅** FAIL 灯 / 真失败态 |
| PlotCanvas 暗 | = InkWell；浅 | `#FFFFFF`（Kai 既有截图需求保留） |

浅色：冷灰纸 + 同系 AccentBlue（加深以满足对比），禁止奶油+陶土。

- 删除「琥珀为主强调」；旧名 `TraceAmber` 可映射为 `AccentBlue` 或保留别名但色值改蓝。
- PVT 多线色：蓝灰族 4～6 色，去掉高饱和紫/铜闪光感。

### M3 · 壳与控件
- 圆角 ≤2px；少阴影；GroupBox / 发丝分隔，不堆软卡片。
- 导航选中：左侧细蓝条或淡蓝底 + 正文色，**不要**整钮金色字。
- Primary 按钮：AccentBlue 底或描边，勿琥珀填充。
- EXIT / 已落盘：中性描边 + mono 字；**不要**整块绿底「突出色块」。真通过只靠灯 + 短词「通过」。

### M4 · 图表
- 图一柱：参考=灰、构造=AccentBlue、目标/约束线=更深灰或虚线；勿三色高饱和并排抢戏。
- 图二：参考=灰虚线，构造=AccentBlue 实线。
- 浅色图区背景仍 `#FFFFFF`。

### M5 · 文档与回归
- 重写 `DESIGN.md` token 表与原则（行业：Virtuoso/主流 EDA 冷静专业；仍避开 FRONTEND_DESIGN 反模式里的奶油陶土 / 酸绿黑底 / SaaS 圆卡片）。
- `smoke_p1`/`smoke_p2` EXIT 0；DESIGN token 断言若绑死旧琥珀 hex，一并更新。
- 截图更新暗/浅对比页各至少 1 张到 `epc_gui/screenshots/`。

## Should
- Fluent `ThemeColor` 指到 AccentBlue。
- README 一句说明审美基线：Virtuoso-like cool gray + blue.

## Won't
- 不换 FluentWindow；不改 PyQt5 栈；不改门禁/对比算法；不做像素级 Cadence 皮肤仿冒（商标/图标）。

## 验收
- U0：无辅助说明/读数用强调色（目视三页）。
- U1：主强调为蓝而非琥珀；PASS/FAIL 色仅灯与总状态。
- U2：smoke_p1/p2 EXIT 0。
- U3：浅色 PlotCanvas `#FFFFFF` 仍成立。
