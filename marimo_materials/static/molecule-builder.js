const COMMON_MOLECULES = [
  "H2O", "CO2", "CH4", "NH3", "H2", "N2", "O2", "CO", "NO",
  "C2H4", "C2H6", "C2H2", "C6H6", "CH3OH", "H2O2", "SO2",
  "HCl", "HF", "CH2O", "H2S", "CCl4", "CF4", "C3H8", "CH3Cl",
];

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
  title.textContent = "Molecule Builder";
  root.appendChild(title);

  const grid = document.createElement("div");
  grid.className = "cb-grid";

  // Molecule name with datalist for autocomplete
  const nameField = field("Molecule name");
  const listId = "cb-mol-list-" + Math.random().toString(36).slice(2);
  const nameInput = document.createElement("input");
  nameInput.type = "text";
  nameInput.className = "cb-input";
  nameInput.value = model.get("name");
  nameInput.placeholder = "e.g. H2O";
  nameInput.setAttribute("list", listId);
  const datalist = document.createElement("datalist");
  datalist.id = listId;
  COMMON_MOLECULES.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m;
    datalist.appendChild(opt);
  });
  nameField.appendChild(nameInput);
  nameField.appendChild(datalist);
  grid.appendChild(nameField);

  // Vacuum
  const vacuumField = field("Vacuum (Å)");
  const vacuumInput = document.createElement("input");
  vacuumInput.type = "number";
  vacuumInput.className = "cb-input";
  vacuumInput.value = model.get("vacuum");
  vacuumInput.min = "0";
  vacuumInput.max = "60";
  vacuumInput.step = "0.5";
  vacuumField.appendChild(vacuumInput);
  grid.appendChild(vacuumField);

  root.appendChild(grid);

  // Status bar
  const status = document.createElement("div");
  status.className = "cb-status";
  root.appendChild(status);

  el.appendChild(root);

  // ── sync to model ─────────────────────────────────────────────────────────
  function sync() {
    model.set("name", nameInput.value.trim() || "H2O");
    model.set("vacuum", Math.max(0, parseFloat(vacuumInput.value) || 5.0));
    model.save_changes();
  }

  vacuumInput.addEventListener("change", sync);

  let debounceTimer;
  nameInput.addEventListener("input", () => {
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
  updateStatus();
}

export default { render };
