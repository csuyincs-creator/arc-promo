# arc-promo 弧形宣传片

[English](README.md) · **简体中文**

一个 agent skill：给它一句话和几张图，产出一条 15–30 秒的 4K 电影感宣传片，风格是
「一条地平线弧形」的匹配剪辑。

每个镜头都是某个圆形世界的顶边，而且永远落在画面同一个位置，所以硬切看上去像同一条地平线
在换身份：黎明时的地球边缘 → 肥皂泡 → 太阳 → 粉笔画蓝图 → 火星 → 薰衣草田 → 雪花。
剪辑点踩在音乐上并逐渐加密；文案一句一句浮现在弧线上；最后一个词随每次切换长大；
接着是标题卡；最后太阳再次升起，让整片首尾循环。

```
一段文案  +  一文件夹图片（可选）  →  out/promo_4k.mp4
```

## 它做了什么

| 阶段 | 具体行为 |
| --- | --- |
| **故事** | 把你的文案拆成 3–4 个短句，拼成一句话，再加 1–2 张尾卡。支持双语（每句可配中英两行）。 |
| **素材** | 优先用你自己的图；一张都不给时，才去 Wikimedia Commons 只找 CC0 / 公有领域图片，并从 NASA 取行星底图。 |
| **镜头** | 给每张图判定类型（风景 → `bend`，圆形物体 → `disc`，行星贴图 → `sphere`，纹理 → `texture`，手绘 → `procedural`），按 4480×2400 压到弧线上，并生成可直接翻看的联系表（contact sheet）。 |
| **剪辑** | 默认用内置 20.06 秒音轨的切点网格（37 个镜头、8 个重拍）；也可照参考视频的节奏剪，或用你给的任意音频做节拍检测。 |
| **渲染** | Remotion → 4K MP4，另出 1080p H.264 版本、`CREDITS.md` 和完整工程源码。 |

## 环境要求

- macOS 或 Linux，**工作目录必须在 APFS / HFS+（或 ext4）上**：`node_modules` 需要符号链接，
  exFAT / FAT 的外置盘会直接失败。
- `PATH` 里有 `ffmpeg` 和 `ffprobe`
- Node.js ≥ 18
- Python 3（`numpy`、`pillow` 由安装脚本装进本地 `.venv`）
- 首次安装需要联网：`npm ci`，以及 Remotion 一次性下载约 140 MB 的无头 Chrome

## 安装为 skill

把仓库克隆到你的 agent 扫描 skill 的目录，目录名保持 `arc-promo`：

```bash
git clone https://github.com/csuyincs-creator/arc-promo.git ~/.agents/skills/arc-promo
```

其他等价的 skills 目录也行——关键是最终路径是 `<skills-dir>/arc-promo/SKILL.md`。

skill 从 `SKILL.md` 加载；`scripts/`、`references/`、`template/`、`assets/` 必须和它放在同一层。

## 怎么用

直接把需求说出来即可。skill 会在「宣传片 / 短片 / trailer / 预告」这类请求，以及
「照那条弧形片子做一个」时触发。

> 给我的咖啡品牌做一条 20 秒宣传片。文案：每杯 / 都是 / 一次 / 出发。
> 收尾那句：每一次出发，都值得被认真对待。
> 用 ~/Pictures/coffee 里的照片，要 4K。

想跟着某首歌的节奏剪：

> 还是这个风格，但按这首歌 0:42 开始剪，总长 20 秒。

产物落在临时工作区的 `out/`：`promo_4k.mp4`、`promo_1080p.mp4`、`CREDITS.md`，
以及完整的 Remotion 工程。

## 音轨与版权

内置音轨（`assets/default-music/music.wav`，20.06 秒）是**第三方音乐**，版权属于原作曲者，
不属于本仓库。公开发布前请先取得授权或换掉。

换成自己的音乐：

```bash
$PY scripts/analyze_music.py --audio song.mp3 --start 42 --length 20 --out <ws>
$PY scripts/analyze_music.py --video reference.mp4 --out <ws>    # 复刻一条片子的剪辑节奏
```

两者都会重写 `src/data/timeline.json`，剪辑随之改变。把 `assets/default-music/` 里的两个文件
拷回去，就能恢复默认节奏。

## 图片与授权

- 自动找图时**只用 CC0 / 公有领域**素材，且只从 Wikimedia Commons 取；每个镜头在 `shots.json`
  里都记录 `credit`、`license`、`url`。
- `make_credits.py` 据此生成 `CREDITS.md`；没记授权的镜头会被标成 `UNKNOWN` 而不是默认放行。
- skill 不会把参考片的品牌元素（logo、产品名、字标）搬到尾卡上——那会让片子看起来像别人家的官方广告。

## 仓库结构

```
SKILL.md                     skill 本体（agent 加载的就是它）
references/
  shot-types.md              镜头类型与参数
  sourcing.md                怎么搜、怎么下 CC0 素材
  editing.md                 排序规则与审片清单
  example-demo/              一个完整的示例工程（shots.json、project.json）
scripts/
  setup_workspace.sh         模板 + npm ci + .venv
  analyze_music.py           视频/音频 → 切点网格（timeline.json）
  fetch_base_maps.sh         行星镜头的 NASA 底图
  search_commons.mjs         Wikimedia Commons 搜索
  fetch_commons.mjs          限速下载器
  gen_shots.py               把所有镜头压到弧线上
  gridsheet.py               带 10% 网格的联系表，用来读地平线行号
  check_circle.py            校验圆心与半径
  shot_sheet.py              成片镜头审片表
  make_credits.py            shots.json + timeline + project → CREDITS.md
template/                    Remotion 工程（Arc、Shot、Planet、EndCard、Effects…）
assets/default-music/        默认音轨 + 它的切点网格
```

## 已知限制

- agent **听不到**成片。同步性靠肉眼核对（切点位置、电平、抽帧条），交付时 skill 会明说这一点。
- 20 秒的片子渲染 4K 大约 3–6 分钟；新工作区第一次跑 Remotion 要下载无头 Chrome。
- 行星镜头依赖 NASA 底图；拿不到时这些镜头会被跳过，而不是硬凑。

## 授权

仓库未附 LICENSE 文件。第三方音乐与摄影作品各依其原始条款。
