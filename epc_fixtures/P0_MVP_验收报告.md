# EPC P0 MVP 正式验收报告

| 项 | 内容 |
|---|---|
| 结论 | **PASS** |
| 验收角色 | EDA 测试验证（本 bot） |
| 验收对象 | `epc_engine` P0 MVP + `/workspace/epc_fixtures/` DEMO 夹具 |
| 日期 | 2026-10-21 22:23 CST（Asia/Shanghai） |
| 数据性质 | **合成 DEMO，非真实 PDK / Foundry 真值** |
| 编排来源 | EDA开发任务编排协调器(Top) 正式验收委托 |

---

## 0. 一页结论

| 检查项 | 结果 |
|---|---|
| 1. B_out COUNT=4950；distinct (9,11,50)；每组 50 key 齐全 | **PASS** |
| 2. B∉A 的 3 instance / 3 pvt 全字段覆盖 | **PASS** |
| 3. 两条 YAML 约束 PASS（上界 ≤1500；`-4%`→×0.96） | **PASS**（持久化浮点容差内） |
| 4. 表轴 N=5、展平 25 token、轴对齐无破损 | **PASS** |
| 5. 违规门禁非 0 退出 | **PASS**（已抽测） |
| 6. README / 文档可复现 | **PASS** |

**缺陷列表（阻塞级）：空。**

---

## 1. 环境

| 项 | 值 |
|---|---|
| OS / shell | Linux / bash（box） |
| Python | `python3` + stdlib `sqlite3`（无 sqlite3 CLI 依赖） |
| 依赖 | `pyyaml`（已安装；`pip install --break-system-packages pyyaml`） |
| 工作目录 | `/workspace` |
| A_ref | `/workspace/epc_fixtures/A_ref.db`（COUNT=40000） |
| Job YAML | `/workspace/epc_fixtures/epc_job.sample.yaml`（sha256[:16]=`3575cb2c7e46fe01`） |
| 代码 | `/workspace/epc_engine/` |
| 字典 | `/workspace/EPC_T1_数据字典.md` **v1.1** |
| 范围 | `/workspace/SRAM_Char_AI_范围说明书_T0.md` **v1 / 补丁 v1.0.1** |

---

## 2. 复现步骤（已执行）

```bash
# 若需
pip install --break-system-packages pyyaml

cd /workspace && python3 -m epc_engine /workspace/epc_fixtures/epc_job.sample.yaml
```

**实测输出摘要：**

```
[epc] A loaded: instances=20 pvts=40 keys=50 rows=40000
[epc] B lists: instances=9 pvts=11
[epc]   [PASS] #0 table_upper_bound: … before_max=1387.9; after_max=1387.9; cells_clipped=0/25
[epc]   [PASS] #1 relative_delta_vs_source: delta_pct=-4.0 → ×0.9600; … max_rel_err=0.000e+00; sample baseline0=140 → 134.4
[epc] gates: PASS — all constraints PASS
[epc] wrote 4950 rows
[epc] OK
EXIT=0
```

产物：

- `/workspace/epc_fixtures/B_out.sample.db`
- `/workspace/epc_fixtures/B_out.sample_audit.md`

与 `epc_engine/README.md`、`epc_fixtures/README.md` 描述一致。

---

## 3. 检查项证据

### 3.1 COUNT / distinct / 完备性 — PASS

用 `python3`+`sqlite3`：

| 指标 | 期望 | 实测 |
|---|---|---|
| `COUNT(*)` | 4950 | **4950** |
| `COUNT(DISTINCT instance)` | 9 | **9** |
| `COUNT(DISTINCT pvt)` | 11 | **11** |
| `COUNT(DISTINCT field_key)` | 50 | **50** |
| groups `(instance,pvt)` | 99 | **99** |
| 任一组 key 数 ≠50 | 0 | **0** |
| 各组 key 集合签名数 | 1 | **1** |

### 3.2 B∉A 外延全覆盖 — PASS

对照 `A_ref.db` 与 B 列表：

**B∉A instances（3）：**

- `HINP3TCAM128X64SWISDC`
- `HINP3TCAM256X48SWISDC`
- `HINP3TCAM384X100SWISDC`

**B∉A pvts（3）：**

- `FFGNP_0P75V_0P75V_85C`
- `SSGNP_1P05V_1P05V_M40C`
- `TT_1P05V_1P05V_M40C`

- B 库 instance/pvt 集合与 `B_instance_list.txt` / `B_pvt_list.txt` **完全一致**
- 每个新 instance × 全部 11 pvt、每个新 pvt × 全部 9 instance：均为 **50 key** → **PASS**
- 审计报告中的 B∉A 列表与上表一致

### 3.3 YAML 约束 — PASS

#### #0 `table_upper_bound`

- Locator: `HINP3TCAM512X100SWISDC × SSGNP_0P99V_0P99V_125C × tselr1_min_period`
- B 中 25 cells；`max=1387.9` **≤ 1500**
- Audit：`[PASS]`；`cells_clipped=0/25`；`before_max=after_max=1387.9`

#### #1 `relative_delta_vs_source`（`-4%` → ×0.96）

- Locator: `HINP3TCAM64X8SWISDC × TT_0P80V_0P80V_25C × tcq`
- Audit（应用时内存）：`max_rel_err=0.000e+00`；`baseline0=140 → 134.4`
- 落库后重读（经 `fmt_scalar` 两位小数序列化）：
  - `B[0]=134.40` 精确 = `140×0.96`
  - 全表 ratio ∈ **[0.959983, 0.960020]**
  - `max |B − A×0.96| = 0.004`（显示精度舍入，非语义错误）
- 判定：**PASS**（验收允许浮点容差；与 README 自检脚本一致）

### 3.4 表轴 / 展平 / 对齐 — PASS

| 检查 | 结果 |
|---|---|
| `tran_index` 长度 | **5**（例：`0.005 0.01 0.02 0.04 0.08`） |
| `load_index` 长度 | **5**（例：`0.001 0.005 0.01 0.025 0.05`） |
| 表值 key 展平 token 数 | **25**（14 个表值 key，含 `tselr1_min_period` / `tcq` 等） |
| 全部 99 组轴/表长度违规 | **0** |
| 字段总数 | **50**（与 A / 字典一致） |

### 3.5 违规门禁抽测 — PASS（已做）

原 YAML **未改动**（在 `/tmp` 副本上抽测）。

| 用例 | 改法 | EXIT | 门禁 |
|---|---|---|---|
| A | `#0` instance 改为 A 有但 **B 列表无** 的 `HINP3TCAM192X16SWISDC` | **1** | FAIL：`missing constructed value` |
| C | `#0` key 改为 `nonexistent_key_xyz` | **1** | FAIL：`missing constructed value` |

stderr 含：`[epc] FAIL: constraint gate failed (on_violation=fail_job)`。

**说明（初验当时）：** 曾记录「收紧上界不会失败 / clip-then-pass」。**→ 已由门禁修复推翻**（2026-10-21 复验：bound=1000 → EXIT 1，verify-only）。见 §7。

### 3.6 文档可复现 — PASS

- `epc_engine/README.md`：安装 pyyaml、`python3 -m epc_engine …`、期望 COUNT=4950、python 自检片段
- `epc_fixtures/README.md`：schema、规模 20×40×50、生成脚本、约束语义（`-4%`→×0.96）
- T1 v1.1 / T0 v1.0.1：与夹具规模及验收锚点一致

实测命令即 §2，与 README 一致。

---

## 4. 缺陷列表

| ID | 严重度 | 描述 | 状态 |
|---|---|---|---|
| — | — | （无阻塞缺陷） | — |

---

## 5. 残留风险 / 建议（非 FAIL）

1. **门禁失败仍写库**（初验记录）：`cli.py` 曾在 `evaluate_gates` 失败前已 `write_b_db`。**→ 已关闭（2026-10-21 复验）**：gate FAIL + `fail_job` 时不写 B.db，并清理目标路径旧库；详见 §7 / `P0_MVP_门禁复验.md`。
2. **clip-then-pass**（初验记录）：曾先 clip 再 PASS，收紧上界无法测 FAIL。**→ 已关闭（2026-10-21 复验）**：`fail_job` 下 `table_upper_bound` 为 **verify-only**（超界 FAIL，`cells_clipped=0`）；详见 §7 / `P0_MVP_门禁复验.md`。
3. **序列化舍入**：`fmt_scalar` 对 ≥100 的值保留 2 位小数，相对约束落库后与精确 ×0.96 有 ≤0.004 绝对误差；审计内存校验为 0。P1 可统一更高精度或按 key 类型格式化。
4. **数据为合成 DEMO**：不得外推为真实工艺/PDK 精度结论。

---

## 6. 签署

| 项 | 内容 |
|---|---|
| 总体结论 | **PASS** |
| 关键数字 | B_out **COUNT=4950**；distinct **(9,11,50)**；A_ref **40000** |
| 门禁抽测 | **已做**（exit 1 于缺失定位器 / 缺失 key） |
| 报告路径 | `/workspace/epc_fixtures/P0_MVP_验收报告.md` |

---

## 7. 门禁修复复验指针（2026-10-21 22:27 CST）

初验结论 **PASS** 保留不变。针对初验 **§5.1（门禁失败仍写库）** 与 **§5.2（clip-then-pass）** 的开发修复，已单独复验：

| 项 | 内容 |
|---|---|
| 复验结论 | **PASS** |
| 复验报告 | `/workspace/epc_fixtures/P0_MVP_门禁复验.md` |
| 绿 | EXIT **0**；COUNT=**4950**；`table_upper_bound` **mode=verify_only**；`-4%`→×0.96 仍 PASS |
| 红 | `bash run_red_upper_bound.sh`（bound=1000）→ EXIT **1**；目标 B.db **不存在**；FAIL audit 写出；`cells_clipped=0`（无 clip-then-pass） |
| 附加 | 预置 stale B.db 后被 **removed**；仅收紧上界亦可 FAIL |

**状态更新：** 初验 §5.1、§5.2 所列残留项视为 **已关闭**（在 `on_violation: fail_job` 语义下）。§5.3 序列化舍入与 §5.4 DEMO 性质仍为非阻塞建议项。
