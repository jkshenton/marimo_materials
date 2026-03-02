function render({ model, el }) {

  // ── helpers ────────────────────────────────────────────────────────────────

  function field(labelText, cls) {
    const div = document.createElement("div");
    div.className = "ce-field" + (cls ? " " + cls : "");
    const lbl = document.createElement("span");
    lbl.className = "ce-label";
    lbl.textContent = labelText;
    div.appendChild(lbl);
    return div;
  }

  function numInput(val, step, min, width) {
    const inp = document.createElement("input");
    inp.type = "number";
    inp.className = "ce-input";
    inp.value = val ?? "";
    inp.step = step ?? "any";
    if (min !== undefined) inp.min = min;
    if (width) inp.style.width = width;
    return inp;
  }

  function textInput(val, placeholder, width) {
    const inp = document.createElement("input");
    inp.type = "text";
    inp.className = "ce-input";
    inp.value = val ?? "";
    if (placeholder) inp.placeholder = placeholder;
    if (width) inp.style.width = width;
    return inp;
  }

  function btn(label, cls) {
    const b = document.createElement("button");
    b.className = "ce-btn" + (cls ? " " + cls : "");
    b.textContent = label;
    return b;
  }

  function sectionTitle(text) {
    const div = document.createElement("div");
    div.className = "ce-section-title";
    div.textContent = text;
    return div;
  }

  function round(v, d) { return Math.round(v * 10 ** d) / 10 ** d; }

  // ── parse model state ──────────────────────────────────────────────────────

  function getAtoms() {
    const raw = model.get("atoms_json");
    if (!raw) return null;
    try { return JSON.parse(raw); } catch { return null; }
  }

  // ── root element ──────────────────────────────────────────────────────────

  const root = document.createElement("div");
  root.className = "ce-root";
  el.appendChild(root);

  // error banner
  const errorBox = document.createElement("div");
  errorBox.className = "ce-error";
  errorBox.hidden = true;
  root.appendChild(errorBox);

  // ── section 1: cell ────────────────────────────────────────────────────────

  root.appendChild(sectionTitle("Unit Cell"));

  // Cellpar / Matrix toggle
  let cellMode = "cellpar";
  const cellModeToggle = document.createElement("div");
  cellModeToggle.className = "ce-coords-toggle";
  const cellparBtn = document.createElement("button");
  cellparBtn.className = "ce-toggle-btn active";
  cellparBtn.textContent = "a, b, c, α, β, γ";
  const matrixBtn = document.createElement("button");
  matrixBtn.className = "ce-toggle-btn";
  matrixBtn.textContent = "3×3 matrix";
  cellModeToggle.append(cellparBtn, matrixBtn);
  root.appendChild(cellModeToggle);

  // ── cellpar inputs ─────────────────────────────────────────────────────────
  const cellGrid = document.createElement("div");
  cellGrid.className = "ce-grid";
  root.appendChild(cellGrid);

  // a, b, c
  const aF = field("a (Å)"); const aIn = numInput(0, "0.001", "0"); aF.appendChild(aIn); cellGrid.appendChild(aF);
  const bF = field("b (Å)"); const bIn = numInput(0, "0.001", "0"); bF.appendChild(bIn); cellGrid.appendChild(bF);
  const cF = field("c (Å)"); const cIn = numInput(0, "0.001", "0"); cF.appendChild(cIn); cellGrid.appendChild(cF);
  // α, β, γ
  const alF = field("α (°)"); const alIn = numInput(90, "0.01", "0"); alF.appendChild(alIn); cellGrid.appendChild(alF);
  const beF = field("β (°)"); const beIn = numInput(90, "0.01", "0"); beF.appendChild(beIn); cellGrid.appendChild(beF);
  const gaF = field("γ (°)"); const gaIn = numInput(90, "0.01", "0"); gaF.appendChild(gaIn); cellGrid.appendChild(gaF);

  // ── 3×3 matrix inputs ─────────────────────────────────────────────────────
  const matrixGrid = document.createElement("div");
  matrixGrid.className = "ce-matrix-grid";
  matrixGrid.hidden = true;
  root.appendChild(matrixGrid);

  // Header row: blank + x, y, z
  [["ce-matrix-corner", ""], ["ce-matrix-head", "x"], ["ce-matrix-head", "y"], ["ce-matrix-head", "z"]].forEach(([cls, t]) => {
    const th = document.createElement("span"); th.className = cls; th.textContent = t;
    matrixGrid.appendChild(th);
  });

  // 3 rows (a, b, c vectors), 3 inputs each
  const matrixInputs = ["a", "b", "c"].map(rowLabel => {
    const lbl = document.createElement("span");
    lbl.className = "ce-matrix-row-label";
    lbl.textContent = rowLabel;
    matrixGrid.appendChild(lbl);
    return [0, 1, 2].map(() => {
      const inp = numInput(0, "0.0001", undefined, "100%");
      matrixGrid.appendChild(inp);
      return inp;
    });
  });

  cellparBtn.addEventListener("click", () => {
    if (cellMode === "cellpar") return;
    cellMode = "cellpar";
    cellparBtn.classList.add("active"); matrixBtn.classList.remove("active");
    cellGrid.hidden = false; matrixGrid.hidden = true;
  });
  matrixBtn.addEventListener("click", () => {
    if (cellMode === "matrix") return;
    cellMode = "matrix";
    matrixBtn.classList.add("active"); cellparBtn.classList.remove("active");
    matrixGrid.hidden = false; cellGrid.hidden = true;
  });

  // PBC checkboxes
  const pbcRow = document.createElement("div");
  pbcRow.className = "ce-pbc-row";
  const pbcLabel = document.createElement("span");
  pbcLabel.className = "ce-label";
  pbcLabel.textContent = "PBC";
  pbcRow.appendChild(pbcLabel);
  const pbcChecks = ["x", "y", "z"].map((ax, i) => {
    const lbl = document.createElement("label");
    lbl.className = "ce-pbc-item";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.className = "ce-checkbox";
    lbl.appendChild(cb);
    lbl.append(" " + ax);
    pbcRow.appendChild(lbl);
    return cb;
  });
  root.appendChild(pbcRow);

  const scaleAtomsRow = document.createElement("div");
  scaleAtomsRow.className = "ce-pbc-row";
  const scaleAtomsCb = document.createElement("input");
  scaleAtomsCb.type = "checkbox";
  scaleAtomsCb.className = "ce-checkbox";
  const scaleAtomsLbl = document.createElement("label");
  scaleAtomsLbl.className = "ce-pbc-item";
  scaleAtomsLbl.appendChild(scaleAtomsCb);
  scaleAtomsLbl.append(" Scale atoms with cell");
  scaleAtomsRow.appendChild(scaleAtomsLbl);
  root.appendChild(scaleAtomsRow);

  const setCellBtn = btn("Set cell", "ce-btn--primary ce-btn--full");
  setCellBtn.style.marginTop = "4px";
  setCellBtn.addEventListener("click", () => {
    const pbc = pbcChecks.map(c => c.checked);
    const scale_atoms = scaleAtomsCb.checked;
    if (cellMode === "matrix") {
      sendOp("set_cell", {
        cell_matrix: matrixInputs.map(row => row.map(inp => parseFloat(inp.value) || 0)),
        pbc,
        scale_atoms,
      });
    } else {
      sendOp("set_cell", {
        cellpar: [parseFloat(aIn.value), parseFloat(bIn.value), parseFloat(cIn.value),
                  parseFloat(alIn.value), parseFloat(beIn.value), parseFloat(gaIn.value)],
        pbc,
        scale_atoms,
      });
    }
  });
  root.appendChild(setCellBtn);

  function updateCellInputs(atoms) {
    if (!atoms) return;
    const [a, b, c, al, be, ga] = atoms.cellpar;
    aIn.value  = round(a,  6);
    bIn.value  = round(b,  6);
    cIn.value  = round(c,  6);
    alIn.value = round(al, 4);
    beIn.value = round(be, 4);
    gaIn.value = round(ga, 4);
    atoms.pbc.forEach((v, i) => { pbcChecks[i].checked = v; });
    if (atoms.cell) {
      matrixInputs.forEach((row, i) => row.forEach((inp, j) => {
        inp.value = round(atoms.cell[i][j], 8);
      }));
    }
  }

  // ── section 2: sites ───────────────────────────────────────────────────────

  // coord mode state: "cartesian" | "fractional"
  let coordMode = "cartesian";

  root.appendChild(sectionTitle("Sites"));

  // Cartesian / Fractional toggle
  const coordToggle = document.createElement("div");
  coordToggle.className = "ce-coords-toggle";
  const cartBtn = document.createElement("button");
  cartBtn.className = "ce-toggle-btn active";
  cartBtn.textContent = "Cartesian (Å)";
  const fracBtn = document.createElement("button");
  fracBtn.className = "ce-toggle-btn";
  fracBtn.textContent = "Fractional";
  coordToggle.append(cartBtn, fracBtn);
  root.appendChild(coordToggle);

  const tableWrap = document.createElement("div");
  tableWrap.className = "ce-table-wrap";
  root.appendChild(tableWrap);

  const table = document.createElement("table");
  table.className = "ce-table";
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  ["#", "Symbol", "x", "y", "z", ""].forEach(t => {
    const th = document.createElement("th");
    th.textContent = t;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);
  const [, , thX, thY, thZ] = headerRow.children;
  const tbody = document.createElement("tbody");
  table.appendChild(tbody);
  tableWrap.appendChild(table);

  function updateHeaders() {
    const suffix = coordMode === "fractional" ? "" : " (Å)";
    thX.textContent = "x" + suffix;
    thY.textContent = "y" + suffix;
    thZ.textContent = "z" + suffix;
  }
  updateHeaders();

  cartBtn.addEventListener("click", () => {
    if (coordMode === "cartesian") return;
    coordMode = "cartesian";
    cartBtn.classList.add("active");
    fracBtn.classList.remove("active");
    updateHeaders();
    syncFromModel();
  });
  fracBtn.addEventListener("click", () => {
    if (coordMode === "fractional") return;
    coordMode = "fractional";
    fracBtn.classList.add("active");
    cartBtn.classList.remove("active");
    updateHeaders();
    syncFromModel();
  });

  function buildTableRows(atoms) {
    tbody.innerHTML = "";
    if (!atoms) return;
    atoms.symbols.forEach((sym, i) => {
      const tr = document.createElement("tr");
      const coords = coordMode === "fractional"
        ? atoms.scaled_positions[i]
        : atoms.positions[i];
      const [x, y, z] = coords;

      const tdI  = document.createElement("td");
      tdI.className = "ce-td-idx";
      tdI.textContent = i;

      const tdSym = document.createElement("td");
      const symIn = textInput(sym, "El", "52px");
      symIn.className += " ce-sym";
      tdSym.appendChild(symIn);

      const tdX = document.createElement("td");
      const xIn = numInput(round(x, 6), "0.001", undefined, "90px");
      tdX.appendChild(xIn);

      const tdY = document.createElement("td");
      const yIn = numInput(round(y, 6), "0.001", undefined, "90px");
      tdY.appendChild(yIn);

      const tdZ = document.createElement("td");
      const zIn = numInput(round(z, 6), "0.001", undefined, "90px");
      tdZ.appendChild(zIn);

      const tdDel = document.createElement("td");
      const delBtn = btn("×", "ce-btn--icon");
      delBtn.title = "Delete this site";
      delBtn.addEventListener("click", () => {
        sendOp("delete_atom", { index: i });
      });
      tdDel.appendChild(delBtn);

      tr.append(tdI, tdSym, tdX, tdY, tdZ, tdDel);
      tbody.appendChild(tr);
    });
  }

  // Add-site row
  const addRow = document.createElement("div");
  addRow.className = "ce-add-row";
  const addSymIn  = textInput("", "Symbol", "64px");
  const addXIn    = numInput(0, "0.001", undefined, "80px");
  const addYIn    = numInput(0, "0.001", undefined, "80px");
  const addZIn    = numInput(0, "0.001", undefined, "80px");
  const addBtn    = btn("+ Add site");
  addBtn.addEventListener("click", () => {
    const sym = addSymIn.value.trim();
    if (!sym) return;
    sendOp("add_atom", {
      symbol: sym,
      position: [parseFloat(addXIn.value)||0, parseFloat(addYIn.value)||0, parseFloat(addZIn.value)||0],
      fractional: coordMode === "fractional",
    });
    addSymIn.value = "";
    addXIn.value = addYIn.value = addZIn.value = "0";
  });
  addRow.append(addSymIn, addXIn, addYIn, addZIn, addBtn);
  root.appendChild(addRow);

  // Apply-changes button
  const applyBtn = btn("Apply site edits", "ce-btn--primary ce-btn--full");
  applyBtn.addEventListener("click", () => {
    sendCurrentState();
  });
  root.appendChild(applyBtn);

  // ── section 3: operations ──────────────────────────────────────────────────

  root.appendChild(sectionTitle("Operations"));

  const opsGrid = document.createElement("div");
  opsGrid.className = "ce-ops";
  root.appendChild(opsGrid);

  function opRow(label, controls, runFn) {
    const row = document.createElement("div");
    row.className = "ce-op-row";
    const lbl = document.createElement("span");
    lbl.className = "ce-op-label";
    lbl.textContent = label;
    const inner = document.createElement("div");
    inner.className = "ce-op-controls";
    controls.forEach(c => inner.appendChild(c));
    const runBtn = btn("Run", "ce-btn--run");
    runBtn.addEventListener("click", runFn);
    row.append(lbl, inner, runBtn);
    opsGrid.appendChild(row);
    return row;
  }

  // Wrap PBC
  opRow("Wrap PBC", [], () => sendOp("wrap", {}));

  // Center
  function subLabel(text) {
    const s = document.createElement("span");
    s.className = "ce-sublabel";
    s.textContent = text;
    return s;
  }

  const axSel = document.createElement("select");
  axSel.className = "ce-select";
  axSel.style.width = "56px";
  [["all","All"], ["0","x"], ["1","y"], ["2","z"]].forEach(([v,t]) => {
    const o = document.createElement("option"); o.value = v; o.textContent = t;
    axSel.appendChild(o);
  });

  const vacIn = numInput("", "0.1", "0", "68px");
  vacIn.placeholder = "none";
  vacIn.title = "Add this many Å of vacuum on each side along the selected axis. Leave blank to only shift atoms without changing the cell size.";

  const aboutIn = textInput("", "x,y,z", "90px");
  aboutIn.title = "Centre atoms about this point. Enter a single number (e.g. 0) or three comma-separated values (e.g. 0,0,0). Leave blank to centre about the cell midpoint.";

  opRow("Center", [
    subLabel("Axis:"), axSel,
    subLabel("Add vac (\u00c5/side):"), vacIn,
    subLabel("About:"), aboutIn,
  ], () => {
    const axis = axSel.value === "all" ? [0,1,2] : [parseInt(axSel.value)];
    const vacuum = vacIn.value.trim() !== "" ? parseFloat(vacIn.value) : null;
    const aboutStr = aboutIn.value.trim();
    let about = null;
    if (aboutStr !== "") {
      const parts = aboutStr.split(/[\s,]+/).map(Number).filter(v => !isNaN(v));
      if (parts.length === 1) about = [parts[0], parts[0], parts[0]];
      else if (parts.length === 3) about = parts;
    }
    sendOp("center", { vacuum, axis, about });
  });

  // Repeat
  const repInputs = [1,1,1].map((v, i) => {
    const n = numInput(v, "1", "1", "48px");
    n.title = ["nx","ny","nz"][i];
    return n;
  });
  opRow("Repeat", repInputs, () => {
    sendOp("repeat", { rep: repInputs.map(n => parseInt(n.value)||1) });
  });

  // Translate
  const transInputs = [0,0,0].map((v, i) => {
    const n = numInput(v, "0.1", undefined, "64px");
    n.title = ["tx","ty","tz"][i];
    return n;
  });
  opRow("Translate", transInputs, () => {
    sendOp("translate", { displacement: transInputs.map(n => parseFloat(n.value)||0) });
  });

  // Scale cell
  const scaleIn = numInput(1, "0.01", "0.01", "72px");
  scaleIn.placeholder = "factor";
  opRow("Scale cell", [scaleIn], () => {
    sendOp("scale_cell", { factor: parseFloat(scaleIn.value)||1 });
  });

  // Sort by element
  opRow("Sort by element", [], () => sendOp("sort", {}));

  // ── collect & send helpers ─────────────────────────────────────────────────

  function collectSiteEdits() {
    // Gather all rows from the sites table
    const symbols = [];
    const coords = [];
    tbody.querySelectorAll("tr").forEach(tr => {
      const inputs = tr.querySelectorAll("input");
      if (inputs.length < 4) return;
      symbols.push(inputs[0].value.trim());
      coords.push([
        parseFloat(inputs[1].value) || 0,
        parseFloat(inputs[2].value) || 0,
        parseFloat(inputs[3].value) || 0,
      ]);
    });
    return { symbols, coords };
  }

  function sendCurrentState(op) {
    const atoms = getAtoms();
    if (!atoms) return;
    const { symbols, coords } = collectSiteEdits();
    const payload = { ...atoms, symbols };
    if (coordMode === "fractional") {
      payload.scaled_positions = coords;
      payload.coords_are_fractional = true;
    } else {
      payload.positions = coords;
    }
    if (op) payload._op = op;
    model.set("atoms_json", JSON.stringify(payload));
    model.set("atoms_trigger", model.get("atoms_trigger") + 1);
    model.save_changes();
  }

  function sendOp(name, params) {
    // Send the operation via a dedicated op_json traitlet so that atoms_json
    // is never set to an op-only payload.  The change:atoms_json listener
    // (syncFromModel) would otherwise fire with data that has no "symbols"
    // key and crash before Python has had a chance to respond.
    model.set("op_json", JSON.stringify({ name, params }));
    model.set("atoms_trigger", model.get("atoms_trigger") + 1);
    model.save_changes();
  }

  // ── sync from Python ────────────────────────────────────────────────────────

  function syncFromModel() {
    const atoms = getAtoms();
    buildTableRows(atoms);
    updateCellInputs(atoms);
  }

  model.on("change:atoms_json", syncFromModel);

  model.on("change:error", () => {
    const err = model.get("error");
    if (err) {
      errorBox.textContent = "\u26a0 " + err;
      errorBox.hidden = false;
    } else {
      errorBox.hidden = true;
    }
  });

  // ── initial render ─────────────────────────────────────────────────────────
  syncFromModel();
}

export default { render };
