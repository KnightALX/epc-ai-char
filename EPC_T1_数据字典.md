# EPC T1《数据字典 / Schema》

| 项 | 内容 |
|---|---|
| 状态 | **v1.1**（对照扩容后官方 DEMO 夹具） |
| 范围说明书 | `/workspace/SRAM_Char_AI_范围说明书_T0.md` **v1 / 补丁 v1.0.1** |
| 官方 DEMO 夹具 | `/workspace/epc_fixtures/`（**合成数据，非 PDK / 非 Foundry 真值**） |
| 金标实库 | `/workspace/epc_fixtures/A_ref.db` |
| 日期 | 2026-10-21（Asia/Shanghai） |

---

## 0. DEMO 规模（验收锚点）

| 轴 | A_ref | B 目标列表 |
|---|---|---|
| instance | **20**（全部 option=`SWISDC`） | **9**（其中 **3** ∉ A） |
| pvt | **40** | **11**（其中 **3** ∉ A） |
| field_key | **50**（每组齐全） | 同 A（`all_from_source`） |
| 表轴 N | **5**（5×5=25 cells，行主序） | 同左 |
| `COUNT(*)` | **40_000** (=20×40×50) | 引擎跑通后满表 **9×11×50 = 4_950** |

边角几何覆盖：`64X8` / `512X8` / `64X100` / `512X100`。

---

## 1. 物理 SQLite Schema

```sql
CREATE TABLE char_data(
  instance  TEXT,
  pvt       TEXT,
  field_key TEXT,
  value     TEXT,
  PRIMARY KEY(instance, pvt, field_key)
);
```

| 列 | 含义 |
|---|---|
| `instance` | 须可被 §3 正则解析；DEMO 后缀均为 `SWISDC` |
| `pvt` | 见 §4 |
| `field_key` | 见 §5（50 枚举） |
| `value` | 标量，或空白分隔展平 N×N（DEMO **N=5**） |

---

## 2. value 形态与表还原

| value_kind | 条件 | 规则 |
|---|---|---|
| `vector_axis` | `tran_index` / `load_index` | 长度 = N（DEMO=5） |
| `matrix_flat` | 表值 key 且 token 数 = N² | **行主序** `idx=i*N+j`，**i=tran，j=load** |
| `scalar` | 单 token | float 字符串 |

硬规则：同 `(instance,pvt)` 两轴长度相等；表值长度=N²；否则拒收。写回单空格连接。

DEMO 轴例：`tran_index = 0.005 0.01 0.02 0.04 0.08`。

---

## 3. Instance 解析

```
^(?P<vendor>HI)(?P<process>NP3)(?P<family>[A-Z]+?)(?P<depth>\d+)X(?P<width>\d+)(?:M(?P<mux>\d+))?(?P<options>[A-Z0-9]+)$
```

DEMO：`family=TCAM`，`options=SWISDC`，本夹具无 mux。

### 3.1 A_ref 20 instance

- `HINP3TCAM128X32SWISDC`
- `HINP3TCAM128X72SWISDC`
- `HINP3TCAM128X8SWISDC`
- `HINP3TCAM192X16SWISDC`
- `HINP3TCAM192X64SWISDC`
- `HINP3TCAM256X100SWISDC`
- `HINP3TCAM256X32SWISDC`
- `HINP3TCAM256X8SWISDC`
- `HINP3TCAM384X16SWISDC`
- `HINP3TCAM384X48SWISDC`
- `HINP3TCAM512X100SWISDC`
- `HINP3TCAM512X32SWISDC`
- `HINP3TCAM512X64SWISDC`
- `HINP3TCAM512X8SWISDC`
- `HINP3TCAM64X100SWISDC`
- `HINP3TCAM64X32SWISDC`
- `HINP3TCAM64X64SWISDC`
- `HINP3TCAM64X8SWISDC`
- `HINP3TCAM96X16SWISDC`
- `HINP3TCAM96X48SWISDC`

### 3.2 B.instance_list（9）

- `HINP3TCAM64X8SWISDC`
- `HINP3TCAM64X100SWISDC`
- `HINP3TCAM128X32SWISDC`
- `HINP3TCAM256X32SWISDC`
- `HINP3TCAM512X8SWISDC`
- `HINP3TCAM512X100SWISDC`
- `HINP3TCAM128X64SWISDC`
- `HINP3TCAM256X48SWISDC`
- `HINP3TCAM384X100SWISDC`

**∉ A（3）：** `HINP3TCAM128X64SWISDC`, `HINP3TCAM256X48SWISDC`, `HINP3TCAM384X100SWISDC`

---

## 4. PVT 解析

`{CORNER}_{V1}_{V2}_{TEMP}`；电压 `(\d+)P(\d+)V`；温度 `M?(\d+)C`（`M`→负温）。

### 4.1 A_ref 40 pvt（全枚举）

- `FFGNP_0P675V_0P675V_25C`
- `FFGNP_0P675V_0P675V_M40C`
- `FFGNP_0P80V_0P80V_125C`
- `FFGNP_0P80V_0P80V_25C`
- `FFGNP_0P80V_0P80V_M40C`
- `FFGNP_0P90V_0P90V_25C`
- `FFGNP_0P99V_0P99V_125C`
- `FFGNP_0P99V_0P99V_25C`
- `FFGNP_0P99V_0P99V_M40C`
- `FFGNP_1P05V_1P05V_125C`
- `FFGNP_1P05V_1P05V_25C`
- `FFGNP_1P05V_1P05V_M40C`
- `SSGNP_0P675V_0P675V_0C`
- `SSGNP_0P675V_0P675V_125C`
- `SSGNP_0P675V_0P675V_25C`
- `SSGNP_0P675V_0P675V_85C`
- `SSGNP_0P675V_0P675V_M40C`
- `SSGNP_0P75V_0P75V_125C`
- `SSGNP_0P75V_0P75V_25C`
- `SSGNP_0P75V_0P75V_M40C`
- `SSGNP_0P90V_0P90V_125C`
- `SSGNP_0P90V_0P90V_25C`
- `SSGNP_0P90V_0P90V_M40C`
- `SSGNP_0P99V_0P99V_125C`
- `SSGNP_0P99V_0P99V_25C`
- `SSGNP_0P99V_0P99V_M40C`
- `TT_0P675V_0P675V_125C`
- `TT_0P675V_0P675V_25C`
- `TT_0P675V_0P675V_M40C`
- `TT_0P80V_0P80V_0C`
- `TT_0P80V_0P80V_125C`
- `TT_0P80V_0P80V_25C`
- `TT_0P80V_0P80V_85C`
- `TT_0P80V_0P80V_M40C`
- `TT_0P90V_0P90V_125C`
- `TT_0P90V_0P90V_25C`
- `TT_0P90V_0P90V_M40C`
- `TT_0P99V_0P99V_125C`
- `TT_0P99V_0P99V_25C`
- `TT_1P05V_1P05V_25C`

### 4.2 B.pvt_list（11）

- `SSGNP_0P675V_0P675V_M40C`
- `SSGNP_0P99V_0P99V_125C`
- `TT_0P80V_0P80V_25C`
- `TT_0P90V_0P90V_125C`
- `FFGNP_1P05V_1P05V_M40C`
- `FFGNP_0P80V_0P80V_25C`
- `SSGNP_0P75V_0P75V_125C`
- `TT_0P675V_0P675V_25C`
- `SSGNP_1P05V_1P05V_M40C`
- `FFGNP_0P75V_0P75V_85C`
- `TT_1P05V_1P05V_M40C`

**∉ A（3）：** `SSGNP_1P05V_1P05V_M40C`, `FFGNP_0P75V_0P75V_85C`, `TT_1P05V_1P05V_M40C`

---

## 5. field_key 枚举（C=50）

### 5.1 表轴（2）

`tran_index`, `load_index`

### 5.2 表值（14）— matrix_flat；±% 默认 delay 类

- `tselr1_min_period`
- `tcq`
- `tselw1_min_period`
- `tcd`
- `taccess`
- `tpd_clk_q`
- `taddr_setup`
- `taddr_hold`
- `twen_setup`
- `twen_hold`
- `tcen_setup`
- `tcen_hold`
- `tdata_setup`
- `tdata_hold`

### 5.3 标量（34）

**功耗 / 能量 / 漏电（power 类 ±%）：**  
`leakage_vddc`, `leakage_vddp`, `retention_leakage`, `write_power_vddc`, `write_power_vddp`, `read_power_vddc`, `read_power_vddp`, `standby_power_vddc`, `search_power_vddc`, `dynamic_energy_read`, `dynamic_energy_write`, `dynamic_energy_search`

**电容 / 负载：**  
`pin_cap_a`, `pin_cap_d`, `pin_cap_clk`, `pin_cap_cen`, `pin_cap_wen`, `bitline_cap`, `wordline_cap`, `metal_cap_est`, `fanout_load_nom`

**标量时序（默认 delay 类）：**  
`setup_time_a_scalar`, `hold_time_a_scalar`, `clk_to_q_scalar`, `min_pulse_width_clk`, `min_period_scalar`, `search_latency_scalar`, `temp_coeff_delay`, `slew_out_est`

**其它：**  
`ir_drop_est`, `em_margin`, `noise_margin_snm`, `vdd_min_func`, `area_um2`

### 5.4 机读全表（字母序，已与 DB 核对）

```
area_um2
bitline_cap
clk_to_q_scalar
dynamic_energy_read
dynamic_energy_search
dynamic_energy_write
em_margin
fanout_load_nom
hold_time_a_scalar
ir_drop_est
leakage_vddc
leakage_vddp
load_index
metal_cap_est
min_period_scalar
min_pulse_width_clk
noise_margin_snm
pin_cap_a
pin_cap_cen
pin_cap_clk
pin_cap_d
pin_cap_wen
read_power_vddc
read_power_vddp
retention_leakage
search_latency_scalar
search_power_vddc
setup_time_a_scalar
slew_out_est
standby_power_vddc
taccess
taddr_hold
taddr_setup
tcd
tcen_hold
tcen_setup
tcq
tdata_hold
tdata_setup
temp_coeff_delay
tpd_clk_q
tran_index
tselr1_min_period
tselw1_min_period
twen_hold
twen_setup
vdd_min_func
wordline_cap
write_power_vddc
write_power_vddp
```

---

## 6. EPC Job YAML

对照 `/workspace/epc_fixtures/epc_job.sample.yaml`。

约束强制：`instances`, `pvts`, `keys`, `table_cells`|`scalar`, `target`（range | delta_pct）。

DEMO 约束：

1. `table_upper_bound`：`HINP3TCAM512X100SWISDC` × `SSGNP_0P99V_0P99V_125C` × `tselr1_min_period` × `all_cells` ≤ 1500  
2. `relative_delta_vs_source`：`HINP3TCAM64X8SWISDC` × `TT_0P80V_0P80V_25C` × `tcq` × `all_cells`，`delta_pct: -4` → ×0.96  

`gates.on_violation: fail_job`。

---

## 7. 输出 B.db 验收

| 检查项 | 期望 |
|---|---|
| schema | `char_data` 四列 PK |
| 集合 | 9 instance × 11 pvt × 50 key |
| 行数 | **4_950** |
| 外延 | 3 新 instance + 3 新 pvt 全字段 |
| 约束 | sample 两条 PASS |
| option | 均为 `SWISDC` |

夹具不含已生成 `B_out.sample.db`；由 P0 MVP 写出。

---

## 8. 派生运行期字段

`parse_ok` 与 instance/pvt 解析字段、`in_source_*`、`value_kind`/`n`/`matrix`、`status`、`extrapolated_flag`、job/yaml/db 指纹。

---

## 9. P0 MVP 提示验收

读 `epc_job.sample.yaml` → 写 B.db → `COUNT(*)=4950` → 约束门禁绿。

---

## 10. 修订记录

| 版本 | 说明 |
|---|---|
| v1 | 4×3×11=132，N=3 |
| **v1.1** | **20×40×50=40000，N=5；50 key 分类+全枚举；B 满表 4950；同 option=SWISDC** |

---

*路径：`/workspace/EPC_T1_数据字典.md`（**v1.1**）*
