// Tripo Studio page driver for the agent-driven Tripo route.
//
// Paste this whole file into the browser tool's JavaScript call once per page
// load (it defines window.TS), then call the helpers in later calls, for
// example `await TS.state()` or `await TS.setGeometry({poly: 20000})`.
// Every helper was checked against studio.tripo3d.ai on 2026-11-13. When Tripo
// changes its page, fix the selector here and note the date.
//
// Rules the helpers follow (see docs/3d-units.md, "Tripo by agent"):
// - Tripo's menus open on pointer events, so plain .click() or a screenshot
//   click often does nothing. TS.fire() sends the full pointer sequence.
// - Never reload the page. In the Claude browser pane a reload signs Tripo out.
// - TS.generate(expected) refuses unless the button shows exactly the expected
//   price, clicks once, and waits for the new task. A second click starts a
//   second paid task.
(() => {
  const wait = (ms = 500) => new Promise((r) => setTimeout(r, ms));
  const text = (e) => (e && e.innerText ? e.innerText.replace(/\s+/g, " ").trim() : "");
  const TS = {
    version: "2026-11-14",
    wait,
    text,
    fire(el) {
      if (!el) throw new Error("TS.fire: no element");
      const o = { bubbles: true, cancelable: true, pointerType: "mouse", button: 0 };
      for (const t of ["pointerdown", "mousedown", "pointerup", "mouseup", "click"]) {
        el.dispatchEvent(new (t.startsWith("pointer") ? PointerEvent : MouseEvent)(t, o));
      }
    },
    find(label, { root = document, sel = "button,div,span,a,[role=option],[role=tab]", exact = false } = {}) {
      const hits = [...root.querySelectorAll(sel)].filter((e) => {
        const t = (e.innerText || "").trim();
        return exact ? t === label : t.startsWith(label);
      });
      return hits.sort((a, b) => a.innerText.length - b.innerText.length)[0];
    },
    escape() {
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    },
    signedIn() {
      return !/Sign up\/Log in/.test(document.body.innerText);
    },
    credits() {
      const m = document.body.innerText.match(/\n(\d[\d,]*)\n+Upgrade/);
      return m ? Number(m[1].replace(/,/g, "")) : null;
    },
    generateButtons() {
      return [...document.querySelectorAll("button")].filter((b) => /^Generate\b/.test(text(b)) && !/Multi-Views/.test(text(b)));
    },
    // Price on the Generate button: "Generate 30" -> 30, "Generate 100 0" (trial) -> 0.
    price() {
      const b = TS.generateButtons()[0];
      if (!b) return null;
      const nums = text(b).match(/\d+/g) || [];
      return nums.length ? Number(nums[nums.length - 1]) : null;
    },
    combos() {
      return [...document.querySelectorAll("[role=combobox]")].map(text);
    },
    tasks() {
      return [...document.querySelectorAll('a[href*="/workspace/generate/"]')].map((a) => ({
        id: a.getAttribute("href").split("/").pop(),
        state: /Generating/.test(a.innerText) ? "generating" : "done",
      }));
    },
    async state() {
      return {
        signedIn: TS.signedIn(),
        credits: TS.credits(),
        tab: text([...document.querySelectorAll("button")].find((b) => /rounded-l-full|bg-white/.test(b.className) && /HD Model|Smart Mesh/.test(text(b)))),
        price: TS.price(),
        combos: TS.combos(),
        tasks: TS.tasks(),
        url: location.href,
      };
    },
    // Model tab: "HD Model" or "Smart Mesh".
    async tab(name) {
      const b = [...document.querySelectorAll("button")].find((x) => text(x).startsWith(name));
      TS.fire(b);
      await wait(800);
      return TS.price();
    },
    // Input mode inside the upload box: 0 one picture, 1 multi-view, 2 batch, 3 text.
    async inputMode(index) {
      let box = TS.find("Upload", { exact: true }) || TS.find("Front", { exact: true }) || TS.find("Generating...");
      for (let i = 0; i < 8 && box; i++) {
        box = box.parentElement;
        if (box && box.querySelectorAll("button").length >= 4) break;
      }
      const btn = box && [...box.querySelectorAll("button")][index];
      TS.fire(btn);
      await wait(600);
      return text(box).slice(0, 120);
    },
    async pick(comboText, optionPrefix) {
      const c = [...document.querySelectorAll("[role=combobox]")].find((x) => text(x).includes(comboText));
      if (!c) throw new Error("TS.pick: no combobox with " + comboText);
      if (c.getAttribute("aria-expanded") !== "true") {
        TS.fire(c);
        await wait(500);
      }
      const op = [...document.querySelectorAll("[role=option]")].find((x) => text(x).startsWith(optionPrefix));
      if (!op) throw new Error("TS.pick: no option " + optionPrefix);
      op.focus();
      TS.fire(op);
      await wait(600);
      return text(c);
    },
    // HD Model model: "H3.1", "H3.0" or "H2.5".
    async model(prefix) {
      return TS.pick("H", prefix);
    },
    panel(marker) {
      return [...document.querySelectorAll("[data-state=open]")].find((d) => d.innerText.includes(marker));
    },
    setNumber(input, value) {
      Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set.call(input, String(value));
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
      input.dispatchEvent(new FocusEvent("blur", { bubbles: true }));
    },
    // HD Model "Geometry & Texture" panel. Switch order on 2026-11-13:
    // Ultra Mesh Quality, AI Complete, Texture, Remove Lighting, PBR.
    async setGeometry({ ultra = false, aiComplete = false, texture = true, quality = "2K", topology = "Triangle", poly = 20000, removeLighting = true, pbr = true } = {}) {
      let p = TS.panel("Ultra Mesh Quality");
      if (!p) {
        TS.fire(TS.find("Geometry & Texture"));
        await wait(700);
        p = TS.panel("Ultra Mesh Quality");
      }
      if (!p) throw new Error("TS.setGeometry: panel did not open");
      const sw = [...p.querySelectorAll("[role=switch]")];
      const want = [ultra, aiComplete, texture, removeLighting, pbr];
      for (let i = 0; i < Math.min(sw.length, want.length); i++) {
        if ((sw[i].getAttribute("aria-checked") === "true") !== want[i]) {
          sw[i].click();
          await wait(400);
        }
      }
      const btn = (t) => [...p.querySelectorAll("button,div")].find((e) => e.innerText.trim() === t);
      if (texture && btn(quality)) btn(quality).click();
      await wait(300);
      if (btn(topology)) btn(topology).click();
      await wait(300);
      const input = p.querySelector("input");
      if (input) TS.setNumber(input, poly);
      await wait(400);
      const out = { switches: sw.map((s) => s.getAttribute("aria-checked")), poly: input && input.value, price: TS.price() };
      TS.escape();
      return out;
    },
    // Smart Mesh "Topology" panel: Quad or Triangle, polycount 500 to 25,000
    // (quads) or 50,000 (triangles).
    async setSmartTopology({ topology = "Triangle", poly = 20000 } = {}) {
      let p = TS.panel("Use Same Polygon Count");
      if (!p) {
        TS.fire(TS.find("Topology", { exact: true }));
        await wait(700);
        p = TS.panel("Use Same Polygon Count");
      }
      if (!p) throw new Error("TS.setSmartTopology: panel did not open");
      const btn = (t) => [...p.querySelectorAll("button,div")].find((e) => e.innerText.trim() === t);
      if (btn(topology)) btn(topology).click();
      await wait(300);
      for (const input of p.querySelectorAll("input")) TS.setNumber(input, poly);
      await wait(400);
      const out = { poly: [...p.querySelectorAll("input")].map((i) => i.value), price: TS.price() };
      TS.escape();
      return out;
    },
    // Start one generation. Refuses unless the button shows the expected price.
    // Returns the new task id. Never call it twice for one arm: check
    // TS.tasks() first if a call timed out.
    async generate(expected, { timeoutMs = 20000 } = {}) {
      const price = TS.price();
      if (price !== expected) throw new Error(`TS.generate: price is ${price}, expected ${expected}`);
      const before = new Set(TS.tasks().map((t) => t.id));
      const b = TS.generateButtons()[0];
      b.click();
      const start = Date.now();
      while (Date.now() - start < timeoutMs) {
        await wait(1000);
        const fresh = TS.tasks().filter((t) => !before.has(t.id));
        if (fresh.length) return { started: fresh.map((t) => t.id), credits: TS.credits() };
      }
      return { started: [], note: "no new task seen yet; check TS.tasks() before clicking again", credits: TS.credits() };
    },
    // Signed links of the generated multi-view pictures (front, left, back, right).
    multiviewUrls() {
      return [...document.querySelectorAll("img")].filter((i) => /multiview_\d/.test(i.src)).map((i) => i.src).sort();
    },
  };
  // ---- Rig, Animate and Export pages (checked in Chrome on 2026-11-14) ----
  //
  // Some controls only react to a real pointer click from the browser tool,
  // not to a scripted click: the preset tiles, the animation picker's field
  // and its Select All. For those the helpers return a click point. Pass the
  // width of the screenshot frame the browser tool reports, because that
  // frame is smaller than the page and changes when the window is resized.
  Object.assign(TS, {
    point(el, frameWidth) {
      const r = el.getBoundingClientRect();
      const k = frameWidth / window.innerWidth;
      return [Math.round((r.left + r.width / 2) * k), Math.round((r.top + r.height / 2) * k)];
    },
    leaf(label) {
      return [...document.querySelectorAll("*")].filter((e) => (e.innerText || "").trim() === label).pop();
    },
    // Rig page: the Auto Rig button and its price. Click it with a real click.
    autoRig(frameWidth) {
      const b = [...document.querySelectorAll("button")].find((x) => /^Auto Rig/.test(text(x)));
      if (!b) return null;
      const nums = text(b).match(/\d+/g) || [];
      return { price: nums.length ? Number(nums[nums.length - 1]) : null, point: TS.point(b, frameWidth) };
    },
    rigged() {
      return /Rigged models can be used/.test(document.body.innerText);
    },
    // Animate page: scroll a preset tile into view and return its click point.
    // One real click applies the preset (free). Then await TS.retargeted().
    presetPoint(name, frameWidth) {
      const t = [...document.querySelectorAll("*")].find((e) => e.children.length === 0 && (e.innerText || "").trim() === name);
      if (!t) return null;
      const card = t.parentElement;
      card.scrollIntoView({ block: "center" });
      const r = card.getBoundingClientRect();
      const k = frameWidth / window.innerWidth;
      return [Math.round((r.left + r.width / 2) * k), Math.round((r.top + r.height / 2 - 12) * k)];
    },
    async retargeted(timeoutMs = 30000) {
      const start = Date.now();
      await wait(2000);
      while (Date.now() - start < timeoutMs && /Retargeting|Queuing/.test(document.body.innerText)) await wait(1500);
      return !/Retargeting|Queuing/.test(document.body.innerText);
    },
    // Export dialog on the Animate page. Order that works:
    //   1. real click on TS.exportOpenPoint()          (toolbar Export)
    //   2. real click on TS.animationFieldPoint()      (opens the clip picker)
    //   3. real click on TS.selectAllPoint()           (when the picker lists exactly the wanted clips)
    //   4. await TS.setStayInPlace(true)               (scripted click works)
    //   5. check TS.exportState(), then TS.startExport()  (scripted click works)
    // The switch only exists after at least one clip is selected, and the
    // dialog moves when rows appear, so never click it by a remembered point.
    exportOpenPoint(frameWidth) {
      const b = [...document.querySelectorAll("button")].filter((x) => text(x) === "Export").shift();
      return b ? TS.point(b, frameWidth) : null;
    },
    animationFieldPoint(frameWidth) {
      const label = TS.leaf("Number of Animations");
      if (!label) return null;
      const [x, y] = TS.point(label, frameWidth);
      // The field sits about 40 page pixels under its label.
      return [x, y + Math.round((40 * frameWidth) / window.innerWidth)];
    },
    selectAllPoint(frameWidth) {
      const sa = TS.leaf("Select All");
      if (!sa) return null;
      const [x, y] = TS.point(sa, frameWidth);
      return [x - 10, y];
    },
    staySwitch() {
      const label = [...document.querySelectorAll("*")].filter((e) => (e.innerText || "").trim().startsWith("Animation stay in Place")).pop();
      let p = label;
      for (let i = 0; i < 5 && p; i++) {
        p = p.parentElement;
        const sw = p && p.querySelector("[role=switch]");
        if (sw) return sw;
      }
      return null;
    },
    async setStayInPlace(on = true) {
      const sw = TS.staySwitch();
      if (!sw) throw new Error("TS.setStayInPlace: select the animations first");
      if ((sw.getAttribute("aria-checked") === "true") !== on) {
        sw.click();
        await wait(600);
      }
      return sw.getAttribute("aria-checked") === "true";
    },
    exportState() {
      const m = document.body.innerText.match(/(\d+)\/(\d+)\s*\n?\s*Select All/);
      const sw = TS.staySwitch();
      return {
        selected: m ? Number(m[1]) : null,
        listed: m ? Number(m[2]) : null,
        stayInPlace: sw ? sw.getAttribute("aria-checked") === "true" : null,
        exporting: /Exporting/.test(document.body.innerText),
      };
    },
    // Starts the export. A rigged export is built on Tripo's server in one to
    // two minutes and arrives in the browser's download folder as
    // tripo_convert_<id>.glb. Move and rename it into the job's inbox.
    async startExport() {
      const st = TS.exportState();
      if (st.selected !== null && (st.selected === 0 || st.stayInPlace !== true)) {
        throw new Error("TS.startExport: " + JSON.stringify(st));
      }
      const b = [...document.querySelectorAll("button")].filter((x) => text(x) === "Export").pop();
      b.click();
      await wait(3000);
      return TS.exportState();
    },
  });
  window.TS = TS;
  return "TS " + TS.version + " ready";
})();
