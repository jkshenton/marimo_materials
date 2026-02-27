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

  function numInput(value, min, max) {
    const inp = document.createElement("input");
    inp.type = "number";
    inp.className = "cb-input";
    inp.value = value;
    if (min !== undefined) inp.min = String(min);
    if (max !== undefined) inp.max = String(max);
    return inp;
  }

  // ── DOM ──────────────────────────────────────────────────────────────────
  const root = document.createElement("div");
  root.className = "cb-root";

  const title = document.createElement("div");
  title.className = "cb-title";
  title.textContent = "Nanoparticle Builder";
  root.appendChild(title);

  const topGrid = document.createElement("div");
  topGrid.className = "cb-grid";

  // Symbol
  const symbolField = field("Symbol");
  const symbolInput = document.createElement("input");
  symbolInput.type = "text";
  symbolInput.className = "cb-input";
  symbolInput.value = model.get("symbol");
  symbolInput.placeholder = "e.g. Au";
  symbolField.appendChild(symbolInput);
  topGrid.appendChild(symbolField);

  // Shape
  const shapeField = field("Shape");
  const shapeSelect = document.createElement("select");
  shapeSelect.className = "cb-select";
  ["Icosahedron", "Decahedron", "Octahedron"].forEach(s => {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    if (s === model.get("shape")) opt.selected = true;
    shapeSelect.appendChild(opt);
  });
  shapeField.appendChild(shapeSelect);
  topGrid.appendChild(shapeField);

  root.appendChild(topGrid);

  // Shape-specific parameters grid (rebuilt on shape change)
  const paramsGrid = document.createElement("div");
  paramsGrid.className = "cb-grid";
  root.appendChild(paramsGrid);

  // Icosahedron inputs
  const icoField = field("# Shells");
  const icoInput = numInput(model.get("noshells"), 1, 20);
  icoField.appendChild(icoInput);

  // Decahedron inputs
  const decaPField = field("p");
  const decaPInput = numInput(model.get("p"), 1, 20);
  const decaPNote = document.createElement("small");
  decaPNote.style.fontSize = "10px";
  decaPNote.style.color = "#aaa";
  decaPNote.textContent = "vertices on axis";
  decaPField.appendChild(decaPInput);
  decaPField.appendChild(decaPNote);

  const decaQField = field("q");
  const decaQInput = numInput(model.get("q"), 1, 20);
  const decaQNote = document.createElement("small");
  decaQNote.style.fontSize = "10px";
  decaQNote.style.color = "#aaa";
  decaQNote.textContent = "layers on face";
  decaQField.appendChild(decaQInput);
  decaQField.appendChild(decaQNote);

  const decaRField = field("r (twin)");
  const decaRInput = numInput(model.get("r"), 0, 10);
  decaRField.appendChild(decaRInput);

  // Octahedron inputs
  const octLenField = field("Length");
  const octLenInput = numInput(model.get("oct_length"), 2, 20);
  octLenField.appendChild(octLenInput);

  const octCutField = field("Cutoff");
  const octCutInput = numInput(model.get("cutoff"), 0, 10);
  const octCutNote = document.createElement("small");
  octCutNote.style.fontSize = "10px";
  octCutNote.style.color = "#aaa";
  octCutNote.textContent = "corner removal";
  octCutField.appendChild(octCutInput);
  octCutField.appendChild(octCutNote);

  // Lattice constant (optional, shared by all shapes)
  const lcGrid = document.createElement("div");
  lcGrid.className = "cb-grid";
  const lcField = field("a (\u00c5)");
  const lcInput = document.createElement("input");
  lcInput.type = "number";
  lcInput.className = "cb-input";
  lcInput.placeholder = "auto";
  lcInput.step = "0.001";
  lcInput.min = "0";
  const lcVal = model.get("latticeconstant");
  lcInput.value = lcVal > 0 ? lcVal : "";
  lcField.appendChild(lcInput);
  const lcNote = document.createElement("small");
  lcNote.style.fontSize = "10px";
  lcNote.style.color = "#aaa";
  lcNote.textContent = "leave blank for ASE default";
  lcField.appendChild(lcNote);
  lcGrid.appendChild(lcField);
  root.appendChild(lcGrid);

  // Status bar
  const status = document.createElement("div");
  status.className = "cb-status";
  root.appendChild(status);

  el.appendChild(root);

  // ── show/hide shape params ────────────────────────────────────────────────
  function updateParams() {
    paramsGrid.innerHTML = "";
    const shape = shapeSelect.value;
    if (shape === "Icosahedron") {
      paramsGrid.appendChild(icoField);
    } else if (shape === "Decahedron") {
      paramsGrid.appendChild(decaPField);
      paramsGrid.appendChild(decaQField);
      paramsGrid.appendChild(decaRField);
    } else {
      // Octahedron
      paramsGrid.appendChild(octLenField);
      paramsGrid.appendChild(octCutField);
    }
  }

  // ── sync to model ─────────────────────────────────────────────────────────
  function sync() {
    model.set("symbol", symbolInput.value.trim() || "Au");
    model.set("shape", shapeSelect.value);
    model.set("noshells", Math.max(1, parseInt(icoInput.value) || 3));
    model.set("p", Math.max(1, parseInt(decaPInput.value) || 3));
    model.set("q", Math.max(1, parseInt(decaQInput.value) || 2));
    model.set("r", Math.max(0, parseInt(decaRInput.value) || 0));
    model.set("oct_length", Math.max(2, parseInt(octLenInput.value) || 3));
    model.set("cutoff", Math.max(0, parseInt(octCutInput.value) || 0));
    const lc = parseFloat(lcInput.value);
    model.set("latticeconstant", (isFinite(lc) && lc > 0) ? lc : 0.0);
    model.save_changes();
  }

  shapeSelect.addEventListener("change", () => { updateParams(); sync(); });
  [icoInput, decaPInput, decaQInput, decaRInput, octLenInput, octCutInput, lcInput]
    .forEach(inp => inp.addEventListener("change", sync));

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
  updateParams();
  updateStatus();
}

export default { render };
