/* Lists every fixed line the app can speak, in the form the voice library records it.

     python3 -m http.server 8099   # from melo-mood-app/
     node tools/voice_lines.js http://localhost:8099/index.html

   writes tools/voice_batches.json: batches of up to 20 lines (~380 characters) for one
   ElevenLabs take each (eleven_multilingual_v2: the 1.5 s break tags between lines are
   what the cutter splits on). Read a batch's `prompt` in one take, then cut it with
   tools/voice_lib.py. Lines are deduplicated across screens and keyed by the same hash
   the app looks up (fnv/libText in index.html), so nothing is recorded twice. */
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const url = process.argv[2] || 'http://localhost:8099/index.html';
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto(url);
  await p.waitForTimeout(800);
  const lines = await p.evaluate(() => {
    const N = '＿', seen = new Map();
    const add = L => L.filter(l => speakableLine(l)).forEach(l => {
      const t = libText(l.t, N); if (t && !seen.has(fnv(t))) seen.set(fnv(t), t);
    });
    const realDay = todayKey;
    // scenes reshuffle their affirmations by day and add tone-specific lines
    for (const k of Object.keys(SCENES)) for (const tone of Object.keys(TONES)) for (let d = 0; d < 21; d++) {
      window.todayKey = () => 'D' + d; add(buildScene(k, { tone, name: N, minutes: SCENES[k].min }));
    }
    for (const goal of Object.keys(GOALS)) for (const tone of Object.keys(TONES)) for (const minutes of [1, 3, 7, 12]) for (let s = 0; s < 30; s++)
      add(buildScript({ goal, minutes, tone, name: N, seed: 's' + s }));
    const gl = Object.keys(GOALS);
    for (const a of gl) for (const c of gl) for (let d = 0; d < 14; d++) {
      window.todayKey = () => 'D' + d; add(buildSleep({ goals: a === c ? [a] : [a, c], name: N, minutes: 10 }));
    }
    window.todayKey = realDay;
    for (const k of Object.keys(THEME_SETS)) add(themeScript(k));
    return [...seen].map(([h, t]) => ({ h, t }));
  });
  await b.close();

  // what the voice reads: quote marks dropped, "—— author" read as a new sentence
  const say = t => t.replace(/[「」]/g, '').replace(/\s*——\s*/g, '。').replace(/(\d)-(?=\d)/g, '$1、')
    .replace(/…+/g, '，').replace(/\s*·\s*/g, '，').replace(/\s*，\s*/g, '，');
  const batches = [];
  let cur = [], chars = 0;
  for (const l of lines) {
    if (cur.length && (cur.length >= 20 || chars + l.t.length > 380)) { batches.push(cur); cur = []; chars = 0; }
    cur.push(l); chars += l.t.length;
  }
  if (cur.length) batches.push(cur);
  const out = batches.map((ls, i) => ({ id: 'b' + String(i + 1).padStart(2, '0'), lines: ls, prompt: ls.map(l => say(l.t)).join('\n<break time="1.5s" />\n') }));
  fs.writeFileSync(path.join(__dirname, 'voice_batches.json'), JSON.stringify(out, null, 1));
  console.log(`${lines.length} lines, ${lines.reduce((a, l) => a + l.t.length, 0)} characters, ${out.length} batches`);
})();
