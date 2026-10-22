// rust-deck example plugin: shows the time on every key with `plugin = "clock/time"`.
// Pressing the key toggles seconds, saved with setSettings, and shows a ✓. Plain Node.js, no packages.
// stdout is the protocol (one JSON message per line); log with console.error.
const readline = require("node:readline");

const keys = new Map(); // context → settings
const send = (m) => process.stdout.write(JSON.stringify(m) + "\n");

function show(context) {
  const t = new Date().toTimeString();
  send({ event: "setTitle", context, payload: { title: keys.get(context)?.seconds ? t.slice(0, 8) : t.slice(0, 5) } });
}
const tick = () => {
  keys.forEach((_, c) => show(c));
  setTimeout(tick, 1000 - (Date.now() % 1000)); // on the second, so seconds never skip
};
tick();

const lines = readline.createInterface({ input: process.stdin });
lines.on("line", (line) => {
  let m;
  try {
    m = JSON.parse(line);
  } catch {
    return console.error(`not JSON: ${line}`);
  }
  if (m.event === "willAppear" || m.event === "didReceiveSettings") keys.set(m.context, m.payload.settings);
  if (m.event === "willDisappear") keys.delete(m.context);
  if (m.event === "keyDown") {
    const settings = { ...keys.get(m.context), seconds: !keys.get(m.context)?.seconds };
    keys.set(m.context, settings);
    send({ event: "setSettings", context: m.context, payload: settings });
    send({ event: "showOk", context: m.context });
  }
  if (keys.has(m.context)) show(m.context);
});
lines.on("close", () => process.exit(0)); // stdin closed: the daemon stopped (or is restarting) us
