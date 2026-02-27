function render({ model, el }) {
  // ── DOM ───────────────────────────────────────────────────────────────────
  const root = document.createElement("div");
  root.className = "cd-root";

  const title = document.createElement("div");
  title.className = "cd-title";
  title.textContent = "Download Structure";
  root.appendChild(title);

  // Info row: formula + atom count
  const info = document.createElement("div");
  info.className = "cd-info";
  root.appendChild(info);

  // Format row
  const row = document.createElement("div");
  row.className = "cd-row";

  const fmtLabel = document.createElement("span");
  fmtLabel.className = "cd-label";
  fmtLabel.textContent = "Format";
  row.appendChild(fmtLabel);

  const FORMATS = [
    { value: "cif",         label: "CIF (.cif)" },
    { value: "vasp",        label: "POSCAR (VASP)" },
    { value: "xyz",         label: "XYZ (.xyz)" },
    { value: "extxyz",      label: "Extended XYZ (.extxyz)" },
    { value: "json",        label: "ASE JSON (.json)" },
    { value: "lammps-data",       label: "LAMMPS data (.lammps)" },
    { value: "proteindatabank",   label: "PDB (.pdb)" },
  ];

  const fmtSelect = document.createElement("select");
  fmtSelect.className = "cd-select";
  FORMATS.forEach(({ value, label }) => {
    const opt = document.createElement("option");
    opt.value = value;
    opt.textContent = label;
    if (value === model.get("format")) opt.selected = true;
    fmtSelect.appendChild(opt);
  });
  row.appendChild(fmtSelect);

  const dlBtn = document.createElement("button");
  dlBtn.className = "cd-btn";
  dlBtn.textContent = "Download";
  row.appendChild(dlBtn);

  root.appendChild(row);

  // Status / error bar
  const status = document.createElement("div");
  status.className = "cd-status";
  root.appendChild(status);

  el.appendChild(root);

  // ── helpers ───────────────────────────────────────────────────────────────
  function updateInfo() {
    const n = model.get("n_atoms");
    const formula = model.get("formula");
    if (n > 0) {
      info.textContent = `${formula}  ·  ${n} atoms`;
      info.className = "cd-info cd-info--visible";
    } else {
      info.className = "cd-info";
    }
  }

  function updateStatus() {
    const err = model.get("error");
    if (err) {
      status.textContent = "\u26a0\ufe0e " + err;
      status.className = "cd-status cd-status--visible cd-status--error";
    } else {
      status.className = "cd-status";
    }
    // Enable button only when there is content and no error
    dlBtn.disabled = !model.get("file_content") || !!err;
  }

  function doDownload() {
    const content = model.get("file_content");
    const filename = model.get("filename");
    if (!content) return;
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // ── events ────────────────────────────────────────────────────────────────
  fmtSelect.addEventListener("change", () => {
    model.set("format", fmtSelect.value);
    model.save_changes();
  });

  dlBtn.addEventListener("click", doDownload);

  model.on("change", () => {
    updateInfo();
    updateStatus();
  });

  // ── init ──────────────────────────────────────────────────────────────────
  updateInfo();
  updateStatus();
}

export default { render };
