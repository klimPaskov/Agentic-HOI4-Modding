// Tripo Agentic Canvas helpers. Paste into the page with the browser tool's
// script runner once per page load. It defines window.CV.
//
// Recorded on studio.tripo3d.ai/canvas on 2026-11-14 and run as written for:
// applying a free preset on a selected Animation node and waiting for it
// (CV.search, CV.tile, CV.start, CV.waitIdle, CV.fire). CV.dialog and
// CV.checkExport were tidied after that run and still need one run as
// written. Clicks that open dialogs (a node's Export
// chip, the animation count, Select All, the dialog's Export button) need a
// real pointer click on a freshly looked-up element reference, because the
// page re-renders and old references die. Never click by fixed coordinates:
// the browser frame changes width between calls.
//
// Run as written end to end on 2026-11-22 (an armed humanoid, nine clips) for:
// CV.stubPicker, CV.applyIn, CV.exportPrep and CV.exportClick.
//
// Facts this file relies on:
// - A canvas Animation node holds ONE clip. Give each candidate its own
//   Animation node from the same Rigging node (hover the Rigging result, then
//   its "Animation" chip): the nodes generate in parallel. Each node's panel
//   has its own Library search box, so act in the newest panel (CV.applyIn).
// - Ticking a preset tile applies it at once and is free.
// - The Animation node's Generate tab is text to motion (20 credits, up to
//   5 s) and has a "Multi-stage Motion" option.
// - The "Upload" menu item and an empty node's picture box open the system
//   file picker, which an agent cannot drive. Call CV.stubPicker() first: the
//   page then only marks the input, and the browser tool's file upload feeds
//   the file to that input (the page-level `input[type=file]`).
// - Export from a node's Export chip (it shows while the node is selected
//   and hovered). The dialog starts with "Number of Animations 0" and
//   "Animation stay in Place" off: CV.exportPrep() selects the clip and
//   switches both switches on, CV.exportClick() exports.
// - Chrome starts one download per page load. Reload the canvas page before
//   each further export.
// - The tile label and the exported clip name can differ (tile "defeat"
//   exports "defeat_02", tile "defeat_02" exports "defeat_03"). Always check
//   the clip name in the downloaded file. tripo/join_clips.py joins the files.
// - The Canvas Agent cannot see an Upload node's picture. Do not ask it to
//   plan or to classify: the kit's tripo/pick_preset.py picks the type.
(() => {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const visible = (e) => e.offsetParent !== null;
  const CV = { version: "2026-11-22" };

  // Dispatch a full pointer sequence at a page point.
  CV.fire = (x, y) => {
    const el = document.elementFromPoint(x, y);
    if (!el) return null;
    for (const t of ["pointerdown", "mousedown", "pointerup", "mouseup", "click"]) {
      const Ev = t.startsWith("pointer") ? PointerEvent : MouseEvent;
      el.dispatchEvent(new Ev(t, {
        bubbles: true, cancelable: true, clientX: x, clientY: y, button: 0,
        pointerId: 1, pointerType: "mouse", isPrimary: true, view: window,
      }));
    }
    return el;
  };

  // Visible elements whose own text is exactly t.
  CV.leafs = (t) => [...document.querySelectorAll("*")].filter(
    (e) => visible(e) && e.textContent.trim() === t &&
      ![...e.children].some((c) => c.textContent.trim() === t));

  // Type a preset name into the Library search box of the selected node.
  CV.search = (name) => {
    const box = [...document.querySelectorAll("input")].find(
      (e) => e.placeholder === "Search" && visible(e));
    if (!box) throw new Error("CV.search: no Library search box. Select the Animation node and open Library.");
    const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
    set.call(box, name);
    box.dispatchEvent(new Event("input", { bubbles: true }));
  };

  // The tick mark of the tile whose label is exactly name.
  CV.tile = (name) => {
    const labels = CV.leafs(name).filter((e) => e.children.length === 0);
    if (labels.length !== 1) throw new Error("CV.tile: " + labels.length + " tiles labelled " + name);
    let card = labels[0];
    let tick = null;
    for (let k = 0; k < 6 && !tick; k++) {
      card = card.parentElement;
      tick = card.querySelector('[class*="check-circle"]');
    }
    if (!tick) throw new Error("CV.tile: no tick on tile " + name);
    tick.scrollIntoView({ block: "center" });
    const r = tick.getBoundingClientRect();
    return { x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) };
  };

  CV.busy = () => [...document.querySelectorAll("*")].some(
    (e) => e.children.length === 0 && visible(e) && /^Generating/.test(e.textContent.trim()));

  // Wait until no node shows "Generating". Keep max under the script runner's
  // own time limit (45 s seen) and call again while busy stays true.
  CV.waitIdle = async (max = 38) => {
    let n = 0;
    while (CV.busy() && n < max) { await wait(1000); n++; }
    return { busy: CV.busy(), seconds: n };
  };

  // Apply one preset on the selected Animation node. One preset per call, and
  // wait for idle before the next: quick ticks queue long rebuilds.
  CV.start = async (name) => {
    if (CV.busy()) throw new Error("CV.start: a node is still generating");
    CV.search(name);
    await wait(1500);
    const p = CV.tile(name);
    CV.fire(p.x, p.y);
    await wait(2500);
    return { preset: name, started: CV.busy() };
  };

  // State of the open export dialog. selected is "1/1" once Select All is on.
  CV.dialog = () => {
    const count = (document.body.innerText.match(/\n(\d+\/\d+)\n/) || [])[1] || null;
    const switches = [...document.querySelectorAll("[role=switch]")].filter(visible)
      .map((e) => e.getAttribute("aria-checked") === "true");
    const picked = [...document.querySelectorAll('[role="dialog"]')]
      .filter((d) => /Choose Animations/.test(d.innerText))
      .map((d) => d.innerText.split("\n").filter((s) => /^[a-z0-9_]+$/.test(s.trim())))
      .flat();
    return {
      open: CV.leafs("Number of Animations").length > 0 || CV.leafs("File Name").length > 0,
      selected: count,
      clipNames: [...new Set(picked)],
      // order in the dialog: Export Skeleton, then Animation stay in Place
      exportSkeleton: switches.length ? switches[0] : null,
      stayInPlace: switches.length > 1 ? switches[1] : null,
      converting: /Converting/.test(document.body.innerText),
    };
  };

  // Refuse to go on unless exactly one clip, the wanted one, is selected with
  // skeleton and stay-in-place on. Call right before the real click on Export.
  CV.checkExport = (name) => {
    const d = CV.dialog();
    const ok = d.selected === "1/1" && d.exportSkeleton === true && d.stayInPlace === true &&
      (d.clipNames.length === 0 || d.clipNames.includes(name));
    if (!ok) throw new Error("CV.checkExport: " + JSON.stringify(d));
    return d;
  };

  // Stop file inputs from opening the system picker: a click only marks the
  // input (data-picker="1"), and the browser tool's file upload fills it.
  CV.stubPicker = () => {
    if (!window.__cvOrigClick) {
      window.__cvOrigClick = HTMLInputElement.prototype.click;
      HTMLInputElement.prototype.click = function () {
        if (this.type === "file") { this.setAttribute("data-picker", "1"); return; }
        return window.__cvOrigClick.call(this);
      };
    }
    return "file picker stubbed";
  };

  // Tick one preset in the Library of a node's own panel. fromEnd 0 is the
  // newest panel with an empty search box (a freshly added Animation node).
  CV.applyIn = async (name) => {
    const boxes = [...document.querySelectorAll("input")].filter(
      (e) => e.placeholder === "Search" && visible(e));
    const box = [...boxes].reverse().find((b) => b.value === "");
    if (!box) throw new Error("CV.applyIn: no empty Library search box. Open the new node's Library tab.");
    let panel = box;
    for (let k = 0; k < 8; k++) {
      panel = panel.parentElement;
      if (panel.querySelectorAll('[class*="check-circle"]').length && panel.innerText.includes("Library")) break;
    }
    const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
    set.call(box, name);
    box.dispatchEvent(new Event("input", { bubbles: true }));
    await wait(2000);
    const labels = [...panel.querySelectorAll("*")].filter(
      (e) => e.children.length === 0 && e.textContent.trim() === name && visible(e));
    if (labels.length !== 1) throw new Error("CV.applyIn: " + labels.length + " tiles labelled " + name);
    let card = labels[0];
    let tick = null;
    for (let k = 0; k < 6 && !tick; k++) { card = card.parentElement; tick = card.querySelector('[class*="check-circle"]'); }
    tick.scrollIntoView({ block: "center" });
    const r = tick.getBoundingClientRect();
    CV.fire(r.left + r.width / 2, r.top + r.height / 2);
    await wait(2500);
    return name + " ticked";
  };

  // In the open Export dialog: pick the node's clip, switch Export Skeleton
  // and Animation stay in Place on, and refuse unless exactly one clip is set.
  CV.exportPrep = async () => {
    await wait(2500);
    const dlg = [...document.querySelectorAll('[role="dialog"]')].find((d) => d.innerText.includes("Number of Animations"));
    if (!dlg) throw new Error("CV.exportPrep: no Export dialog");
    if (!CV.leafs("Choose Animations").length) {
      const row = [...dlg.querySelectorAll("*")].find((e) => e.children.length === 0 && e.textContent.trim() === "Number of Animations");
      const r = row.parentElement.getBoundingClientRect();
      CV.fire(r.right - 20, r.top + r.height / 2);
      await wait(2500);
    }
    const all = CV.leafs("Select All")[0];
    const sr = all.getBoundingClientRect();
    CV.fire(sr.left + sr.width / 2, sr.top + sr.height / 2);
    await wait(800);
    for (const s of dlg.querySelectorAll("[role=switch]")) {
      if (s.getAttribute("aria-checked") !== "true") { s.click(); await wait(600); }
    }
    const d = CV.dialog();
    const switches = [...dlg.querySelectorAll("[role=switch]")].map((s) => s.getAttribute("aria-checked") === "true");
    if (d.selected !== "1/1" || switches.length < 2 || switches.some((s) => !s)) throw new Error("CV.exportPrep: " + JSON.stringify(d));
    return d;
  };

  CV.exportClick = () => {
    const dlg = [...document.querySelectorAll('[role="dialog"]')].find((d) => d.innerText.includes("Number of Animations"));
    [...dlg.querySelectorAll("button")].find((b) => b.innerText.trim() === "Export").click();
    return "export started";
  };

  window.CV = CV;
  return "CV " + CV.version + " ready";
})();
