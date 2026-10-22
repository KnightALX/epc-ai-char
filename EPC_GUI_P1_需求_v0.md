# EPC GUI-P1 需求 v0

| 项 | 内容 |
|---|---|
| 状态 | **v0**（Kai 开 GUI-P1；**本侧不扇出**开发/测试；编排器交接） |
| 日期 | 2026-10-22（Asia/Shanghai） |
| 基线 | GUI-P0 **PASS**：`/workspace/epc_gui/GUI_P0_验收报告.md` |
| 范围锚 | `/workspace/EPC_GUI_范围说明书_v0.md` **§5.2** + **§6 美学**（仍生效） |
| 代码 | `/workspace/epc_gui/`；引擎 `/workspace/epc_engine/`；夹具 `/workspace/epc_fixtures/` |

> P1 = 在 P0 闭环之上把「糖衣可理解、趋势可导出、hold-out 可点开、历史可回看、主题可切换」做成可验收增强。  
> **不改**引擎门禁语义；GUI **仍不内算** PASS/FAIL；DEMO 一等公民。

---

## 1. 一页结论

| 问 | 答 |
|---|---|
| 做什么 | 落实范围书 §5.2 五条 + P0 非阻塞残留中 **R1/R3/R4**；**L1 FluentWindow = Won't**（本轮） |
| 硬边界 | 门禁只读 audit/EXIT；美学续 DESIGN / FRONTEND_DESIGN；深浅主题均过反模式自检 |
| 拍板 | **无开放问**；下文推荐均 **冻结为默认** → **可直接开开发** |
| 非目标 | 沿用范围书 §7（Web / 真 PDK / GUI 训模型 / 绕过 fail_job / AI 默认美学） |

---

## 2. 范围表（Must / Should / Won't）

| ID | 项 | 级别 | 来源 |
|---|---|---|---|
| **P1-A** | 约束糖衣可视化展开 + dry-run 拒载预检 | **Must** | 范围 §5.2-1 |
| **P1-B** | T0 多 key facet；T1+T2+T3 全开；导出 PNG/CSV | **Must** | 范围 §5.2-2 |
| **P1-C** | 内嵌选跑 `eval_h3.py` / 打开 `algo_holdout_report.md` | **Must** | 范围 §5.2-3 |
| **P1-D** | job 历史列表；主题深浅色 | **Must** | 范围 §5.2-4 |
| **P1-E** | 薄 API `run_job`（可选抽出） | **Should** | 范围 §5.2-5；门禁仍只读 audit |
| **P1-R1** | GUI venv/`requirements.txt` 补齐 `joblib`/`scikit-learn`（+ README 一句） | **Must** | P0 残留 R1 |
| **P1-R3** | `audit_parse` 覆盖 P2 G1/G3 短语（未知可保留但尽量解析；**未知≠绿** 不变） | **Must** | P0 残留 R3 |
| **P1-R4** | T1 默认 `seed_from_A`；外推点继续明示可接受误差 | **Must** | P0 残留 R4 / L2 |
| **P1-L1** | 改顶层为 `FluentWindow` | **Won't** | P0 L1：仅当 offscreen 不 abort 才评估；本轮保持 `QMainWindow` + README 说明 |
| — | 改引擎门禁 / schema / 真工艺文案 | **Won't** | 硬约束 |

---

## 3. 页面与行为改动

### 3.1 Page A · 输入配置（P1-A, P1-D, P1-R1）

| 能力 | 验收要点 |
|---|---|
| **糖衣展开** | 对 YAML 中 `relative_improve_vs_source`：只读表展示展开后的原子 `relative_delta_vs_source` 行（instance×pvt×key×δ/族），并显示 `expanded_constraint_count` / `sugar_origin`。实现：**调用引擎既有展开**（`epc_engine.job.load_job` 或等价只读 API），**禁止** GUI 自写一套展开规则 |
| **dry-run 拒载预检** | 按钮「预检」：不跑构造、不写 B.db；加载/校验 YAML（含 mode/operator 冲突、糖衣拒载、缺角覆盖等引擎会拒的项）。成功 → 绿字摘要；失败 → 展示引擎/校验异常原文，**不**改成 GUI 自造错误码 |
| **job 历史** | 每次成功「运行」或「另存」追加一条：时间、yaml 路径、mode、EXIT、audit 路径、db 路径（若有）。列表可点选 → 回填表单或仅打开该次 audit/db。持久化建议 `~/.epc_gui/job_history.json` 或 `epc_gui/state/`（DEMO 可写 `/workspace/epc_gui/state/`） |
| **依赖** | `requirements.txt` 含引擎运行依赖；干净 venv `pip install -r` 后 sample + residual 路径可内嵌 Run |

### 3.2 Page B · 输出预览

| 能力 | 验收要点 |
|---|---|
| 保持 P0 | instance/pvt/key 矩阵预览 |
| P1 轻增（Should） | 从历史条目一键打开对应 db；导出当前切片 CSV（可与 Page C 导出共用服务） |

### 3.3 Page C · 数据对比（P1-B, P1-C, P1-R3, P1-R4）

| 能力 | 验收要点 |
|---|---|
| **T0 多 key facet** | 用户多选 ≥2 key 时：按 key **分面**（上下/网格多图）或明确图例「key×pvt」；P0 单 key+多 PVT 行为保持 |
| **T1 全开** | 默认对照源改为 **`seed_from_A`**（同 instance×pvt×key 在 A/源库的 seed 或已有组）；max_rel 期望 &lt;1e-9。若用户仍选手动 locator 且为外推点 → 保留「外推点可能≠seed」提示，**不**把外推误差当 H2 失败谎报 |
| **T2 全开** | 子页/折叠区：展示 hold-out / Δ 热力或读入 `eval_h3` / h3_report 中的 p95 数字；**数值来自脚本或报表，GUI 不重算门禁阈值** |
| **T3 全开** | 有相对/糖衣时：固定抽 ≥1 speed + ≥1 power（若存在）柱状 baseline vs B vs 目标；标 `baseline_source`；与 G2 口径一致的展示（仍不内算 gate） |
| **导出** | 「导出对比」→ 当前 T0（及可选 T1 表）**PNG**（图）+ **CSV**（容量、pvt、key、typical）；路径可选，默认 `epc_gui/exports/` |
| **eval_h3 / hold-out** | 按钮：① 子进程跑 `/workspace/epc_fixtures/p2/eval_h3.py`（或文档钉死的入口），日志进面板，结束后提示打开生成的 `h3_report.md`；② 「打开 hold-out 报表」直接打开 `/workspace/epc_fixtures/algo_holdout_report.md`（系统/内嵌 Markdown 只读均可） |
| **audit 灯** | 增强解析：P2 audit 中 G1/G3（及既有 H1–H3 / H3-hard）尽量出 PASS/FAIL/SKIP；解析不到 → **未知（MuteFog）**，禁止当绿 |

### 3.4 壳 · 主题（P1-D）

| 能力 | 验收要点 |
|---|---|
| 深/浅切换 | 设置或顶栏切换；**两套** token 写入 `DESIGN.md`（浅色不得滑向奶油+陶土等反模式） |
| 持久化 | 记住上次主题 |
| 截图 | 深、浅各至少：配置页 + 对比页（含 T0）各 1 张 → `screenshots/p1_*` |

### 3.5 薄 API（P1-E · Should）

若开发抽出 `epc_engine` 可 import 的 `run_job(path) -> exit_code`（或 GUI `services` 薄封装）：

- GUI Run 可改调该 API，**但** PASS/FAIL 展示仍只来自 audit 文件 + EXIT。  
- 无强制：子进程 CLI 保持可用即算 P0 回归绿；P1-E 不阻塞 Must 项。

---

## 4. 美学（续 §6）

| 项 | P1 要求 |
|---|---|
| 规范 | `/workspace/epc_gui/FRONTEND_DESIGN.md` |
| 计划 | 更新 **`DESIGN.md`**：补充浅色 token + P1 新增控件（历史列表、facet、导出）的布局原则；改前自检反模式 |
| 验收 | 新截图；深浅均过 U6 同类审查 |
| 禁止 | 为「浅色」引入奶油底/陶土强调等清单项 |

---

## 5. 验收 U 表（GUI-P1）

| # | 项 | 标准 |
|---|---|---|
| **U0** | P0 回归 | sample / P1 绿 / P2 Geom 绿 / H3-hard 红 行为与 P0 报告一致；门禁仍只读 |
| **U1** | 糖衣展开 | 加载 `p1/epc_job.p1_improve_green.yaml`：展开行数 = 引擎 `expanded_constraint_count`；与 CLI/load_job 一致 |
| **U2** | dry-run | 对 `p1_r1_vague` 或 mode 冲突 YAML：预检失败且**不写** db；对绿 YAML：预检通过 |
| **U3** | T0 facet | ≥2 key × ≥2 PVT：出现分面或多系列图例；CSV 导出含 key 列 |
| **U4** | T1 seed_from_A | 默认路径 max_rel &lt; 1e-9（DEMO）；外推手动点仍有提示 |
| **U5** | T2+T3 | T2 能展示报表/脚本数字或热力；T3 在 sample/P1 绿上可见 speed+power 柱 |
| **U6** | 导出 | 一键产出 PNG+CSV，文件非空且与当前图选择一致 |
| **U7** | eval_h3 / hold-out | 能启动 eval_h3（EXIT 记入日志）并打开 `algo_holdout_report.md` |
| **U8** | 历史 | ≥2 次运行后列表 ≥2 条；点选可回到对应 audit/上下文 |
| **U9** | 主题 | 深↔浅切换无崩溃；浅色截图未命中 §6 反模式 |
| **U10** | R1 依赖 | 干净 venv 仅按 `requirements.txt` 安装后，内嵌 residual 相关 job 不再因缺 joblib/sklearn 失败 |
| **U11** | R3 解析 | P2 Geom 绿 audit：G/H 灯尽量非「未知」；任一未知仍 ≠ 总体绿 |
| **U12** | 美学 | 更新后 `DESIGN.md` + P1 截图齐；对照 FRONTEND_DESIGN |

---

## 6. Fixtures / 联调路径

| 用途 | 路径 |
|---|---|
| 糖衣绿 | `epc_fixtures/p1/epc_job.p1_improve_green.yaml` |
| 糖衣拒载 | `epc_fixtures/p1/epc_job.p1_r1_vague.yaml` |
| sample / T3 | `epc_fixtures/epc_job.sample.yaml` |
| P2 / H 灯 | `epc_fixtures/p2/job_corner_fill_green.yaml` |
| 红 / 未落盘 | `epc_fixtures/p2/job_corner_fill_residual_h3hard.yaml` |
| eval_h3 | `epc_fixtures/p2/eval_h3.py` → `h3_report.md` |
| hold-out | `epc_fixtures/algo_holdout_report.md` |

Smoke：扩展 `scripts/smoke_headless.py`（或 `smoke_p1.py`）覆盖 U1/U2/U4/U10 中可 headless 部分。

---

## 7. 对 Kai 的冻结推荐（无开放拍板）

| 主题 | 冻结 |
|---|---|
| FluentWindow | **本轮不做**（Won't）；保持 QMainWindow + 说明 |
| 薄 API | **Should**：有则用，无则不阻塞 |
| T1 默认 | **`seed_from_A`** |
| 历史存储 | 本地 JSON；不做云同步 |
| 浅色 | 必须进 DESIGN.md；禁止反模式色 |

若 Kai 无异议，编排器可 **直接开开发**。

---

## 8. 交付物（开发阶段）

| 产物 | 说明 |
|---|---|
| 更新后的 `/workspace/epc_gui/` | P1 功能 |
| `DESIGN.md` 浅色 + P1 布局补丁 | 美学硬项 |
| `screenshots/p1_*` | 深浅 × 关键页 |
| `GUI_P1_验收自测.md`（开发） | 对照 U0–U12 |
| （测试方）正式验收报告 | 编排器另派，**本需求侧不扇出** |

---

## 9. 一页结论

- GUI-P1 Must：糖衣展开 + dry-run、T0 facet + T1–T3 全开 + 导出、eval_h3/hold-out 入口、历史、深浅主题、R1/R3/R4。  
- Won't：FluentWindow 本轮、改引擎门禁。  
- **无待 Kai 拍板项 → 可直接开开发。**  

**本文路径**：`/workspace/EPC_GUI_P1_需求_v0.md`
