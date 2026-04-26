// F1 Strategist landing animation.
// Lines spawn from a single origin, draw the track, draw opponents, draw
// a decision timeline. Glow only on the leading tip of each in-flight line;
// after a line is complete, it's flat.
//
// Aesthetic constraint: monochrome, no neon, no permanent glow except a single
// pit-decision pulse at the climax.

(function () {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";

  // -------------------------------------------------------------------------
  // Track geometry — a representative simplified Spa-like contour.
  // Coordinates in viewBox space (0..1000, 0..600). Closed polyline.
  // Generated from a smoothed approximation; not literal Spa, but reads as
  // "F1 track" silhouette.
  // -------------------------------------------------------------------------
  const TRACK = [
    [240, 320], [220, 280], [220, 240], [260, 210], [310, 195], [360, 195],
    [410, 210], [460, 220], [510, 220], [560, 215], [610, 220], [660, 240],
    [710, 270], [750, 305], [770, 345], [765, 385], [740, 415], [700, 430],
    [660, 425], [620, 405], [600, 380], [600, 355], [610, 335], [605, 315],
    [580, 305], [550, 315], [520, 345], [490, 380], [450, 410], [410, 425],
    [370, 425], [330, 410], [295, 385], [270, 355], [250, 335], [240, 320]
  ];

  const ORIGIN = { x: 500, y: 320 };

  // Opponent grid positions (where ghost lines emerge from offscreen to)
  const OPPONENTS = [
    { x: 260, y: 215, label: "#1" },
    { x: 410, y: 200, label: "#4" },
    { x: 560, y: 220, label: "#44" },
    { x: 710, y: 280, label: "#16" },
    { x: 700, y: 425, label: "#55" },
  ];

  // Decision timeline — each entry shows up one at a time
  const DECISIONS = [
    { lap: "L00", cmd: "INSPECT_TYRE_DEGRADATION", key: false },
    { lap: "L02", cmd: "CHECK_OPPONENT_STRATEGY 44", key: false },
    { lap: "L04", cmd: "ASSESS_UNDERCUT_WINDOW", key: false },
    { lap: "L05", cmd: "REQUEST_FORECAST", key: true },
    { lap: "L06", cmd: "SET_MODE conserve", key: false },
    { lap: "L07", cmd: "RADIO_DRIVER \"box this lap\"", key: false },
    { lap: "L07", cmd: "PIT_NOW inter", key: true },
    { lap: "L08", cmd: "SET_MODE push", key: false },
    { lap: "L11", cmd: "DEFEND_POSITION", key: false },
    { lap: "L12", cmd: "DONE — score 0.95", key: true },
  ];

  // Hero copy — types itself
  const TITLE_TEXT = "AN LLM RACE STRATEGIST";
  const SUBTITLE_TEXT =
    "Lap 8 · Spa · light rain.  We trained an LLM to be the race engineer on the pit wall — " +
    "12 strategic decision points, hidden state, six-dimension reward.  Theme #2 long-horizon planning.";

  // -------------------------------------------------------------------------
  // Background canvas: subtle vignette + grid (very faint)
  // -------------------------------------------------------------------------
  function drawBg() {
    const c = document.getElementById("bg");
    const ctx = c.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    function resize() {
      c.width = window.innerWidth * dpr;
      c.height = window.innerHeight * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      paint();
    }
    function paint() {
      const w = window.innerWidth;
      const h = window.innerHeight;
      ctx.clearRect(0, 0, w, h);
      // very faint dot grid
      ctx.fillStyle = "rgba(232,232,232,0.03)";
      const step = 40;
      for (let x = step; x < w; x += step) {
        for (let y = step; y < h; y += step) {
          ctx.fillRect(x, y, 1, 1);
        }
      }
      // radial vignette toward edges
      const grad = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, Math.max(w, h) * 0.7);
      grad.addColorStop(0, "rgba(0,0,0,0)");
      grad.addColorStop(1, "rgba(0,0,0,0.55)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, w, h);
    }
    window.addEventListener("resize", resize);
    resize();
  }

  // -------------------------------------------------------------------------
  // Animation primitives
  // -------------------------------------------------------------------------
  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  // Append an SVG line that draws itself from (x1,y1) to (x2,y2) over `dur`.
  // While drawing, the path has a glow filter; after, the filter is removed
  // (clean flat line).
  function drawLine(parent, x1, y1, x2, y2, dur, klass) {
    const line = document.createElementNS(SVG_NS, "line");
    line.setAttribute("x1", x1);
    line.setAttribute("y1", y1);
    line.setAttribute("x2", x2);
    line.setAttribute("y2", y2);
    if (klass) line.setAttribute("class", klass);
    line.setAttribute("filter", "url(#tipGlow)");
    parent.appendChild(line);

    const len = Math.hypot(x2 - x1, y2 - y1);
    line.setAttribute("stroke-dasharray", String(len));
    line.setAttribute("stroke-dashoffset", String(len));
    // force reflow then animate
    line.getBoundingClientRect();
    line.style.transition = `stroke-dashoffset ${dur}ms linear`;
    line.setAttribute("stroke-dashoffset", "0");

    return new Promise(resolve => {
      setTimeout(() => {
        line.removeAttribute("filter");      // glow off after draw → clean flat
        line.style.transition = "";
        resolve(line);
      }, dur + 30);
    });
  }

  // Draw a polyline (sequence of points) one segment at a time.
  // Returns when fully drawn.
  async function drawPolyline(parent, points, dur, klass) {
    const total = points.length - 1;
    const per = Math.max(40, dur / total);
    for (let i = 0; i < total; i++) {
      const [x1, y1] = points[i];
      const [x2, y2] = points[i + 1];
      // sequential — wait for each segment (prevents jagged "all at once")
      // but use shorter waits to keep total wall-clock = dur
      // we pause for 60% of segment duration, line completes during that wait
      drawLine(parent, x1, y1, x2, y2, per, klass);
      await sleep(per * 0.55);
    }
    await sleep(per * 0.5); // final segment finishes
  }

  // Type text into an element character by character.
  async function typeInto(el, text, perChar) {
    el.textContent = "";
    for (let i = 0; i < text.length; i++) {
      el.textContent += text[i];
      await sleep(perChar + (Math.random() * 18 - 6));
    }
  }

  // Pop a list item into the timeline
  async function appendDecision(d, idx) {
    const ul = document.getElementById("decisions");
    const li = document.createElement("li");
    if (d.key) li.classList.add("key");
    li.innerHTML = `<span class="lap">${d.lap}</span><span class="cmd">${escapeHtml(d.cmd)}</span>`;
    ul.appendChild(li);
    await sleep(15);
    li.classList.add("in");
    if (d.key && d.cmd.startsWith("PIT_NOW")) {
      pulseAt(ORIGIN.x + 200, ORIGIN.y);   // the climax pulse
    }
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, c => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[c]));
  }

  // Draw a single bright pulse circle that fades — the "pit decision" climax glow
  function pulseAt(x, y) {
    const g = document.getElementById("decision-pulse");
    const c = document.createElementNS(SVG_NS, "circle");
    c.setAttribute("cx", x);
    c.setAttribute("cy", y);
    c.setAttribute("r", 2);
    c.setAttribute("class", "pit-pulse");
    c.setAttribute("filter", "url(#pulse)");
    g.appendChild(c);
    let r = 2;
    let opacity = 1;
    const id = setInterval(() => {
      r += 1.2;
      opacity -= 0.04;
      c.setAttribute("r", r);
      c.style.opacity = String(Math.max(0, opacity));
      if (opacity <= 0) {
        clearInterval(id);
        c.remove();
      }
    }, 16);
  }

  // -------------------------------------------------------------------------
  // The choreography
  // -------------------------------------------------------------------------
  async function run() {
    // Step 1 — single origin dot
    const originGroup = document.getElementById("origin");
    const dot = document.createElementNS(SVG_NS, "circle");
    dot.setAttribute("cx", ORIGIN.x);
    dot.setAttribute("cy", ORIGIN.y);
    dot.setAttribute("r", 1.5);
    dot.setAttribute("fill", "var(--accent)");
    dot.setAttribute("filter", "url(#tipGlow)");
    originGroup.appendChild(dot);
    await sleep(400);

    // Step 2 — lines spawn FROM origin to each track vertex (radial sketch)
    // then we connect them in order — gives the "drawing from a point" feel
    const trackGroup = document.getElementById("track-lines");
    const radialDur = 700;
    const promises = TRACK.map(([x, y], i) => {
      // staggered so they don't all snap at once
      return new Promise(r => setTimeout(() => {
        drawLine(trackGroup, ORIGIN.x, ORIGIN.y, x, y, radialDur, "radial").then(line => {
          // fade the radial spoke after a beat — keeps the polygon clean
          setTimeout(() => {
            line.style.transition = "opacity 600ms";
            line.style.opacity = "0";
            setTimeout(() => line.remove(), 700);
          }, 180);
          r();
        });
      }, i * 18));
    });
    await Promise.all(promises);
    await sleep(120);

    // Step 3 — connect the polygon (the actual track outline)
    await drawPolyline(trackGroup, TRACK, 1400, null);
    await sleep(200);

    // Step 4 — opponent ghost lines streak in from offscreen to grid positions
    const oppGroup = document.getElementById("opponent-lines");
    await Promise.all(OPPONENTS.map((o, i) => new Promise(r => setTimeout(() => {
      const fromX = o.x < 500 ? -50 : 1050;
      drawLine(oppGroup, fromX, o.y, o.x, o.y, 600, "opponent").then(() => {
        // small dot at landing point
        const c = document.createElementNS(SVG_NS, "circle");
        c.setAttribute("cx", o.x);
        c.setAttribute("cy", o.y);
        c.setAttribute("r", 1.6);
        c.setAttribute("fill", "var(--ink)");
        oppGroup.appendChild(c);
        // label
        const t = document.createElementNS(SVG_NS, "text");
        t.setAttribute("x", o.x + 6);
        t.setAttribute("y", o.y - 6);
        t.setAttribute("fill", "var(--dim)");
        t.setAttribute("font-size", "9");
        t.setAttribute("font-family", "monospace");
        t.textContent = o.label;
        t.style.opacity = "0";
        oppGroup.appendChild(t);
        setTimeout(() => { t.style.transition = "opacity 400ms"; t.style.opacity = "1"; }, 50);
        r();
      });
    }, i * 100))));
    await sleep(200);

    // Step 5 — telemetry ribbon (tiny lap-time chart in a corner)
    const tele = document.getElementById("telemetry");
    const baseX = 70, baseY = 540, w = 200, h = 38;
    // axes
    drawLine(tele, baseX, baseY, baseX + w, baseY, 350, "telemetry");
    drawLine(tele, baseX, baseY - h, baseX, baseY, 350, "telemetry");
    await sleep(380);
    // a sketched lap-time curve — varying for visual interest
    const lapCurve = [];
    const N = 12;
    for (let i = 0; i < N; i++) {
      const x = baseX + (i / (N - 1)) * w;
      const v = 0.55 + 0.18 * Math.sin(i * 0.7) + (i === 7 ? 0.22 : 0); // bump at L07 (pit)
      const y = baseY - v * h;
      lapCurve.push([x, y]);
    }
    await drawPolyline(tele, lapCurve, 800, "telemetry");
    await sleep(120);

    // Step 6 — type the title and subtitle
    const titleEl = document.getElementById("title-text");
    const subEl = document.getElementById("subtitle");
    await typeInto(titleEl, TITLE_TEXT, 42);
    titleEl.classList.add("done");
    await sleep(200);
    await typeInto(subEl, SUBTITLE_TEXT, 14);
    await sleep(300);

    // Step 7 — decisions stream into the timeline
    for (let i = 0; i < DECISIONS.length; i++) {
      await appendDecision(DECISIONS[i], i);
      await sleep(DECISIONS[i].key ? 380 : 200);
    }

    // Step 8 — final score reveal
    const score = document.getElementById("score-readout");
    await typeInto(score, "0.95   (untrained: 0.38)", 28);
  }

  // Boot
  window.addEventListener("DOMContentLoaded", () => {
    drawBg();
    run().catch(err => console.error(err));
  });
})();
