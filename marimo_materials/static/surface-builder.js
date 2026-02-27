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

  function numInput(value, min, max, step) {
    const inp = document.createElement("input");
    inp.type = "number";
    inp.className = "cb-input";
    inp.value = value;
    if (min !== undefined) inp.min = min;
    if (max !== undefined) inp.max = max;
    if (step !== undefined) inp.step = step;
    return inp;
  }

  // ── DOM ──────────────────────────────────────────────────────────────────
  const root = document.createElement("div");
  root.className = "cb-root";

  const title = document.createElement("div");
  title.className = "cb-title";
  title.textContent = "Surface Slab Builder";
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

  // Facet
  const FACETS = ["fcc111", "fcc100", "fcc110", "fcc211",
                  "bcc100", "bcc110", "bcc111",
                  "hcp0001", "hcp10m10"];
  const facetField = field("Facet");
  const facetSelect = document.createElement("select");
  facetSelect.className = "cb-select";
  FACETS.forEach(f => {
    const opt = document.createElement("option");
    opt.value = f;
    opt.textContent = f;
    if (f === model.get("facet")) opt.selected = true;
    facetSelect.appendChild(opt);
  });
  facetField.appendChild(facetSelect);
  grid.appendChild(facetField);

  // Layers
  const layersField = field("Layers");
  const layersInput = numInput(model.get("layers"), 1, 30, 1);
  layersField.appendChild(layersInput);
  grid.appendChild(layersField);

  // Vacuum
  const vacuumField = field("Vacuum (Å)");
  const vacuumInput = numInput(model.get("vacuum"), 0, 60, 0.5);
  vacuumField.appendChild(vacuumInput);
  grid.appendChild(vacuumField);

  // Supercell a
  const scaField = field("Super a");
  const scaInput = numInput(model.get("supercell_a"), 1, 10, 1);
  scaField.appendChild(scaInput);
  grid.appendChild(scaField);

  // Supercell b
  const scbField = field("Super b");
  const scbInput = numInput(model.get("supercell_b"), 1, 10, 1);
  scbField.appendChild(scbInput);
  grid.appendChild(scbField);

  root.appendChild(grid);

  // ── Lattice constants (optional) ─────────────────────────────────────────
  const lcTitle = document.createElement("div");
  lcTitle.className = "cb-label";
  lcTitle.style.marginBottom = "6px";
  lcTitle.textContent = "Lattice constants (Å) — leave blank for ASE default";
  root.appendChild(lcTitle);

  const lcGrid = document.createElement("div");
  lcGrid.className = "cb-grid";

  function optFloat(traitName, label) {
    const f = field(label);
    const inp = document.createElement("input");
    inp.type = "number";
    inp.className = "cb-input";
    inp.placeholder = "auto";
    inp.step = "0.001";
    inp.min = "0";
    const v = model.get(traitName);
    inp.value = v > 0 ? v : "";
    f.appendChild(inp);
    return { field: f, inp };
  }

  const { field: aField, inp: aInput } = optFloat("a", "a (Å)");
  const { field: cField, inp: cInput } = optFloat("c", "c (Å)");
  lcGrid.appendChild(aField);
  lcGrid.appendChild(cField);
  root.appendChild(lcGrid);

  // c only makes sense for HCP facets
  const HCP_FACETS = new Set(["hcp0001", "hcp10m10"]);

  function updateLatticeFields() {
    const isHcp = HCP_FACETS.has(facetSelect.value);
    cInput.disabled = !isHcp;
    if (!isHcp) cInput.value = "";
  }

  // Orthogonal checkbox
  const orthoRow = document.createElement("div");
  orthoRow.className = "cb-checkbox-row";
  const orthoId = "cb-ortho-" + Math.random().toString(36).slice(2);
  const orthoCb = document.createElement("input");
  orthoCb.type = "checkbox";
  orthoCb.id = orthoId;
  orthoCb.checked = model.get("orthogonal");
  const orthoLbl = document.createElement("label");
  orthoLbl.htmlFor = orthoId;
  orthoLbl.textContent = "Orthogonal cell";
  orthoRow.appendChild(orthoCb);
  orthoRow.appendChild(orthoLbl);
  root.appendChild(orthoRow);

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
    model.set("facet", facetSelect.value);
    model.set("layers", Math.max(1, parseInt(layersInput.value) || 4));
    model.set("vacuum", Math.max(0, parseFloat(vacuumInput.value) || 10.0));
    model.set("supercell_a", Math.max(1, parseInt(scaInput.value) || 1));
    model.set("supercell_b", Math.max(1, parseInt(scbInput.value) || 1));
    model.set("orthogonal", orthoCb.checked);
    model.set("a", parseOptFloat(aInput));
    model.set("c", parseOptFloat(cInput));
    model.save_changes();
  }

  // facetSelect handled separately – needs updateLatticeFields first
  [orthoCb, layersInput, vacuumInput, scaInput, scbInput, aInput, cInput]
    .forEach(e => e.addEventListener("change", sync));
  facetSelect.addEventListener("change", () => { updateLatticeFields(); sync(); });

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
