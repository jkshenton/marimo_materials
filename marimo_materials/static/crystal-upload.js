function render({ model, el }) {
  // --- DOM skeleton ---
  const root = document.createElement("div");
  root.className = "cu-root";

  const dropzone = document.createElement("div");
  dropzone.className = "cu-dropzone";
  dropzone.innerHTML = `
    <span class="cu-icon">&#8679;</span>
    <span class="cu-label">Drop a structure file here<br><small>or click to browse</small></span>
  `;

  const fileInfo = document.createElement("div");
  fileInfo.className = "cu-fileinfo";
  fileInfo.hidden = true;

  const controls = document.createElement("div");
  controls.className = "cu-controls";

  const fmtGroup = document.createElement("label");
  fmtGroup.className = "cu-field";
  const fmtTitle = document.createElement("span");
  fmtTitle.textContent = "format";
  const fmtInput = document.createElement("input");
  fmtInput.type = "text";
  fmtInput.placeholder = "auto-detect";
  fmtInput.value = model.get("ase_format");
  fmtInput.className = "cu-input";
  fmtGroup.appendChild(fmtTitle);
  fmtGroup.appendChild(fmtInput);

  const idxGroup = document.createElement("label");
  idxGroup.className = "cu-field";
  const idxTitle = document.createElement("span");
  idxTitle.textContent = "index";
  const idxInput = document.createElement("input");
  idxInput.type = "text";
  idxInput.value = model.get("index");
  idxInput.placeholder = "0  or  :  for all";
  idxInput.className = "cu-input cu-input--short";
  idxGroup.appendChild(idxTitle);
  idxGroup.appendChild(idxInput);

  const kwGroup = document.createElement("label");
  kwGroup.className = "cu-field cu-field--full";
  const kwTitle = document.createElement("span");
  kwTitle.textContent = "extra kwargs (JSON)";
  const kwInput = document.createElement("input");
  kwInput.type = "text";
  kwInput.placeholder = '{"key": "value"}';
  kwInput.value = model.get("extra_kwargs_json");
  kwInput.className = "cu-input cu-input--wide";
  kwGroup.appendChild(kwTitle);
  kwGroup.appendChild(kwInput);

  controls.appendChild(fmtGroup);
  controls.appendChild(idxGroup);
  controls.appendChild(kwGroup);

  const parseBtn = document.createElement("button");
  parseBtn.className = "cu-parse-btn";
  parseBtn.textContent = "Parse structure";

  const errorBox = document.createElement("div");
  errorBox.className = "cu-error";
  errorBox.hidden = true;
  const errorIcon = document.createElement("span");
  errorIcon.className = "cu-error-icon";
  errorIcon.textContent = "\u26a0";
  const errorMsg = document.createElement("span");
  errorMsg.className = "cu-error-msg";
  errorBox.appendChild(errorIcon);
  errorBox.appendChild(errorMsg);

  root.appendChild(dropzone);
  root.appendChild(fileInfo);
  root.appendChild(controls);
  root.appendChild(parseBtn);
  root.appendChild(errorBox);
  el.appendChild(root);

  // Hidden file input for click-to-browse
  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.style.display = "none";
  el.appendChild(fileInput);

  // --- helpers ---
  function updateFileInfo() {
    const name = model.get("filename");
    const count = model.get("frames_count");
    if (!name) return;
    const frameNote = count > 1 ? `  \u2022  ${count} frames` : "";
    fileInfo.textContent = `\u2713 ${name}${frameNote}`;
    fileInfo.hidden = false;
    dropzone.classList.add("cu-dropzone--loaded");
  }

  function flushInputs() {
    model.set("ase_format", fmtInput.value.trim());
    model.set("index", idxInput.value.trim() || "0");
    model.set("extra_kwargs_json", kwInput.value.trim());
  }

  function loadFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const bytes = new Uint8Array(e.target.result);
      // Encode to base64 in chunks to avoid call-stack overflow on large files
      let binary = "";
      const chunkSize = 8192;
      for (let i = 0; i < bytes.byteLength; i += chunkSize) {
        binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
      }
      const b64 = btoa(binary);
      const kb = (file.size / 1024).toFixed(1);
      // Show the filename immediately so the user gets feedback.
      // Frame count will be filled in after a successful parse.
      fileInfo.textContent = `\u2713 ${file.name}  (${kb}\u202fKB) \u2013 ready to parse`;
      fileInfo.hidden = false;
      dropzone.classList.add("cu-dropzone--loaded");
      errorBox.hidden = true;
      model.set("filename", file.name);
      model.set("file_content_b64", b64);
      model.save_changes();
    };
    reader.readAsArrayBuffer(file);
  }

  // --- events ---
  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("cu-dropzone--hover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("cu-dropzone--hover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("cu-dropzone--hover");
    const file = e.dataTransfer?.files?.[0];
    if (file) loadFile(file);
  });

  fileInput.addEventListener("change", () => {
    const file = fileInput.files?.[0];
    if (file) loadFile(file);
  });

  // Sync each input on blur so values are committed before parse fires.
  fmtInput.addEventListener("blur", () => {
    model.set("ase_format", fmtInput.value.trim());
    model.save_changes();
  });
  idxInput.addEventListener("blur", () => {
    model.set("index", idxInput.value.trim() || "0");
    model.save_changes();
  });
  kwInput.addEventListener("blur", () => {
    model.set("extra_kwargs_json", kwInput.value.trim());
    model.save_changes();
  });

  parseBtn.addEventListener("click", () => {
    // Flush all inputs and increment parse_trigger in a single save_changes().
    // anywidget wraps incoming comm messages in hold_trait_notifications, so
    // Python sees ALL updated values atomically before _on_parse_trigger fires.
    flushInputs();
    model.set("parse_trigger", model.get("parse_trigger") + 1);
    model.save_changes();
  });

  // Sync changes pushed from Python
  model.on("change:ase_format",        () => { fmtInput.value = model.get("ase_format"); });
  model.on("change:index",             () => { idxInput.value = model.get("index"); });
  model.on("change:extra_kwargs_json", () => { kwInput.value  = model.get("extra_kwargs_json"); });
  model.on("change:frames_count",      () => { updateFileInfo(); });
  model.on("change:parse_error", () => {
    const err = model.get("parse_error");
    if (err) {
      errorMsg.textContent = err;
      errorBox.hidden = false;
    } else {
      errorBox.hidden = true;
      errorMsg.textContent = "";
    }
  });
  model.on("change:filename", () => { updateFileInfo(); });
}

export default { render };
