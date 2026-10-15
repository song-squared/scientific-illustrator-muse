// mcp-shim.mjs — Muse 版 scientific-illustrator 的 MCP client 垫片
//
// 用法: node mcp-shim.mjs <server-script.mjs>
// 然后按行从 stdin 读 JSON, 每行一种:
//   {"id":1,"tool":"drawio_live_status","arguments":{}}   -> 转成 tools/call
//   {"id":2,"method":"tools/list"}                        -> 透传 JSON-RPC
//   {"id":3,"method":"shutdown"}                         -> 关闭 server 并退出
//
// 每行输出一行 JSON:
//   {"id":1,"ok":true,"text":"...","structured":{...},"images":["/abs/path.png"]}
// 截图等 image 内容会落盘到 ./shots/, 绝不把 base64 打进 stdout。
// server 的 stderr 直接透出, 方便排错。

import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { promises as fs } from "node:fs";
import path from "node:path";
import os from "node:os";

const serverScript = process.argv[2];
if (!serverScript) {
  process.stderr.write("usage: node mcp-shim.mjs <server-script.mjs>\n");
  process.exit(2);
}

const SHIM_DIR = path.dirname(new URL(import.meta.url).pathname);
const SHOTS_DIR = path.join(SHIM_DIR, "shots");
await fs.mkdir(SHOTS_DIR, { recursive: true });

const server = spawn(process.execPath, [serverScript], {
  cwd: path.dirname(path.resolve(serverScript)),
  stdio: ["pipe", "pipe", "inherit"],
});
server.on("exit", (code) => {
  process.stderr.write(`[shim] server exited with code ${code}\n`);
  process.exit(code ?? 1);
});

const pending = new Map();
let nextId = 1;
const serverRl = createInterface({ input: server.stdout, crlfDelay: Infinity });
serverRl.on("line", (line) => {
  if (!line.trim()) return;
  let msg;
  try { msg = JSON.parse(line); } catch { return; }
  const cb = pending.get(msg.id);
  if (cb) { pending.delete(msg.id); cb(msg); }
});

function rpc(method, params) {
  return new Promise((resolve) => {
    const id = nextId++;
    pending.set(id, resolve);
    server.stdin.write(JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n");
  });
}

async function unwrap(result) {
  const out = { text: "", images: [] };
  const content = result?.content;
  if (Array.isArray(content)) {
    for (const part of content) {
      if (part.type === "text") out.text += part.text;
      else if (part.type === "image" && part.data) {
        const name = `shot-${Date.now()}-${Math.floor(Math.random() * 1e6)}.png`;
        const p = path.join(SHOTS_DIR, name);
        await fs.writeFile(p, Buffer.from(part.data, "base64"));
        out.images.push(p);
      }
    }
  }
  if (!out.text && !out.images.length && result && typeof result === "object") {
    // 非 tools/call 方法 (如 tools/list) 没有 content, 直接转储原始结果
    const dump = JSON.stringify(result, null, 2);
    out.text = dump.length > 60000 ? dump.slice(0, 60000) + "\n...[truncated]" : dump;
  }
  return out;
}

// 启动握手
const init = await rpc("initialize", {
  protocolVersion: "2025-06-18",
  capabilities: {},
  clientInfo: { name: "muse-shim", version: "0.1.0" },
});
if (init.error) {
  process.stderr.write(`[shim] initialize failed: ${JSON.stringify(init.error)}\n`);
  process.exit(1);
}
process.stderr.write(`[shim] connected: ${init.result?.serverInfo?.name} v${init.result?.serverInfo?.version}\n`);

const stdinRl = createInterface({ input: process.stdin, crlfDelay: Infinity });
for await (const line of stdinRl) {  if (!line.trim()) continue;
  let req;
  try { req = JSON.parse(line); } catch {
    process.stdout.write(JSON.stringify({ id: null, ok: false, error: "bad json" }) + "\n");
    continue;
  }
  const id = req.id ?? null;
  try {
    if (req.method === "shutdown") {
      server.kill();
      process.stdout.write(JSON.stringify({ id, ok: true }) + "\n");
      process.exit(0);
    }
    let res;
    if (req.method) {
      res = await rpc(req.method, req.params || {});
    } else if (req.tool) {
      res = await rpc("tools/call", { name: req.tool, arguments: req.arguments || {} });
    } else {
      throw new Error("need {tool} or {method}");
    }
    if (res.error) {
      process.stdout.write(JSON.stringify({ id, ok: false, error: res.error }) + "\n");
      continue;
    }
    const r = res.result || {};
    const isError = r.isError === true;
    const { text, images } = await unwrap(r);
    process.stdout.write(JSON.stringify({
      id, ok: !isError, text,
      ...(r.structuredContent !== undefined ? { structured: r.structuredContent } : {}),
      ...(images.length ? { images } : {}),
      ...(isError ? { toolError: true } : {}),
    }) + "\n");
  } catch (e) {
    process.stdout.write(JSON.stringify({ id, ok: false, error: String(e?.message || e) }) + "\n");
  }
}

// stdin 结束 (管道模式) -> 关闭 server 并退出, 不 hanging
server.kill();
await new Promise((r) => setTimeout(r, 300));
process.exit(0);
