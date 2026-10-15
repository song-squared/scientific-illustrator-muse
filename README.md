# 🎨 scientific-illustrator-muse

[English](README.md) | [中文](README.zh-CN.md)

**Muse has a remote computer. Why not use it?**

That's where it all starts. ✨

## 💡 Why this exists

AI-generated architecture diagrams and scientific illustrations look beautiful,
but you can't edit them. 😤
Change one word, swap a color, move a module — and you're in for a world of pain,
because it's just a flat image.

Now you can take an AI-generated architecture diagram and have Muse turn it into
an **editable diagram**: every box, every line, every word is an independent
component. Change whatever you want, however you want. 🖱️

Beautiful + editable, together at last. That's why this exists. ❤️

## 🚀 The idea

The open-source project [scientific-illustrator](https://github.com/icebird1998/scientific-illustrator)
did something cool: let AI drive draw.io directly to create research illustrations.
But it needs a Codex account + a local draw.io install — you have to install software
on your own machine, configure the environment, and hook AI up to a local canvas.
All the hassle lives on your local machine. 😮‍💨

But Muse? Every Muse account comes with a remote computer. Terminal, browser,
installs software, runs programs. 💻

So why install draw.io locally at all? 🤔

**One Muse remote computer is the entire workbench.** 🖥️

Send a reference image to Muse. It installs draw.io on its remote computer,
spins up a virtual display, drives the canvas, exports the result —
you just collect two things:

- 📝 Editable `.drawio` source file → single-click it open in Muse, select all,
  copy, paste into [app.diagrams.net](https://app.diagrams.net) and edit right
  in the browser. **Nothing to install locally.**
- 🖼️ Finished PNG

What used to need a Codex account + local draw.io now takes
**one Muse account. That's it.**
Draw in the cloud, edit on the web, zero local installs. ☁️

Even better: **📱 you can do scientific illustration from your phone.**
Send Muse a reference image from your phone, it draws in the cloud,
you fine-tune in your phone browser at [app.diagrams.net](https://app.diagrams.net) —
a pocket research-illustration workstation, no computer needed.

That's the innovation here: not algorithmic, but **conceptual — a new way of working**. 💡
A new way to play with Muse: treat the remote computer as an infinitely
extending workbench.
Scientific illustration finally has a **single-account, zero-local-install solution**. 🎯

One more shift: **what used to require expertise now works for beginners**. 🌱

The upstream route demands you understand Codex, install draw.io, configure MCP —
every step a gatekeeper, each one blocking people who just want to draw a diagram. 🚧

The Muse version cuts the barrier down to one sentence: send Muse an image.
Isn't that exactly what Muse was designed for? AI for everyone,
regardless of technical skill. Our goals align. 🤝

## 🛠️ What it does

Give Muse a reference image (lab setup, network architecture, process flow,
circuit diagram…), and it redraws it on its remote computer, producing:

- 📝 Editable `.drawio` source — modify component by component in draw.io
- 🖼️ Finished PNG

Or give it a text description and let it design from scratch. Icons and 3D
components are AI-generated and embedded; pick 3D or flat style. 🎲

```
A reference image → Muse (remote computer) → draw.io → .drawio + PNG
```

## ✏️ After drawing: edit freely

Editability is the soul of this project. Once you have the `.drawio`, three ways to tweak:

**1. Ask Muse to fine-tune** 🗣️

Just talk to it like a human:

> "Double the font size of 'Global Release'"
> "This color scheme is too dark, brighten it up"
> "The arrows are too thin, make them bolder"

Muse edits, re-exports, and sends you the new image. Script edits and
regeneration are deterministic — only what you asked for changes,
everything else stays put. Nothing gets messed up.

**2. Edit it yourself on the web** 🖱️

Single-click the `.drawio` open in Muse, select all, copy, paste into
[app.diagrams.net](https://app.diagrams.net).
Every box, line, and word is an independent component: drag to reposition,
recolor, reword — as intuitive as PowerPoint. Nothing to install locally.

**3. Swap components** 🔄

Don't like an icon? Two ways to replace it:

- Ask Muse: tell it "this gear looks bad, generate a nicer one and swap it in" —
  it regenerates that component with AI and swaps it seamlessly, nothing else moves
- Do it manually: have Muse generate the new image, delete the old component
  in [app.diagrams.net](https://app.diagrams.net), drag the new one in, position it

---

Mix and match: big changes go to Muse, small tweaks by hand —
"beautiful + editable" finally comes full circle. ⭕

## 🚀 Getting started

**👶 Beginner version** (one sentence):

> Tell your Muse: "Check out this open-source project scientific-illustrator-muse
> and install it on your remote computer." Then send it an image:
> "Please redraw this for me."
>
> That's it. 😎

**👨‍💻 Technical version**: see [QUICKSTART.md](QUICKSTART.md) — your first diagram in three steps.

```bash
git clone https://github.com/song-squared/scientific-illustrator-muse.git
cd scientific-illustrator-muse
./setup.sh
```

## 📋 Workflow

[SKILL.md](SKILL.md) — the full spec: write XML directly, embed AI-generated icons,
four self-checks after drawing (colors / layout / 3D-vs-2D style / text). ✅

## 📁 Contents

| File | Description |
|---|---|
| `QUICKSTART.md` | Three-step quickstart 🚀 |
| `SKILL.md` | Full workflow spec 📋 |
| `setup.sh` | One-click install: Xvfb + draw.io Desktop + system deps ⚙️ |
| `mcp-call.sh` | Batch call entrypoint 🔧 |
| `mcp-shim.mjs` | MCP shim: stdio JSON-RPC forwarding 🔌 |
| `scripts/` | draw.io MCP server (vendored from upstream) 📦 |

## 💻 Environment

- Linux (tested on Ubuntu 22.04/24.04), Node.js 18+, Python 3 + pillow
- draw.io Desktop (installed automatically by `setup.sh`)

## 🙏 Credits

- [icebird1998/scientific-illustrator](https://github.com/icebird1998/scientific-illustrator) (MIT):
  draw.io MCP server reused as-is, only fixed the data URI semicolon truncation
- draw.io Desktop (Apache 2.0)

## 🌟 What's next

This is one experiment in a new way to play with Muse: **the remote computer as workbench**.

If you've used Muse's remote computer to build something else interesting,
share it — looking forward to more new ways to play with Muse. 🎉

## 📄 License

MIT
