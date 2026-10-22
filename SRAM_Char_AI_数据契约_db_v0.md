# 表征 .db 数据契约 v0.1（Kai 口述迭代）

| 项 | 内容 |
|---|---|
| 状态 | 草案 v0.1 |
| 存储 | SQLite；**SRAM/Memory compiler 核心表征库**，支撑后续出库 .lib |
| 范围 | **一个工艺平台**下的一份（或多份）`.db` |
| 规模 | 记录条数 ≈ **A × B × C**（A=instance 数，B=PVT 数，C≈每组 field_key 数 ~50） |

## 逻辑行

```
instance_name | pvt | field_key | value
```

- 每个 `(instance, pvt)` 下 `field_key` 集合相同（C 固定）。
- `value`：标量，或展平 N×N（3/5/7，通常 5×5）。
- 表轴：`tran_index` / `load_index`；表值：constraint / delay / min_period 等。

## Instance 命名正则（必须可解析）

样例：`HINP3TCAM64X8SWISDC`、`HINP3TCAM64X8M2SWISDC`

| 段 | 含义 | 示例 |
|---|---|---|
| Vendor | 厂商前缀 | `HI` |
| Process | 工艺平台 | `NP3` |
| Family / 开发套 | 数字之前的产品族 | `TCAM`；亦可 `SRAMHCSPEB` / `SRAMHCSPSB` / `HCTP` / `HCBP` 等 |
| Geometry | `{depth}X{width}` 可选 `M{mux}` | `64X8`、`64X8M2`、`512X100` |
| Options | 其余 option 串 | `SWISDC` |

**解析要求：** 见到 instance name 必须按上表拆解；Family 在「数字开始之前」；Geometry 识别 `(\d+)X(\d+)(M\d+)?`；前后缀分别归 Vendor+Process 与 Options（具体正则以样例 .db 校验后锁定）。

## PVT 命名（样例）

`SSGNP_0P675V_0P675V_M40C` → corner + 多电压 + 温度（解析器待 .db 校验）。

## 业务主线（相对讲稿的关键纠偏）

讲稿 Slide 24–26 侧重 **PVT 维**缺数/少仿/跨工艺迁移。  
Kai 补充的 **compiler 核心用法**是 **配置维（instance 几何）插值**：

1. `.db` 中备齐 **边角 instance**（如 64×8、512×8、64×100、512×100）在 **全部 B 个 PVT** 下的全字段 C。  
2. 按数据趋势，对目标几何（如 128×64）在 **同样 B 个 PVT** 上生成全部 `field_key|value`。  
3. 生成结果供后续 **lib 出库**。  
4. 边角点尽量覆盖目标范围；也可用于范围外外推（风险更高，需门禁）。

因此预测问题至少有两条轴，可组合：

| 轴 | 问题 | 输入 | 输出 |
|---|---|---|---|
| **配置维（主）** | 边角 instance → 新 instance | 已知几何点的全 PVT×全字段 | 新几何的全 PVT×全字段 |
| **PVT 维（辅/讲稿）** | 缺 PVT / 少 PVT | 同 instance 部分 PVT | 其余 PVT |
| **组合** | 新几何 + 部分 PVT 缺失 | 混合 | 完整表 |

P0 推荐需在「配置维插值出库」与「PVT 缺数解卡」之间由 Kai 确认优先级（默认：**配置维插值更贴近 compiler 出库主路径**）。

## 待确认

- [ ] 样例 `.db` 上传（introspection A/B/C、物理 schema、全 field_key）
- [ ] Family 枚举完整列表
- [ ] 边角 instance 选取策略（矩形凸包？对角线？）
- [ ] P0 主线：配置维插值 vs PVT 缺数 vs 两者同里程碑
