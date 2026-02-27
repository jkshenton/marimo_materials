function render({ model, el }) {
  // ── helpers ──────────────────────────────────────────────────────────────
  function field(labelText) {
    const div = document.createElement("div");
    div.className = "cb-field";
    const lbl = document.createElement("span");
    lbl.className = "cb-label";
    lbl.textContent = labelText;
    div.appendChild(lbl);
    return div;
  }

  // ── DOM ──────────────────────────────────────────────────────────────────
  const root = document.createElement("div");
  root.className = "cb-root";

  const title = document.createElement("div");
  title.className = "cb-title";
  title.textContent = "Bulk Structure Builder";
  root.appendChild(title);

  const grid = document.createElement("div");
  grid.className = "cb-grid";

  // Symbol
  const symbolField = field("Symbol");
  const symbolInput = document.createElement("input");
  symbolInput.type = "text";
  symbolInput.className = "cb-input";
  symbolInput.value = model.get("symbol");
  symbolInput.placeholder = "e.g. Cu";
  symbolField.appendChild(symbolInput);
  grid.appendChild(symbolField);

  // Crystal structure
  const STRUCTURES = ["", "fcc", "bcc", "hcp", "diamond", "zincblende",
                      "rocksalt", "cesiumchloride", "fluorite", "wurtzite"];
  const STRUCT_LABELS = ["Auto", "FCC", "BCC", "HCP", "Diamond",
                         "Zincblende", "Rocksalt", "CsCl", "Fluorite", "Wurtzite"];
  const structField = field("Structure");
  const structSelect = document.createElement("select");
  structSelect.className = "cb-select";
  STRUCTURES.forEach((v, i) => {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = STRUCT_LABELS[i];
    if (v === model.get("crystalstructure")) opt.selected = true;
    structSelect.appendChild(opt);
  });
  structField.appendChild(structSelect);
  grid.appendChild(structField);

  // Supercell a×b×c
  const scField = field("Supercell a×b×c");
  const scRow = document.createElement("div");
  scRow.className = "cb-row";
  const supercell = model.get("supercell");
  const scInputs = supercell.map(v => {
    const inp = document.createElement("input");
    inp.type = "number";
    inp.className = "cb-input cb-input--sm";
    inp.min = "1";
    inp.max = "20";
    inp.value = v;
    scRow.appendChild(inp);
    return inp;
  });
  scField.appendChild(scRow);
  grid.appendChild(scField);

  root.appendChild(grid);

  // ── Lattice constants (optional) ──────────────────────────────────────────
  const lcTitle = document.createElement("div");
  lcTitle.className = "cb-label";
  lcTitle.style.marginBottom = "6px";
  lcTitle.textContent = "Lattice constants (Å) — leave blank for ASE default";
  root.appendChild(lcTitle);

  const lcGrid = document.createElement("div");
  lcGrid.className = "cb-grid";

  function optFloat(traitName, label, placeholder) {
    const f = field(label);
    const inp = document.createElement("input");
    inp.type = "number";
    inp.className = "cb-input";
    inp.placeholder = placeholder || "auto";
    inp.step = "0.001";
    inp.min = "0";
    const v = model.get(traitName);
    inp.value = v > 0 ? v : "";
    f.appendChild(inp);
    return { field: f, inp };
  }

  const { field: aField, inp: aInput } = optFloat("a", "a (Å)");
  const { field: bField, inp: bInput } = optFloat("b", "b (Å)");
  const { field: cField, inp: cInput } = optFloat("c", "c (Å)");
  const { field: coveraField, inp: coveraInput } = optFloat("covera", "c/a");
  lcGrid.appendChild(aField);
  lcGrid.appendChild(bField);
  lcGrid.appendChild(cField);
  lcGrid.appendChild(coveraField);
  root.appendChild(lcGrid);

  // Which lattice inputs are meaningful for each structure.
  // b is only used by orthorhombic cells which we don't expose, so it stays
  // disabled for all named structures. Auto ("") enables everything.
  const LC_ACTIVE = {
    "": ["a", "b", "c", "covera"],
    "fcc": ["a"],
    "bcc": ["a"],
    "hcp": ["a", "c", "covera"],
    "diamond": ["a"],
    "zincblende": ["a"],
    "rocksalt": ["a"],
    "cesiumchloride": ["a"],
    "fluorite": ["a"],
    "wurtzite": ["a", "c", "covera"],
  };
  const lcInputMap = { a: aInput, b: bInput, c: cInput, covera: coveraInput };

  function updateLatticeFields() {
    const active = new Set(LC_ACTIVE[structSelect.value] || ["a"]);
    for (const [name, inp] of Object.entries(lcInputMap)) {
      const enabled = active.has(name);
      inp.disabled = !enabled;
      if (!enabled) inp.value = "";
    }
  }

  // Cubic checkbox
  const cubicRow = document.createElement("div");
  cubicRow.className = "cb-checkbox-row";
  const cubicId = "cb-cubic-" + Math.random().toString(36).slice(2);
  const cubicCb = document.createElement("input");
  cubicCb.type = "checkbox";
  cubicCb.id = cubicId;
  cubicCb.checked = model.get("cubic");
  const cubicLbl = document.createElement("label");
  cubicLbl.htmlFor = cubicId;
  cubicLbl.textContent = "Cubic unit cell";
  cubicRow.appendChild(cubicCb);
  cubicRow.appendChild(cubicLbl);
  root.appendChild(cubicRow);

  // Status bar
  const status = document.createElement("div");
  status.className = "cb-status";
  root.appendChild(status);

  el.appendChild(root);

  // ── sync to model ─────────────────────────────────────────────────────────
  function parseOptFloat(inp) {
    const v = parseFloat(inp.value);
    return (isFinite(v) && v > 0) ? v : 0.0;
  }

  function sync() {
    model.set("symbol", symbolInput.value.trim() || "Cu");
    model.set("crystalstructure", structSelect.value);
    model.set("supercell", scInputs.map(i => Math.max(1, parseInt(i.value) || 1)));
    model.set("cubic", cubicCb.checked);
    model.set("a", parseOptFloat(aInput));
    model.set("b", parseOptFloat(bInput));
    model.set("c", parseOptFloat(cInput));
    model.set("covera", parseOptFloat(coveraInput));
    model.save_changes();
  }

  // structSelect handled separately below (needs updateLatticeFields first)
  cubicCb.addEventListener("change", sync);
  scInputs.forEach(inp => inp.addEventListener("change", sync));
  [aInput, bInput, cInput, coveraInput].forEach(inp => inp.addEventListener("change", sync));

  structSelect.addEventListener("change", () => { updateLatticeFields(); sync(); });

  let debounceTimer;
  symbolInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(sync, 400);
  });

  // ── status updates from Python ────────────────────────────────────────────
  function updateStatus() {
    const err = model.get("error");
    const n = model.get("n_atoms");
    if (err) {
      status.textContent = "\u26a0\ufe0e " + err;
      status.className = "cb-status cb-status--visible cb-status--error";
    } else if (n > 0) {
      status.textContent = "\u2713 Built " + n + " atoms";
      status.className = "cb-status cb-status--visible cb-status--ok";
    } else {
      status.className = "cb-status";
    }
  }

  model.on("change", updateStatus);
  updateLatticeFields();
  updateStatus();
}

export default { render };
