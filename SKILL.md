# Muse 版 Scientific Illustrator 工作流

> 改编自上游 Codex 插件 skill `recreate-scientific-figure-in-drawio`。
> 上游用 Codex + 原生 MCP 调用；这里用 Muse + `mcp-shim.mjs` 垫片调用同一批 MCP server。
> MCP server 本体（`live-server.mjs` / `server.mjs`）是上游代码，原样复用，不改。

## 0. 环境与路径（每次开工先确认）

| 项目 | 值 |
|---|---|
| 工作目录 | 项目根目录（`git clone` 下来的 `scientific-illustrator-muse/`） |
| 垫片 | `mcp-shim.mjs`（stdio JSON-RPC 转发，截图落盘到 `shots/`） |
| 批量入口 | `mcp-call.sh live` / `mcp-call.sh file`（自动起 Xvfb、设好 `DISPLAY=:99` 与 `DRAWIO_PATH`） |
| 上游 server | `./scripts/`（从上游 vendored：`live-server.mjs`、`server.mjs`、`drawio-path.mjs`） |
| draw.io 可执行 | `/opt/drawio/drawio`，经 wrapper `drawio-ns.sh` 加 `--no-sandbox`（root 必需） |
| 虚拟显示 | `Xvfb :99`（`mcp-call.sh` 会自动拉起） |
| 依赖包缓存 | `deps/`（draw.io 的 .deb 依赖，apt 不可用时本地安装） |
| 安装包 | `drawio-32.4.1.deb`（`setup.sh` 自动下载；apt 不可用时手动重装） |

调用方式（二选一）：

- **批量模式**（推荐）：`printf '%s\n' '{...}' '{...}' | ./mcp-call.sh live`，
  一次调用 = 一个 server 会话，stdin 结束即退出。适合一气呵成的绘制序列。
- **常驻模式**：后台起垫片进程，用 stdin 逐条发调用，画布会话跨多轮保持。
  适合"画 → 看截图 → 改 → 再画"的交互式流程。

## 0. 设计先行（继承 design-scientific-figure）

动笔前先定四件事，写在任务开头：

1. **一句话信息**：这张图要讲什么（如"共享储能电站把光伏风电存起来再并网"）。
2. **阅读顺序**：观众视线先到哪、再到哪（如"先看顶部三组设备，再看底部流程条"）。
3. **硬约束**：长宽比、输出尺寸、必须一字不差的标签、不能动的事实。
4. **3D 判断**：参考图是否为 3D 表现（见 4.0）。先做**布局分析**：
   上下分区——上部通常是 3D 表现的组件区，下部是 2D 表现的流程/标签区；
   上部再按左中右分块，每块独立决策。

## 0.5 截图 + 堆叠（难画的 3D 组件）

3D 透视组件先判断是否容易画：
- **易画**（如电池单体）：按 4.0 做 3D 组件化，手绘可编辑。
- **难画**（如透视风机群、变压器、控制柜）：**截图 → 去毛刺 → 堆叠**，
  不要硬画：
  1. 从原图按对象紧裁剪（`PIL ImageChops.difference` 去白边）；
  2. 检查裁片边缘，把相邻箭头、相邻设备的"入镜"部分收进裁剪框外——
     这就是"擦去毛刺"；
  3. **背景透明化**：只保留干净的实体。做法：先给裁片加一圈白边
     （保证角落落在背景上），再从四个角 floodfill 白色→透明，
     最后裁掉全透明边。不透明的白底会在网格画布上形成白盒子，
     导致堆叠时组件视觉重叠；
  4. **图形缩放**：按原图比例关系调整各截图的显示尺寸
     （如变压器/控制柜相对电池的高度比），不要直接沿用裁片像素尺寸；
  5. `drawio_live_add_image` 作为原子图片堆叠进画布，摆好位置、避免重叠；
  6. 文字、箭头、流程条一律保持手绘可编辑。
- 技术坑：draw.io 的 cell 样式按分号切分，data URL 里的 `;base64`
  会被截断。插入图片前必须做 `convertDataUri` 转换
  （`data:image/png;base64,xxx` → `data:image/png,xxx`），
  与 draw.io 官方 `EditorUi.convertDataUri` 一致。
  （2026-10-14 已修复上游 `addImage` 缺失此转换的 bug。）

## 1. 建会话（安全启动）

**默认用冷启动**（实测规律：全新 profile 启动 → 空白画布 `graph_ready=true`；
沿用旧 profile → 可能停在起始页 `graph_ready=false`）：

```bash
pkill -f "[d]rawio.*no-sandbox"; sleep 2; rm -rf ~/.drawio-live-mcp
printf '%s\n' '{"id":1,"tool":"drawio_live_launch","arguments":{}}' | ./mcp-call.sh live
```

1. 先确认 Xvfb 在跑：`ps aux | grep "[X]vfb :99"`（`mcp-call.sh` 会自动拉起）。
2. 调 `drawio_live_launch`，要求返回 `connected=true`。
3. 调 `drawio_live_status`，要求 `graph_ready=true` 且标题为 `Untitled Diagram`。
   若不满足，重复上面的冷启动三件套。
4. 要接着画之前存过的图：launch 时传 `file_path` 指向已保存的 `.drawio`。
5. 只读 inspection 任务：只调 `get_capabilities` + `status` + `inspect`，
   不 clear、不 add、不 save。

## 2. 查能力（动笔前必做）

调 `drawio_live_get_capabilities`，拿到 `baseline_shapes` 的 `plugin_name` 列表
（实测：`rectangle,rounded,ellipse,diamond,cylinder,hexagon,triangle,parallelogram,trapezoid,pentagon,star,document,note,cloud,text,swimlane`）。
**形状名只能用这个列表里的**，猜名字会被 server 拒绝（它不允许静默画成矩形）。
需要特殊图形时：用已注册名 → 或用基础图元拼 → 最后才考虑原子图片。

## 3. 语义对照表

| 要画的东西 | 实现方式 |
|---|---|
| 可编辑文字 | `drawio_live_add_shape` + `shape=text` |
| 符号/面板/容器 | `add_shape` 用 baseline 名或注册名 |
| 坐标轴/刻度/分隔线/自由箭头 | `drawio_live_add_line`（参数是 `begin_x/begin_y/end_x/end_y` + `waypoints:[{x,y}]`，不是 `points` 数组） |
| 语义连线（保持吸附） | `drawio_live_add_edge`（指定出入点/waypoints）。注意没有 `drawio_live_add_text`/`drawio_live_add_connector` 这两个工具，文本用 `add_shape`+`shape=text` |
| 表格 | `drawio_live_add_table` + `update_table_cell` / `update_table_layout` |
| 常规图表 | `drawio_live_add_chart`，或用可编辑图元手拼 |
| 重复纹样 | `duplicate_cell` + `group_cells`/`ungroup_cell` + `set_z_order` |
| 精确布局 | `drawio_live_align_cells` / `drawio_live_distribute_cells`，不要目测 |
| 结构审查 | `drawio_live_audit_figure` + `drawio_live_inspect` |
| 渲染审查 | `drawio_live_screenshot`（PNG 落盘到 `shots/`，用 read 工具看图） |

## 4. 绘制循环（Designer → Drawer → Reviewer → Corrector）

### 4.0 先判断 3D：组件化方法论

1. 先看参考图是否为 **3D 表现**（透视、厚度、明暗面）。
2. 识别出需要封装的 **3D 单元**（如电池组里的单块电池）：先画好**一个**单元——
   前面（主色）+ 顶面（浅色）+ 侧面（深色），三块拼出厚度感。
3. 单元定稿后再阵列复制（`duplicate` 思路或循环生成），不要先铺平面再补 3D。
4. 2D 图形不受此约束，但"先做组件再排列"的思路同样适用（如风机：杆+轮毂+叶片为一组）。

1. **Designer（规划）**：从参考图提取清单——每个元素分配稳定 id、坐标、
   宽高、父分组、绘制顺序、z-order；分类为文字/图形/自由线/连线/表格/图表/重复纹样/不可约光栅区。
2. **Drawer（绘制）**：一次画**一个逻辑区域**，从背景到前景，`pause_after_ms` 给非零值
   （看得见的节奏）；文字用独立 text cell 并规划好换行；连线用 attached edge，
   轴线用 free line；画完一批就 `fit` 保持视野。
3. **Reviewer（审查，继承 audit-scientific-figure）**：每画完一个区域，走四通道检查：
   - 语义：文字准确、拓扑对、箭头方向对；
   - 可编辑性：每个语义对象都是可编辑 cell，无面板截图替代；
   - 几何：对齐、等距、边距、留白，**连线横平竖直**（waypoint 必须选在正交转折点上，
     禁止出现斜线段；出入锚点取边中点，不取角落）；
   - 文字：不溢出、有换行、字号层级一致、颜色统一。
   然后 `screenshot` 看渲染 + `audit_figure` 查结构。
   **分块对比法**：把参考图和重绘图按相同逻辑块裁切（设备区/阵列区/流程区），
   逐块并排对比——整体看容易"差不多就行"，分块看差距无处藏身。
4. **Corrector（修正，继承 correct-scientific-figure）**：每个 finding 必须有
   ——定位（区域+对象 id）、证据（截图/审计原文）、验收条件——才动手改；
   改完重截图+重审计，直到本区域无未解决问题才画下一区域。
   注意：没有 delete 工具，waypoint 建好后改不了，**连线宁可重画也不凑合**。
5. 全部区域通过后，对**整张画布**再跑一遍审查循环。

## 5. 图型专项（通用性实战沉淀）

### 5.1 表格
- 无原生 table 形状，用 `text` cell 拼。**必须**显式
  `strokeColor=none;fillColor=none;`，否则 text cell 默认带边框，booktabs 表会变成网格表。
- booktabs 三线：顶线粗、表头下细、底线粗，用 `drawio_live_add_line` 画。
- 表头/最优值加粗用 `fontStyle=1`。

### 5.2 图表（曲线图）
- 混合策略：数据曲线（含误差棒）截图——形状无法精确复现；
  坐标轴、刻度线、刻度标签、轴标签、标题、网格、图例全部手绘可编辑。
- 截图前：用 numpy 定位轴线像素，只裁轴线内侧的数据区；
  图例若在数据区内，先涂白再透明化（后面手绘可编辑图例）。
- 刻度位置按数据范围线性映射计算，不要目测。
- Y 轴竖排标签用 `rotation=270`。
- 网格用浅灰虚线（`dashed=1`）。

### 5.3 显微照片拼图
- 照片面板：截图为原子图片（深色背景无需透明，紧裁剪即可）。
- 截图前先涂掉原标签（A/B/C/D）和标尺（深色底用黑矩形盖），后面重建为可编辑。
- **标尺必须实测**：用 numpy 找白色横条，量像素宽，绝不目测；
  面板缩放时标尺按同比例缩放（如 400px 面板上 121px → 300px 面板上 91px）。
- 标尺画法：白色线 + "20 μm" 文字，位置右下。
- 面板标签：白色加粗 text，左上。
- 无缝拼图：面板零间距紧贴放置。

### 5.4 复杂 2D 系统图（VPP 架构图实战）
- 大图先分区规划，用脚本生成批量调用，不要手写上百个 JSON。
- **图标终极方案（2026-10-14 实战验证）**：**AI 生成 + 直接嵌入 .drawio**
  1. 用 `media.generate_icon` 生成图标（方正、扁平、无字，按需指定颜色如 `#2B7DE9`）。
  2. PIL 白底转透明 → PNG。
  3. base64 后直接写进 `.drawio` XML：`<mxCell ... style="shape=image;image=data:image/png,BASE64;...">`。
     **关键**：不要用 `data:image/png;base64,...` 形式——draw.io style 用分号分隔，
     `;base64` 会被截断。用无分号的 `data:image/png,...`。
  4. `drawio_export` 能正常渲染嵌入图片（不像 MCP `add_image` 那样丢失）。
  5. 图标是独立可移动/缩放的 cell，用户在 diagrams.net 里可直接调整。
- **已证伪的图标路线**（别再踩）：
  - 原图抠图：用户明确反对，粗糙。
  - PIL 生成 PNG + MCP `add_image`：早期不渲染，原因是 `;base64` 分号被 style
    截断（已修复 live-server.mjs）。当前主路线已改为 base64 直接写 XML。
  - `drawio_live_add_line` 矢量手绘：小规模可用；大批量调用时曾出现线条丢失，
    但未严格排除旧文件/缓存干扰，不应视为确定性 bug。
  - `drawio_live_add_shape` 矩形拼图标：能导出，但小尺寸元素有渲染阈值
    （1.0x/1.8x 导出成碎片，2.0x 才正常），图标被迫放大到压字。
- 虚线域：`dashed=1;dashPattern=10 8`。
- 标题栏：色块矩形 + 白字 text 叠在盒顶。
- 多行小字用 `whiteSpace=wrap`。
- 复杂箭头走线用 waypoint 保证正交。

### 5.5 含 3D 组件的系统示意图（储能电站实战）
- **3D 硬骨头别手画**：电池阵列、变压器、控制柜这类 3D 表现组件，
  用 `media.generate_image` 直接生成（prompt 指定 isometric、白底、无字），
  比"前面+顶面+侧面"手拼形状快 10 倍且更好看。
- **生成后必须紧凑裁剪**：AI 图白边大，直接嵌入边框松散。
  用 PIL `ImageChops.difference` 找非白 bbox（阈值 15，防阴影误裁），
  四边各留 10px，再 base64 嵌入。裁完的图存 `gen_icons/cropped/`。
- **图标去底进阶**：生成的图标不一定是纯白底（有浅蓝底的情况）。
  用"四角采样背景色 + 色距阈值 60"转透明，比固定阈值 240 更鲁棒。
- **嵌入方式**：同 5.4，直接写 `.drawio` XML 的
  `<object><mxCell style="shape=image;image=data:image/png,BASE64">`，
  不用 `;base64`。
- **矢量与位图分工**：3D 组件是位图（可拖可缩放），标签/流程块/箭头是矢量可编辑。
- **连线自己整理**：旧图导入的连线常有重复 id 或拐点蛇形，
  别修，直接删了按"关系正确、形状好看"重画。正交 `┌┐` 走线，
  waypoints 只留必要拐点。能量流向保持从左到右。

### 5.6 批量练习：直接写 XML 比 live 快 10 倍
- 10 张图通宵实战结论：`.drawio` 直接手写 XML + `mcp-call.sh file` 做
  validate/export，比 live 逐笔绘制快一个数量级，适合批量练习。
- live 模式的坑：同一端口多次 launch 会复用旧画布 → "Cell id already exists"；
  拿干净画布最省事的办法是用新端口。draw.io 实例启动慢，graph 未就绪时调用报
  "graph is not ready"，等几秒重试；实例彻底坏掉（no debuggable editor page）时
  kill -9 进程 + 删 `~/.drawio-live-mcp/<port>` 后重建。
- `drawio_validate` 在 live 生成的文件上报 "mxCell without id" 属误报（此前储能图也有），
  不影响导出，PNG 正常即可。
- `generate_image` 每轮限 4 张，超了另起一轮。

### 5.7 重绘后必查清单（2026-10-14 用户立规矩）
重绘完、导出后，必须逐项对照原图检查，**不能只看结构对了就交**：
1. **颜色**：每个色块的填充色、边框色是否与原图一致。fillColor 参数可能被忽略
   （MCP 直接写 XML 的 style 字符串最可靠），改完必须看导出 PNG 确认。
2. **布局位置**：各组件的相对位置、间距、對齐方式是否与原图一致。
   外层容器是虚线框还是实线、有没有填充色，都要对。
3. **图标风格 3D/2D**：看原图的图标是立体 3D 还是扁平 2D，AI 生成时 prompt
   必须指定对应风格（如 "Cisco network icon style, 3D isometric" vs "flat 2D icon"）。
   风格错了整张图就不像。
   - **3D 图标生成原则**（2026-10-14 用户立）：判定为 3D 风格后，用原图做参考图
     输入 AI 生成，目标是**一样或相似度很高**，不是凭空创作。
   - 例外须用户特批（如网络拓扑图用户选了 3D 立体风，尽管原图是扁平蓝）。
4. **文字**：标签内容、字号层级、有没有压住/被压住。
5. 做完 1-4 再做原图/重绘对比图，肉眼过一遍。

### 5.8 图片缓存：更新后用户看不到新图（2026-10-14）
- **现象**：PNG 已更新，但用户在 App 里看到的还是旧图。iOS/Android 客户端会缓存
  相同 URL 的图片。**App 端缓存 Muse 修不了，只能绕过。**
- **对策**：每次实质更新，文件名强制带时间戳（`date +%H%M%S`），如
  `practice2-sld-110439.png`，确保 URL 全网唯一，客户端无缓存可命中。
  `overwrite:true` 只用于中间过程，最终交付必须新名。
- 顺手把旧版本留着，方便回滚对比。
- 发图时只发最新时间戳那张，不要翻旧消息看图。

### 5.9 电气原理图（2026-10-16 浮球电机实战）
- 可画。接触器触点/线圈、热继电器、电机、指示灯、按钮、选择开关、浮球开关
  全是直线/圆/矩形的组合，Python 直写 `.drawio` XML 一把梭，不用 AI 生成图标，
  也不用调 draw.io 自带电气符号库（库是给人用鼠标点的，AI 背内部 style 名反而慢）。
- 难点不在画，在**认电路**：元件多、接线密，认错一个符号整图就错。
  动笔前先分区放大读原图，盘点所有元件与接线拓扑再写代码。
- 版式建议：原图常把控制支路挤在主触点极间穿过，重绘时可把主回路/指示灯/
  控制回路分成左中右三区，拓扑不变、可读性更好（差异要在完工报告里说明）。
- 黑底白线 CAD 风：先画满画布黑矩形打底（`fillColor=#000000`），再画白线；
  红实心圆点表示导线连接（无点交叉=不连接）。

### 5.10 Python 直写 XML 的坑（2026-10-16）
- `as` 是 Python 关键字，`ET.SubElement(..., as_="geometry")` 会原样输出成
  错误属性 `as_=`，draw.io 解析异常。必须用 attrib 字典：
  `ET.SubElement(parent, "mxGeometry", {"as": "geometry", ...})`。
  同理 `mxPoint` 标签别手滑写成 `mxGeometry`。
- 写完先用极简渲染器自查几何（`drawio_render.py`：PIL 直读 .drawio 画 PNG），
  确认无误再走 draw.io 官方导出；draw.io 挂掉时它也可做导出兜底。

### 5.5 铁律
- 只调 draw.io 自身的图 API；不模拟鼠标键盘；不预生成 XML 再打开。
- `save_snapshot` 存 `.drawio` 只能发生在图已画完之后。
- 原子图片（`add_image`）仅用于真正不可约的光栅区（显微照片、热图等），
  必须配 `raster_reason` + 紧裁剪 + 分解说明；文字/箭头/图例一律重建成可编辑 cell。
- 未经用户确认，不 `clear` 已有画布。
- 截图只看 `shots/` 落盘文件，不把 base64 打进上下文。

## 6. 交付

1. 最后一次全画布审查通过。
2. `drawio_live_save_snapshot` 存 `.drawio`。
3. 切到 `mcp-call.sh file`：`drawio_validate` 校验 → `drawio_export` 出 PNG（review 用，
   建议 2000px）/ SVG / PDF。
4. 汇报：对象总数、分组数、图片数及每个 raster 声明、各区域与整画布的审查结果、
   校验结果、残留的不确定点。

## 7. 故障速查

| 现象 | 处理 |
|---|---|
| `graph_ready=false`，标题是起始页 | `rm -rf ~/.drawio-live-mcp` 后重新 launch |
| `spawn ... ENOENT` | 检查 `drawio-ns.sh` 是否存在（曾离奇消失过），`/opt/drawio/drawio` 是否还在 |
| `Unknown or unloaded draw.io shape` | 形状名不在能力列表里，查 `get_capabilities` |
| 远端机重启/VM 替换后 | Xvfb/drawio 进程全灭，`mcp-call.sh` 会自动重起 Xvfb；若 `/opt/drawio` 被清空，用工作区备份包重装：`sudo dpkg -i drawio-32.4.1.deb` + 补 `libnotify4` `libxtst6`（`libsecret-1-0` 缺失不影响运行） |
| 手动启动停在起始页 | 走 MCP `drawio_live_launch` 会自动进 Untitled Diagram（`graph_ready=true`），不用手动点 |
| 审计报 `connector-path-through-object` | 先看是不是装饰性线条（叶片穿过轮毂、网格线穿过面板、散热片穿过箱体）——是则为误报，接受；真问题只看 `outside-page` 和 `arrowhead-intrusion` |
| 内存不足（可用 <300MB） | 先 `free -m` 确认；Electron 启动可能失败，等宿主机内存回落再试 |
| apt 卡死 | 别等了，走 curl 手动下 deb（参考第三步的包地址记录） |
| `drawio --headless --export` 段错误 | 缺 Electron 运行时依赖；改用 `xvfb-run -a /opt/drawio/drawio --no-sandbox --export ...`（2026-10-16 实测可用） |
