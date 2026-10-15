# 🎨 scientific-illustrator-muse

[English](README.md) | [中文](README.zh-CN.md)

**Muse 有一台远程电脑，为什么不用起来？**

这就是全部的起点。✨

## 💡 为什么做这个

很多 AI 生成的架构图、科学示意图很漂亮，但你改不了。😤
想改一个字、换一个颜色、挪一个模块 —— 折腾得要死要活，
因为那只是一张扁平的图片。

现在你可以拿 AI 生成的架构图，让 Muse 把它变成一张**可编辑的架构图**：
每个框、每根线、每个字都是独立组件，你想怎么改就怎么改。🖱️

漂亮 + 可编辑，第一次兼得。这就是做这个的初衷。❤️

## 🚀 一个想法

开源项目 [scientific-illustrator](https://github.com/icebird1998/scientific-illustrator)
做了一件很酷的事：让 AI 直接驱动 draw.io 画科研示意图。但它需要
Codex 账号 + 本地安装 draw.io —— 用户得在自己电脑上装软件、配环境、
让 AI 连上本地画布，折腾的是本地这一套。😮‍💨

而 Muse 呢？每个 Muse 账号背后都有一台远程电脑。有终端、有浏览器、
能装软件、能跑程序。💻

那为什么还要本地装 draw.io？🤔

**一台 Muse 的远程电脑，就是全部的工作台。** 🖥️

参考图发给 Muse，它在自己的远程电脑上装好 draw.io、拉起虚拟显示、
驱动画布、导出成品 —— 你只管收两样东西：

- 📝 可编辑的 `.drawio` 源文件 → 在 Muse 里单击打开，全选复制，
  粘贴到 [app.diagrams.net](https://app.diagrams.net)，浏览器里直接改，**本地啥都不用装**
- 🖼️ PNG 成品图

Codex 账号 + 本地 draw.io 才能做的事，现在**一个 Muse 账号，全搞定**。
画在云端，改在网页，本地零安装。☁️

更进一步：**📱 你在手机上都能搞科学绘图**。手机里给 Muse 发一张参考图，
它在云端画完，你在手机浏览器里打开 [app.diagrams.net](https://app.diagrams.net) 微调 ——
口袋里的科研绘图工作站，不需要电脑。

这就是本项目的创新：不是算法上的，是**想法上的、工作模式上的**。💡
Muse 的一种新玩法：把远程电脑当成无限延伸的工作台。
科学绘图这件事，第一次有了**单账号、零本地安装的解决方案**。🎯

还有一个变化：**原来需要专业知识才玩得转，现在小白也能用**。🌱

上游路线要求你懂 Codex、会装 draw.io、配得通 MCP ——
每一道都是门槛，拦住的都是只想画张图的人。🚧

Muse 版把门槛砍到只剩一句话：给 Muse 发张图。
这不恰好就是 Muse 的设计初衷吗？让每个人都能用上 AI，
不管他懂不懂技术。我们的目标，一致。🤝

## 🛠️ 它能做什么

给 Muse 一张参考图（实验装置、网络架构、工艺流程、电路图……），
它在远程电脑上自动重绘，产出两样东西：

- 📝 可编辑的 `.drawio` 源文件 —— 在 draw.io 里逐组件修改
- 🖼️ PNG 成品图

也可以给一段文字描述，让它从零设计。图标、3D 组件用 AI 生成后嵌入，
风格可指定立体或扁平。🎲

```
一张参考图 → Muse（远程电脑）→ draw.io → .drawio + PNG
```

## ✏️ 画完之后：随便改

可编辑才是这个项目的灵魂。拿到 `.drawio` 后，三种改法：

**1. 让 Muse 帮你微调** 🗣️

直接跟它说人话就行：

> "把'全球開放'几个字放大一倍"
> "这个配色太暗了，换亮一点"
> "箭头太细，加粗"

Muse 改完重新导出，新图发你。改脚本、重生成都是确定性的 ——
只动你指定的地方，其他纹丝不动，不会改乱。

**2. 自己在网页上动手改** 🖱️

把 `.drawio` 在 Muse 里单击打开，全选复制，粘贴到 [app.diagrams.net](https://app.diagrams.net)，
每个框、每根线、每个字都是独立组件：拖位置、换颜色、改文字，
跟 PPT 一样直观。本地啥都不用装。

**3. 换组件** 🔄

看某个图标不顺眼？两种换法：

- 让 Muse 换：跟它说"这个齿轮不好看，重新生成一个更好看的换上"，
  它用 AI 重新生成该组件、无缝替换，其他部分不动
- 自己手动换：让 Muse 给你生成新图，在 [app.diagrams.net](https://app.diagrams.net) 里删掉旧组件，
  把新图拖进来，摆好位置就行

---

三种改法混着用：大改找 Muse，小改自己动手 ——
"漂亮 + 可编辑"第一次真正闭环。⭕

## 🚀 上手

**👶 小白版**（一句话）：

> 告诉你的 Muse："看看这个开源项目 scientific-illustrator-muse，
> 在远程电脑上安装一下。"然后发给它一张图："请帮我重绘一下。"
>
> 就这么简单。😎

**👨‍💻 技术版**：见 [QUICKSTART.md](QUICKSTART.md) —— 三步跑通第一张图。

```bash
git clone https://github.com/song-squared/scientific-illustrator-muse.git
cd scientific-illustrator-muse
./setup.sh
```

## 📋 工作流

[SKILL.md](SKILL.md) —— 完整规范：直接写 XML、AI 图标嵌入、
画完四项自查（颜色/布局/3D-2D风格/文字）。✅

## 📁 目录

| 文件 | 说明 |
|---|---|
| `QUICKSTART.md` | 三步上手 🚀 |
| `SKILL.md` | 完整工作流规范 📋 |
| `setup.sh` | 一键安装：Xvfb + draw.io Desktop + 系统依赖 ⚙️ |
| `mcp-call.sh` | 批量调用入口 🔧 |
| `mcp-shim.mjs` | MCP 垫片：stdio JSON-RPC 转发 🔌 |
| `scripts/` | draw.io MCP server（从上游 vendored）📦 |

## 💻 环境

- Linux（Ubuntu 22.04/24.04 实测）、Node.js 18+、Python 3 + pillow
- draw.io Desktop（`setup.sh` 自动装）

## 🙏 致谢

- [icebird1998/scientific-illustrator](https://github.com/icebird1998/scientific-illustrator)（MIT）：
  draw.io MCP server 原样复用，仅修复 data URI 分号截断
- draw.io Desktop（Apache 2.0）

## 🌟 期待

这是 Muse 新玩法的一次尝试：**远程电脑即工作台**。

如果你也用 Muse 的远程电脑干出了别的有意思的事，
欢迎分享 —— 期待有更多 Muse 的新玩法。🎉

## 📄 License

MIT
