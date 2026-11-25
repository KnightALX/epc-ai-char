# EPC《双新 (geom+PVT) hold-out 切片 / LON》正式验收报告

| 项 | 内容 |
|---|---|
| 结论 | **PASS**（阻塞缺陷：无） |
| 日期 | 2026-10-22 15:54 Asia/Shanghai |
| 规格 | `/workspace/EPC_双新_holdout切片_需求_v0.md` **v0**（Kai：Q1=A 30 折笛卡尔；Q2=A 报表 Must + 硬 EXIT 可关、**无 stamp**；Q3=`≤`） |
| 引擎 | `/workspace/epc_engine/`（验收**未改**产品代码；仅写入本报告于 fixtures） |
| 验收方 | 独立复跑 `run_lon_holdout_suite.sh` + U0–U5 抽检（**非盲签**开发自测 / 非复用开发声称数字） |
| 开发自测 | `/workspace/epc_fixtures/LON_自测.md`（仅参考） |
| 解耦 | 与 AB-hard stamp / Op-Geom H3-hard / `eval_h3` **并列、不缠死** |
| DEMO | fixture ≠ 真 PDK |

---

## 1. 一键 suite（独立复跑）

```bash
bash /workspace/epc_fixtures/run_lon_holdout_suite.sh
# → SUMMARY pass=8 fail=0 ；SUITE_EXIT=0
PYTHONPATH=/workspace python3 -m epc_engine.lon_holdout --require-lon-hard
# → EXIT 0；LON-hard PASS（含于 suite U2）
```

### Suite 摘录

```text
======== LON hold-out suite ========
=== U3 LON-hard gate logic ===
lon_gate_logic PASS
OK U3_gate_logic
=== U5 mock red (hard EXIT) ===
mock_red EXIT 3
OK U5_mock_red
=== U1 protocol purity (1 fold) ===
purity PASS HINP3TCAM64X8SWISDC TT_0P80V_0P80V_25C n_cells 104
OK U1_protocol_purity
=== U2 green LON report (30 folds) ===
[lon] A=/workspace/epc_fixtures/A_ref.db instances=20 pvts=40 folds=30 protocol=lon_v0
[lon] LON p95 baseline(idw)=0.311677 selected=0.104781 n=3120 le_idw=True
[lon] gate LON-hard=PASS
[lon] report → /workspace/epc_fixtures/algo_holdout_dual_new_report.md
green LON p95_selected=0.104781 p95_idw=0.311677
OK U2_green_report
=== U4 anti-impersonation ===
U4 no corner/H3 evidence in lon_holdout code PASS
OK U4_no_eval_h3
=== report mutual links ===
OK mutual_report_links
=== U0 sample residual ===
… ab_hard: PASS … writing B.db → …/B_out.sample.db
OK U0_sample
=== no LON stamp contract ===
OK no_lon_stamp
======== SUMMARY pass=8 fail=0 ========
```

| 计数 | 值 |
|---|---|
| pass | **8** |
| fail | **0** |
| SUITE_EXIT | **0** |

### 本轮独立测得（绿路径）

| 量 | 独立复跑值 | 开发声称 | 一致？ |
|---|---|---|---|
| p95_selected | **0.104781** | 0.104781 | 是 |
| p95_idw_nn | **0.311677** | 0.311677 | 是 |
| n_cells | **3120** | 3120 | 是 |
| n_folds | **30** | 30 | 是 |
| 比较 | 0.104781 ≤ 0.311677 → **PASS** | — | — |
| 协议 id | `lon_v0` | — | — |
| 报表生成时刻 | 2026-10-22 **15:53:39 CST** | — | 本轮 suite 重写 |

旁路报表：`/workspace/epc_fixtures/algo_holdout_dual_new_report.md`  
互链：`algo_holdout_report.md` § Dual-new / LON ↔ dual_new 报表。

---

## 2. U0–U5 证据表

| # | 项 | 结论 | 证据 |
|---|---|---|---|
| **U0** | 回归 | **PASS** | **AB-hard suite** 独立复跑：`SUMMARY pass=8 fail=0`，SUITE_EXIT **0**。**sample** residual：EXIT **0**，落盘 `B_out.sample.db`，audit `ab_hard: PASS`。**约束绿** `p1_improve_green`：EXIT **0**，G3=16，约束门 PASS。**约束红**：R1 vague EXIT **2**（拒载）；R2 proxy forbid EXIT **1**。**P2 idw 绿** `job_corner_fill_green`：EXIT **0**，COUNT=2000，`H3-hard SKIP (backend=idw_nn)`。**P2 residual Geom H3 红不变**：`job_corner_fill_residual_h3hard` EXIT **1**、**无** `out_geom_residual_h3hard.db`；audit `h3_hard: FAIL`，p95_sel≈0.02632 > p95_idw≈0.00767（与既有加固报告一致）。**无** `*.lon_hard.json` stamp。 |
| **U1** | 协议纯度 | **PASS** | 单折抽检 `LOI_INSTANCES[0]×LOP_PVTS[0]` = `HINP3TCAM64X8SWISDC` × `TT_0P80V_0P80V_25C`：`train_has_held_inst=False`，`train_has_held_pvt=False`，`train_n_instances=19`，`train_n_pvts=39`；`test_locators` 共 8，**全部** `(I_h,P_h,*)`；本折 n_cells=**104**。代码路径：`eval_lon_fold` 仅对 held 交叉点 `add` 误差，不并入 LOI/LOP 态 cell。 |
| **U2** | 绿报表 | **PASS** | 全量 30 折：两路 p95 **有限**（0.104781 / 0.311677）；折数=**30**；折名单与 `LOI_INSTANCES×LOP_PVTS` 笛卡尔 **逐项一致**（独立 `folds == expected`）。报表含 Summary / Per-key / purity sample / 协议 id=`lon_v0`；与 LOI/LOP 报表互链。 |
| **U3** | 比较 `≤` | **PASS** | `evaluate_lon_hard_gates(0.1,0.1)` → **PASS**（equality）；`(0.2,0.1)` → **FAIL**；`(0.05,0.1)` → **PASS**；`detail.compare=='<='`，`protocol=='lon_v0'`。硬门旗标：`--require-lon-hard`（默认开）在 mock `p95_sel=0.99 > p95_idw=0.10` 时 EXIT **3**；同 mock 加 `--no-require-lon-hard` → EXIT **0**（仍写报表）。 |
| **U4** | 反冒充 | **PASS** | `lon_holdout.py` 去掉 docstring/注释后 **无** `eval_h3` / `h3_hard` / `modes.h3`；AST import 仅 `idw_nn` / `train_lib` / `source` 等，**不** import 四角/H3。Suite 项 `U4_no_eval_h3` OK。与 `run_ab_hard_suite` / `run_p2_suite` 并列、不共享协议实现。 |
| **U5** | 红（S3） | **PASS** | mock `evaluate_lon_hard_gates(0.99, 0.10)` → FAIL；suite 断言硬 EXIT 路径 rc=**3**（`OK U5_mock_red`）。CLI mock FAIL + `--require-lon-hard` → EXIT **3**。 |

Should（LON-S* 已覆盖硬门与红夹具）不挡；Won't（stamp / 真库 / GUI / 四角冒充）未当缺陷。

---

## 3. 关键 EXIT / 行为一览（本轮独立）

| 场景 | EXIT | 要点 |
|---|---|---|
| LON suite 全绿 | **0** | pass=8 fail=0 |
| LON CLI `--require-lon-hard`（现行 residual） | **0** | p95_sel 0.104781 ≤ p95_idw 0.311677；n=3120；folds=30 |
| LON mock FAIL + `--require-lon-hard` | **3** | 硬门红 |
| LON mock FAIL + `--no-require-lon-hard` | **0** | 旗标可关；报表仍写 |
| AB-hard suite | **0** | pass=8 |
| sample residual | **0** | B.db 有；`ab_hard: PASS` |
| P1 约束绿 | **0** | G3=16 |
| P1 R1 vague | **2** | 拒载 |
| P1 R2 proxy forbid | **1** | 不通过 |
| P2 idw corner green | **0** | COUNT=2000；`H3-hard SKIP` |
| P2 residual Geom H3-hard | **1** | 无 out db；`h3_hard: FAIL` |

---

## 4. 截图 / 产物清单

| 产物 | 路径 |
|---|---|
| 旁路 LON 报表（本轮重写） | `/workspace/epc_fixtures/algo_holdout_dual_new_report.md` |
| LOI/LOP 互链主报表 | `/workspace/epc_fixtures/algo_holdout_report.md` |
| LON suite 脚本 | `/workspace/epc_fixtures/run_lon_holdout_suite.sh` |
| 协议实现 | `/workspace/epc_engine/lon_holdout.py` |
| 本验收报告 | `/workspace/epc_fixtures/双新_holdout切片_验收报告.md` |

无 GUI；无截图要求。

---

## 5. 已知限制 / 非阻塞

1. **Should 全量红夹具**：suite 用 gate-logic mock 验证硬 EXIT（S3），未另造劣化模型重训 30 折——符合「红夹具」薄口径，不挡 PASS。  
2. **无 LON stamp**（Won't / Kai Q2）：在线 job **不**重跑 30 折 LON；与 AB stamp 解耦。  
3. **耗时**：全量 30 折在争核时可达十余分钟；空闲约 1–2 min（与开发自测量级一致）。验收建议串行跑 suite，避免与 AB/P2 并行打满 CPU。  
4. **DEMO≠PDK**：`A_ref.db` 为合成 fixture，数字不可当 foundry 标定。

---

## 6. 结论

**PASS**。U0–U5 无失败项；独立复跑 LON suite `pass=8`；绿路径 p95_sel=**0.104781** ≤ p95_idw=**0.311677**，n=**3120**，folds=**30**；硬门 `≤` / equality / 旗标可关 / 反冒充均核过；AB-hard 与 Geom H3 红行为未回归。

