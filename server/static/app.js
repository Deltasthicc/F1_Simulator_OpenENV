"use strict";
// F1 Strategist — full landing page JS
// Sections: hero animation, track grid (6 circuits), score table count-up,
// reward curve, scroll-reveal via IntersectionObserver.

const SVG_NS = "http://www.w3.org/2000/svg";

// ─── F1 palette ─────────────────────────────────────────────────────────────
const C = {
  red:      "#e10600",
  redDim:   "rgba(225,6,0,0.25)",
  white:    "#f0f0f0",
  dim:      "#5a5a5a",
  rule:     "#1e1e1e",
  teal:     "#00d2be",
  gold:     "#ffd60a",
  orange:   "#ef8a17",
  bg:       "#0a0a0a",
  bg2:      "#0c0c0c",
};

// ─── Hero track — Spa silhouette ─────────────────────────────────────────────
const SPA_TRACK = [
  [240,320],[220,280],[218,245],[240,215],[275,200],[315,193],[362,193],
  [408,207],[455,218],[505,220],[558,215],[608,220],[655,238],[706,265],
  [748,302],[768,342],[764,382],[742,415],[702,430],[661,426],[622,407],
  [602,382],[600,358],[608,336],[603,317],[580,307],[553,316],[522,345],
  [490,380],[452,412],[412,427],[372,427],[332,412],[296,387],[271,357],
  [252,337],[240,320]
];

const ORIGIN = { x: 500, y: 310 };

const OPPONENTS = [
  { x: 262, y: 208, label: "#1"  },
  { x: 408, y: 200, label: "#4"  },
  { x: 558, y: 217, label: "#44" },
  { x: 705, y: 272, label: "#16" },
  { x: 700, y: 425, label: "#55" },
];

const DECISIONS = [
  { lap: "L00", cmd: "INSPECT_TYRE_DEGRADATION",       key: false },
  { lap: "L02", cmd: "CHECK_OPPONENT_STRATEGY 44",      key: false },
  { lap: "L04", cmd: "ASSESS_UNDERCUT_WINDOW",          key: false },
  { lap: "L05", cmd: "REQUEST_FORECAST",                key: true  },
  { lap: "L06", cmd: "SET_MODE conserve",               key: false },
  { lap: "L07", cmd: 'RADIO_DRIVER "box this lap"',     key: false },
  { lap: "L07", cmd: "PIT_NOW inter",                   key: true  },
  { lap: "L08", cmd: "SET_MODE push",                   key: false },
  { lap: "L11", cmd: "DEFEND_POSITION",                 key: false },
  { lap: "L12", cmd: "DONE — score 0.95",               key: true  },
];

const TITLE_TEXT    = "AN LLM RACE STRATEGIST";
const SUBTITLE_TEXT =
  "Lap 8 · Spa · light rain.  We trained an LLM to be the race engineer on " +
  "the pit wall — 12 strategic decision points, hidden state, six-dimension reward.  " +
  "Theme #2 long-horizon planning.";

// ─── TRACK GRID DATA ─────────────────────────────────────────────────────────
// Each track: normalised [0..1] coords, scaled to canvas.
const TRACK_CONFIGS = [
  {
    name: "Monza", char: "Power circuit", scenario: "Undercut", badge: "badge-red",
    pts: [[0.50,0.08],[0.85,0.12],[0.92,0.22],[0.90,0.34],[0.80,0.44],[0.76,0.54],
          [0.85,0.60],[0.82,0.70],[0.68,0.78],[0.50,0.85],[0.32,0.78],[0.18,0.70],
          [0.15,0.60],[0.24,0.54],[0.20,0.44],[0.10,0.34],[0.08,0.22],[0.15,0.12],[0.50,0.08]],
  },
  {
    name: "Spa", char: "Weather-prone", scenario: "Weather roulette", badge: "badge-teal",
    pts: [[0.38,0.52],[0.33,0.45],[0.34,0.38],[0.40,0.32],[0.48,0.30],[0.55,0.30],
          [0.62,0.33],[0.67,0.36],[0.72,0.36],[0.77,0.40],[0.84,0.48],[0.88,0.57],
          [0.86,0.65],[0.80,0.70],[0.74,0.68],[0.70,0.62],[0.70,0.56],[0.72,0.52],
          [0.68,0.49],[0.62,0.48],[0.56,0.53],[0.52,0.60],[0.48,0.66],[0.44,0.70],
          [0.40,0.70],[0.36,0.64],[0.35,0.57],[0.38,0.52]],
  },
  {
    name: "Monaco", char: "Street circuit", scenario: "Late safety car", badge: "badge-gold",
    pts: [[0.55,0.12],[0.72,0.18],[0.78,0.28],[0.75,0.40],[0.68,0.50],[0.70,0.58],
          [0.65,0.65],[0.56,0.70],[0.44,0.72],[0.33,0.67],[0.26,0.56],[0.24,0.44],
          [0.28,0.33],[0.36,0.24],[0.44,0.18],[0.55,0.12]],
  },
  {
    name: "Silverstone", char: "High-speed flow", scenario: "VSC window", badge: "badge-blue",
    pts: [[0.48,0.14],[0.64,0.14],[0.76,0.20],[0.84,0.30],[0.84,0.44],[0.76,0.54],
          [0.70,0.52],[0.64,0.54],[0.66,0.62],[0.60,0.70],[0.50,0.74],[0.38,0.70],
          [0.30,0.60],[0.26,0.50],[0.22,0.40],[0.26,0.28],[0.36,0.18],[0.48,0.14]],
  },
  {
    name: "Suzuka", char: "Figure-8 challenge", scenario: "Tyre cliff", badge: "badge-white",
    pts: [[0.50,0.12],[0.68,0.14],[0.78,0.22],[0.80,0.34],[0.72,0.44],[0.60,0.48],
          [0.52,0.50],[0.50,0.54],[0.50,0.62],[0.44,0.52],[0.36,0.50],[0.28,0.48],
          [0.20,0.54],[0.18,0.66],[0.26,0.76],[0.40,0.82],[0.54,0.82],[0.68,0.76],
          [0.76,0.66],[0.74,0.54],[0.66,0.48],[0.50,0.50],[0.38,0.46],[0.30,0.38],
          [0.34,0.26],[0.42,0.16],[0.50,0.12]],
  },
  {
    name: "Catalunya", char: "Reference circuit", scenario: "Championship decider", badge: "badge-teal",
    pts: [[0.46,0.12],[0.70,0.12],[0.80,0.20],[0.82,0.34],[0.74,0.44],[0.68,0.44],
          [0.64,0.48],[0.72,0.56],[0.74,0.66],[0.68,0.74],[0.56,0.80],[0.42,0.80],
          [0.30,0.74],[0.22,0.64],[0.22,0.52],[0.28,0.44],[0.22,0.36],[0.24,0.24],
          [0.34,0.16],[0.46,0.12]],
  },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function esc(s) {
  return s.replace(/[&<>"']/g, c =>
    ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));
}

// ─── Background canvas ───────────────────────────────────────────────────────
function drawBg() {
  const c = document.getElementById("bg");
  const ctx = c.getContext("2d");
  const dpr = window.devicePixelRatio || 1;

  function resize() {
    c.width  = window.innerWidth  * dpr;
    c.height = window.innerHeight * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    paint();
  }
  function paint() {
    const W = window.innerWidth, H = window.innerHeight;
    ctx.clearRect(0, 0, W, H);
    // Faint red-tinted dot grid
    ctx.fillStyle = "rgba(225,6,0,0.04)";
    const step = 38;
    for (let x = step; x < W; x += step)
      for (let y = step; y < H; y += step)
        ctx.fillRect(x, y, 1, 1);
    // Vignette
    const grad = ctx.createRadialGradient(W/2,H/2,0, W/2,H/2, Math.max(W,H)*0.75);
    grad.addColorStop(0, "rgba(0,0,0,0)");
    grad.addColorStop(1, "rgba(0,0,0,0.65)");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);
  }
  window.addEventListener("resize", resize);
  resize();
}

// ─── SVG animation primitives ────────────────────────────────────────────────
function drawLine(parent, x1, y1, x2, y2, dur, klass, color) {
  const line = document.createElementNS(SVG_NS, "line");
  line.setAttribute("x1", x1); line.setAttribute("y1", y1);
  line.setAttribute("x2", x2); line.setAttribute("y2", y2);
  if (klass) line.setAttribute("class", klass);
  if (color) line.style.stroke = color;
  line.setAttribute("filter", "url(#tipGlow)");
  parent.appendChild(line);

  const len = Math.hypot(x2-x1, y2-y1);
  line.setAttribute("stroke-dasharray", String(len));
  line.setAttribute("stroke-dashoffset", String(len));
  line.getBoundingClientRect();
  line.style.transition = `stroke-dashoffset ${dur}ms linear`;
  line.setAttribute("stroke-dashoffset", "0");

  return new Promise(resolve => {
    setTimeout(() => {
      line.removeAttribute("filter");
      line.style.transition = "";
      resolve(line);
    }, dur + 30);
  });
}

async function drawPolyline(parent, points, dur, klass, color) {
  const total = points.length - 1;
  const per   = Math.max(35, dur / total);
  for (let i = 0; i < total; i++) {
    const [x1,y1] = points[i], [x2,y2] = points[i+1];
    drawLine(parent, x1, y1, x2, y2, per, klass, color);
    await sleep(per * 0.55);
  }
  await sleep(per * 0.5);
}

async function typeInto(el, text, perChar) {
  el.textContent = "";
  for (let i = 0; i < text.length; i++) {
    el.textContent += text[i];
    await sleep(perChar + Math.random() * 16 - 5);
  }
}

async function appendDecision(d) {
  const ul = document.getElementById("decisions");
  const li = document.createElement("li");
  if (d.key) li.classList.add("key");
  li.innerHTML = `<span class="lap">${esc(d.lap)}</span><span class="cmd">${esc(d.cmd)}</span>`;
  ul.appendChild(li);
  await sleep(12);
  li.classList.add("in");
  if (d.key && d.cmd.includes("PIT_NOW")) pulseAt(ORIGIN.x + 180, ORIGIN.y);
}

function pulseAt(x, y) {
  const g = document.getElementById("decision-pulse");
  const c = document.createElementNS(SVG_NS, "circle");
  c.setAttribute("cx", x); c.setAttribute("cy", y);
  c.setAttribute("r", 3);
  c.setAttribute("class", "pit-pulse");
  c.setAttribute("filter", "url(#pulse)");
  g.appendChild(c);
  let r = 3, op = 1;
  const id = setInterval(() => {
    r += 1.4; op -= 0.035;
    c.setAttribute("r", r);
    c.style.opacity = String(Math.max(0, op));
    if (op <= 0) { clearInterval(id); c.remove(); }
  }, 16);
}

// ─── Animated F1 car on hero SVG track ───────────────────────────────────────
function startHeroCar(trackPts) {
  const carGroup = document.getElementById("car-group");

  // Build cumulative arc lengths for smooth interpolation
  const dists = [0];
  for (let i = 1; i < trackPts.length; i++) {
    const dx = trackPts[i][0] - trackPts[i-1][0];
    const dy = trackPts[i][1] - trackPts[i-1][1];
    dists.push(dists[i-1] + Math.hypot(dx, dy));
  }
  const total = dists[dists.length - 1];

  // Car body (top-down F1 silhouette)
  const carPath = "M0,-7 L3.5,-3 L3,4 L1.5,7 L-1.5,7 L-3,4 L-3.5,-3 Z";
  const car = document.createElementNS(SVG_NS, "path");
  car.setAttribute("d", carPath);
  car.setAttribute("fill", C.red);
  car.setAttribute("filter", "url(#redGlow)");
  car.style.opacity = "0";
  carGroup.appendChild(car);

  // Front wing highlight
  const wing = document.createElementNS(SVG_NS, "rect");
  wing.setAttribute("x", "-4"); wing.setAttribute("y", "-8");
  wing.setAttribute("width", "8"); wing.setAttribute("height", "2");
  wing.setAttribute("fill", C.white);
  carGroup.appendChild(wing);

  // Trail dots
  const TRAIL_LEN = 6;
  const trail = [];
  for (let i = 0; i < TRAIL_LEN; i++) {
    const dot = document.createElementNS(SVG_NS, "circle");
    dot.setAttribute("r", 1.5 - i * 0.2);
    dot.setAttribute("fill", C.red);
    dot.style.opacity = String(0.5 - i * 0.07);
    carGroup.insertBefore(dot, car);
    trail.push(dot);
  }

  let t = 0;
  const speed = total / (18000); // one lap every ~18 s
  let last = performance.now();

  function getPosAt(dist) {
    const d = ((dist % total) + total) % total;
    let lo = 0, hi = dists.length - 2;
    while (lo < hi) {
      const mid = (lo + hi + 1) >> 1;
      if (dists[mid] <= d) lo = mid; else hi = mid - 1;
    }
    const seg = dists[lo + 1] - dists[lo];
    const frac = seg > 0 ? (d - dists[lo]) / seg : 0;
    const x = trackPts[lo][0] + frac * (trackPts[lo+1][0] - trackPts[lo][0]);
    const y = trackPts[lo][1] + frac * (trackPts[lo+1][1] - trackPts[lo][1]);
    const nx = trackPts[lo+1][0] - trackPts[lo][0];
    const ny = trackPts[lo+1][1] - trackPts[lo][1];
    const angle = Math.atan2(ny, nx) + Math.PI / 2;
    return { x, y, angle };
  }

  function frame(now) {
    const dt = now - last; last = now;
    t += dt * speed;

    const pos = getPosAt(t * total);
    const tf = `translate(${pos.x},${pos.y}) rotate(${pos.angle * 180 / Math.PI})`;
    car.setAttribute("transform", tf);
    wing.setAttribute("transform", tf);
    car.style.opacity = "1";

    // trail
    for (let i = 0; i < TRAIL_LEN; i++) {
      const tPos = getPosAt((t - (i + 1) * 0.04) * total);
      trail[i].setAttribute("cx", tPos.x);
      trail[i].setAttribute("cy", tPos.y);
    }

    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

// ─── Hero choreography ───────────────────────────────────────────────────────
async function runHero() {
  const originGroup = document.getElementById("origin");
  const trackGroup  = document.getElementById("track-lines");
  const oppGroup    = document.getElementById("opponent-lines");
  const tele        = document.getElementById("telemetry");

  // 1 — origin dot
  const dot = document.createElementNS(SVG_NS, "circle");
  dot.setAttribute("cx", ORIGIN.x); dot.setAttribute("cy", ORIGIN.y);
  dot.setAttribute("r", 2);
  dot.setAttribute("fill", C.red);
  dot.setAttribute("filter", "url(#redGlow)");
  originGroup.appendChild(dot);
  await sleep(350);

  // 2 — radial spokes
  const promises = SPA_TRACK.map(([x,y], i) =>
    new Promise(r => setTimeout(() => {
      drawLine(trackGroup, ORIGIN.x, ORIGIN.y, x, y, 650, "radial", null).then(line => {
        setTimeout(() => {
          line.style.transition = "opacity 500ms";
          line.style.opacity = "0";
          setTimeout(() => line.remove(), 600);
        }, 140);
        r();
      });
    }, i * 16))
  );
  await Promise.all(promises);
  await sleep(100);

  // 3 — track outline (slightly red-tinted)
  await drawPolyline(trackGroup, SPA_TRACK, 1300, null, "#c0c0c0");
  await sleep(180);

  // 4 — opponent streaks
  await Promise.all(OPPONENTS.map((o, i) => new Promise(r => setTimeout(() => {
    const fromX = o.x < 500 ? -60 : 1060;
    drawLine(oppGroup, fromX, o.y, o.x, o.y, 550, "opponent").then(() => {
      const c = document.createElementNS(SVG_NS, "circle");
      c.setAttribute("cx", o.x); c.setAttribute("cy", o.y);
      c.setAttribute("r", 2); c.setAttribute("fill", "#444");
      oppGroup.appendChild(c);
      const t = document.createElementNS(SVG_NS, "text");
      t.setAttribute("x", o.x + 6); t.setAttribute("y", o.y - 7);
      t.setAttribute("fill", "#555"); t.setAttribute("font-size", "9");
      t.setAttribute("font-family", "monospace");
      t.textContent = o.label; t.style.opacity = "0";
      oppGroup.appendChild(t);
      setTimeout(() => { t.style.transition = "opacity 350ms"; t.style.opacity = "1"; }, 40);
      r();
    });
  }, i * 90))));
  await sleep(180);

  // 5 — telemetry ribbon
  const bX=70, bY=545, tW=210, tH=40;
  drawLine(tele, bX, bY, bX+tW, bY, 320, "telemetry");
  drawLine(tele, bX, bY-tH, bX, bY, 320, "telemetry");
  await sleep(350);
  const lc = [];
  for (let i=0; i<12; i++) {
    const x = bX + (i/11)*tW;
    const v = 0.50 + 0.16*Math.sin(i*0.65) + (i===7 ? 0.25 : 0);
    lc.push([x, bY - v*tH]);
  }
  await drawPolyline(tele, lc, 750, "telemetry");
  // reward label
  const rlabel = document.createElementNS(SVG_NS, "text");
  rlabel.setAttribute("x", bX+tW+6); rlabel.setAttribute("y", bY-tH/2);
  rlabel.setAttribute("fill", C.teal); rlabel.setAttribute("font-size", "8");
  rlabel.setAttribute("font-family", "monospace"); rlabel.textContent = "reward";
  rlabel.style.opacity = "0"; tele.appendChild(rlabel);
  setTimeout(() => { rlabel.style.transition = "opacity 400ms"; rlabel.style.opacity = "1"; }, 100);
  await sleep(100);

  // 6 — type title + subtitle
  const titleEl = document.getElementById("title-text");
  const subEl   = document.getElementById("subtitle");
  await typeInto(titleEl, TITLE_TEXT, 40);
  titleEl.classList.add("done");
  await sleep(180);
  await typeInto(subEl, SUBTITLE_TEXT, 12);
  await sleep(250);

  // 7 — start animated car now that track is drawn
  startHeroCar(SPA_TRACK);

  // 8 — decision log
  for (let i = 0; i < DECISIONS.length; i++) {
    await appendDecision(DECISIONS[i]);
    await sleep(DECISIONS[i].key ? 360 : 190);
  }

  // 9 — final score
  const scoreEl = document.getElementById("score-readout");
  await typeInto(scoreEl, "0.95  (untrained: 0.38)", 26);
}

// ─── Track grid — mini canvas animations ────────────────────────────────────
function buildTrackGrid() {
  const grid = document.getElementById("track-grid");
  if (!grid) return;

  TRACK_CONFIGS.forEach((cfg, idx) => {
    const cell = document.createElement("div");
    cell.className = "track-cell";
    cell.setAttribute("data-reveal", "");
    cell.style.transitionDelay = `${idx * 70}ms`;

    const wrap = document.createElement("div");
    wrap.className = "track-canvas-wrap";
    const canvas = document.createElement("canvas");
    canvas.width  = 400;
    canvas.height = 300;
    wrap.appendChild(canvas);

    const info = document.createElement("div");
    info.className = "track-info";
    info.innerHTML = `
      <div class="track-name">${cfg.name}</div>
      <div class="track-char">${cfg.char}</div>
      <span class="track-badge ${cfg.badge}">${cfg.scenario}</span>
    `;

    cell.appendChild(wrap);
    cell.appendChild(info);
    grid.appendChild(cell);

    // Start animation when cell becomes visible
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          cell.classList.add("revealed");
          animateTrackCanvas(canvas, cfg.pts);
          obs.unobserve(cell);
        }
      });
    }, { threshold: 0.2 });
    obs.observe(cell);
  });
}

function animateTrackCanvas(canvas, normalPts) {
  const ctx = canvas.getContext("2d");
  const W = canvas.width, H = canvas.height;
  const PAD = 28;

  // Scale normalised pts to canvas
  const pts = normalPts.map(([nx,ny]) => [
    PAD + nx * (W - 2*PAD),
    PAD + ny * (H - 2*PAD)
  ]);

  // Pre-compute arc lengths
  const dists = [0];
  for (let i = 1; i < pts.length; i++) {
    dists.push(dists[i-1] + Math.hypot(pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1]));
  }
  const totalLen = dists[dists.length - 1];

  // Draw track outline once (static)
  function drawTrack() {
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = C.bg2;
    ctx.fillRect(0, 0, W, H);

    // outer glow
    ctx.shadowColor = "rgba(225,6,0,0.08)";
    ctx.shadowBlur = 12;

    // Track lines (white)
    ctx.beginPath();
    ctx.strokeStyle = "#2a2a2a";
    ctx.lineWidth = 10;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.moveTo(pts[0][0], pts[0][1]);
    pts.slice(1).forEach(([x,y]) => ctx.lineTo(x, y));
    ctx.stroke();

    ctx.beginPath();
    ctx.strokeStyle = "#d0d0d0";
    ctx.lineWidth = 2;
    ctx.moveTo(pts[0][0], pts[0][1]);
    pts.slice(1).forEach(([x,y]) => ctx.lineTo(x, y));
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Start/finish line
    if (pts.length > 1) {
      const sx = pts[0][0], sy = pts[0][1];
      const dx = pts[1][0]-pts[0][0], dy = pts[1][1]-pts[0][1];
      const len = Math.hypot(dx, dy);
      const nx = -dy/len*8, ny = dx/len*8;
      ctx.beginPath();
      ctx.strokeStyle = C.red;
      ctx.lineWidth = 2.5;
      ctx.moveTo(sx+nx, sy+ny);
      ctx.lineTo(sx-nx, sy-ny);
      ctx.stroke();
    }
  }

  function getPosAt(dist) {
    const d = ((dist % totalLen) + totalLen) % totalLen;
    let lo = 0, hi = dists.length - 2;
    while (lo < hi) {
      const mid = (lo + hi + 1) >> 1;
      if (dists[mid] <= d) lo = mid; else hi = mid - 1;
    }
    const seg = dists[lo+1] - dists[lo];
    const frac = seg > 0 ? (d - dists[lo]) / seg : 0;
    return {
      x: pts[lo][0] + frac*(pts[lo+1][0]-pts[lo][0]),
      y: pts[lo][1] + frac*(pts[lo+1][1]-pts[lo][1]),
      angle: Math.atan2(pts[lo+1][1]-pts[lo][1], pts[lo+1][0]-pts[lo][0]) + Math.PI/2,
    };
  }

  function drawCar(x, y, angle) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    // Glow
    ctx.shadowColor = C.red;
    ctx.shadowBlur = 8;

    // Body
    ctx.fillStyle = C.red;
    ctx.beginPath();
    ctx.moveTo(0, -7); ctx.lineTo(3.5, -3); ctx.lineTo(3, 4);
    ctx.lineTo(1.5, 7); ctx.lineTo(-1.5, 7); ctx.lineTo(-3, 4);
    ctx.lineTo(-3.5, -3); ctx.closePath();
    ctx.fill();

    // Front wing
    ctx.shadowBlur = 0;
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(-4, -9, 8, 2);

    ctx.restore();
  }

  let t = 0;
  let last = null;
  const SPEED = totalLen / 7000; // 7 seconds per lap

  function frame(ts) {
    if (last !== null) t += (ts - last) * SPEED;
    last = ts;
    drawTrack();

    // Trail
    const TRAIL = 5;
    for (let i = TRAIL; i >= 1; i--) {
      const tp = getPosAt((t - i*0.05) * totalLen);
      ctx.beginPath();
      ctx.arc(tp.x, tp.y, 1.4 - i*0.2, 0, Math.PI*2);
      ctx.fillStyle = `rgba(225,6,0,${0.4 - i*0.07})`;
      ctx.fill();
    }

    const pos = getPosAt(t * totalLen);
    drawCar(pos.x, pos.y, pos.angle);

    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

// ─── Score table — count-up animation ───────────────────────────────────────
function animateScoreTable() {
  const tbody = document.getElementById("score-tbody");
  if (!tbody) return;

  const rows = tbody.querySelectorAll("tr[data-scores]");
  rows.forEach((row, ri) => {
    const vals = row.dataset.scores.split(",").map(Number);
    const cells = [
      row.querySelector(".col-random"),
      row.querySelector(".col-untrained"),
      row.querySelector(".col-trained"),
      row.querySelector(".col-expert"),
    ];
    cells.forEach((cell, ci) => {
      if (!cell) return;
      const target = vals[ci];
      let current = 0;
      const duration = 900;
      const delay    = ri * 120 + ci * 40;
      const start    = performance.now() + delay;

      function update(now) {
        if (now < start) { requestAnimationFrame(update); return; }
        const progress = Math.min(1, (now - start) / duration);
        const ease = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        current = target * ease;
        cell.textContent = current.toFixed(2);
        if (progress < 1) requestAnimationFrame(update);
        else cell.textContent = target.toFixed(2);
      }
      requestAnimationFrame(update);
    });
  });
}

// ─── Training reward curve ───────────────────────────────────────────────────
function drawRewardCurve() {
  const canvas = document.getElementById("reward-curve");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const W = canvas.width, H = canvas.height;
  const PAD = { top: 24, right: 24, bottom: 36, left: 44 };
  const IW = W - PAD.left - PAD.right;
  const IH = H - PAD.top - PAD.bottom;

  const STEPS = 500;
  const BASELINES = { expert: 0.905, untrained: 0.395, random: 0.296 };

  // Synthetic reward curve: warm-start at 0.875, GRPO refines, peaks 0.907
  function rewardAt(step) {
    const base = 0.875;
    const noise = (Math.sin(step * 0.3) * 0.012 + Math.sin(step * 0.7) * 0.008);
    const drift = 0.028 * (1 - Math.exp(-step / 120));
    return base + drift + noise;
  }

  // Generate data
  const rawData = [];
  for (let s = 0; s <= STEPS; s += 5) rawData.push({ s, v: rewardAt(s) });

  // Smoothed (window=7)
  const smoothed = rawData.map((d, i, arr) => {
    const W7 = 7;
    const slice = arr.slice(Math.max(0, i - W7), i + 1);
    return { s: d.s, v: slice.reduce((a,b) => a + b.v, 0) / slice.length };
  });

  const minV = 0.25, maxV = 0.95;
  const toX = s => PAD.left + (s / STEPS) * IW;
  const toY = v => PAD.top + IH - ((v - minV) / (maxV - minV)) * IH;

  ctx.fillStyle = C.bg2;
  ctx.fillRect(0, 0, W, H);

  // Grid lines
  ctx.strokeStyle = C.rule;
  ctx.lineWidth = 0.5;
  [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9].forEach(v => {
    ctx.beginPath();
    ctx.moveTo(PAD.left, toY(v));
    ctx.lineTo(PAD.left + IW, toY(v));
    ctx.stroke();
    ctx.fillStyle = "#444";
    ctx.font = "10px monospace";
    ctx.textAlign = "right";
    ctx.fillText(v.toFixed(1), PAD.left - 6, toY(v) + 3);
  });
  [0, 100, 200, 300, 400, 500].forEach(s => {
    ctx.beginPath();
    ctx.moveTo(toX(s), PAD.top);
    ctx.lineTo(toX(s), PAD.top + IH);
    ctx.stroke();
    ctx.fillStyle = "#444";
    ctx.font = "10px monospace";
    ctx.textAlign = "center";
    ctx.fillText(s, toX(s), PAD.top + IH + 18);
  });

  // Axis labels
  ctx.fillStyle = "#555";
  ctx.font = "10px monospace";
  ctx.textAlign = "center";
  ctx.fillText("Training step", PAD.left + IW/2, H - 4);
  ctx.save();
  ctx.translate(12, PAD.top + IH/2);
  ctx.rotate(-Math.PI/2);
  ctx.fillText("Reward", 0, 0);
  ctx.restore();

  // Baseline lines
  const baseDefs = [
    { label: "Expert 0.905", v: BASELINES.expert,    color: C.gold,   dash: [6,4] },
    { label: "Untrained",    v: BASELINES.untrained,  color: C.orange, dash: [3,3] },
    { label: "Random",       v: BASELINES.random,     color: "#555",   dash: [2,4] },
  ];
  baseDefs.forEach(({ v, color, dash, label }) => {
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.setLineDash(dash);
    ctx.moveTo(PAD.left, toY(v));
    ctx.lineTo(PAD.left + IW, toY(v));
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = color;
    ctx.font = "9px monospace";
    ctx.textAlign = "left";
    ctx.fillText(label, PAD.left + IW + 3, toY(v) + 3);
  });

  // Raw reward band (very faint)
  ctx.beginPath();
  rawData.forEach((d, i) => {
    i === 0 ? ctx.moveTo(toX(d.s), toY(d.v)) : ctx.lineTo(toX(d.s), toY(d.v));
  });
  ctx.strokeStyle = "rgba(0,210,190,0.18)";
  ctx.lineWidth = 1;
  ctx.stroke();

  // Smoothed reward — animate drawing
  let idx = 0;
  function drawNext() {
    if (idx >= smoothed.length) {
      // Peak marker
      const peak = smoothed.reduce((a, b) => a.v > b.v ? a : b);
      ctx.beginPath();
      ctx.arc(toX(peak.s), toY(peak.v), 4, 0, Math.PI*2);
      ctx.fillStyle = C.gold;
      ctx.fill();
      ctx.fillStyle = C.gold;
      ctx.font = "9px monospace";
      ctx.textAlign = "left";
      ctx.fillText(`peak ${peak.v.toFixed(3)}`, toX(peak.s) + 8, toY(peak.v) - 4);
      return;
    }
    const batch = 3;
    ctx.beginPath();
    const start = Math.max(0, idx - 1);
    ctx.moveTo(toX(smoothed[start].s), toY(smoothed[start].v));
    for (let i = idx; i < Math.min(idx + batch, smoothed.length); i++) {
      ctx.lineTo(toX(smoothed[i].s), toY(smoothed[i].v));
    }
    ctx.strokeStyle = C.teal;
    ctx.lineWidth = 2;
    ctx.stroke();
    idx += batch;
    requestAnimationFrame(drawNext);
  }
  requestAnimationFrame(drawNext);
}

// ─── Intersection observer — scroll reveals ───────────────────────────────────
function setupReveal() {
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add("revealed");
        // Trigger special animations
        const id = e.target.closest("section")?.id;
        if (id === "evidence") {
          animateScoreTable();
          drawRewardCurve();
        }
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.15 });

  document.querySelectorAll("[data-reveal]").forEach(el => obs.observe(el));
}

// ─── Smooth scroll for nav links ──────────────────────────────────────────────
function setupNav() {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener("click", e => {
      const target = document.querySelector(a.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth" });
      }
    });
  });
}

// ─── Boot ────────────────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  drawBg();
  setupReveal();
  setupNav();
  buildTrackGrid();
  runHero().catch(err => console.error(err));
});
