"""CrystalViewer – a marimo-friendly wrapper around weas-widget.

Usage pattern::

    from marimo_materials import CrystalViewer
    import marimo as mo

    cv = CrystalViewer(model_style=2, color_type="VESTA")
    cv.load_example("tio2.cif")

    # Render the controls panel (updates the viewer live, no cell re-run needed):
    mo.ui.anywidget(cv.panel())

    # Render the 3D viewer in a separate cell:
    cv.weas

    # Or load your own structure:
    cv.from_ase(atoms)
    cv.weas
"""

from __future__ import annotations

from typing import Any


class _CrystalViewerControls:
    """Internal anywidget that renders a controls panel for CrystalViewer.

    Not exported – obtain via ``CrystalViewer.panel()``.

    Architecture: the ControlsWidget traitlets mirror the camelCase traitlets
    on weas's ``BaseWidget`` directly. Python ``observe`` callbacks write those
    same traitlets on ``viewer.weas`` (``BaseWidget``) – deliberately bypassing
    the ``AtomsViewer`` Python setters which call ``update_atoms()`` and trigger
    a dict-traitlet cascade. Setting the ``BaseWidget`` traitlet directly fires
    the backbone ``change:KEY`` event that weas's own JS handlers already
    consume (→ ``K.avr.applyState(…, {redraw:"full"})``).  Backbone's ``===``
    equality check for scalar (Int/Unicode/Bool) traitlets makes the
    ``applyState → viewerUpdated`` echo a no-op for the same value.
    """

    _esm = """
function mkSelect(label, options, initVal, onChange) {
  const wrap = document.createElement("label");
  wrap.className = "cvc-field";
  const lbl = document.createElement("span");
  lbl.textContent = label;
  const sel = document.createElement("select");
  options.forEach(([text, val]) => {
    const opt = document.createElement("option");
    opt.value = String(val);
    opt.textContent = text;
    if (String(val) === String(initVal)) opt.selected = true;
    sel.appendChild(opt);
  });
  sel.addEventListener("change", () => onChange(sel.value));
  wrap.appendChild(lbl);
  wrap.appendChild(sel);
  return wrap;
}

function mkCheckbox(label, initVal, onChange) {
  const wrap = document.createElement("label");
  wrap.className = "cvc-field cvc-check";
  const inp = document.createElement("input");
  inp.type = "checkbox";
  inp.checked = initVal;
  inp.addEventListener("change", () => onChange(inp.checked));
  const span = document.createElement("span");
  span.textContent = label;
  wrap.appendChild(inp);
  wrap.appendChild(span);
  return wrap;
}

function mkRow(parent) {
  const row = document.createElement("div");
  row.className = "cvc-row";
  parent.appendChild(row);
  return row;
}

function render({ model, el }) {
  el.className = "cvc-panel";

  // Write the traitlet back to our own model; the Python observer forwards
  // it to viewer.weas (BaseWidget) which fires change:KEY in JS without
  // going through AtomsViewer.update_atoms().
  function set(key, val) {
    model.set(key, val);
    model.save_changes();
  }

  const row1 = mkRow(el);
  const row2 = mkRow(el);
  const row3 = mkRow(el);

  // Row 1 – render appearance
  row1.appendChild(mkSelect("Model style",
    [["Ball",0],["Ball+Stick",1],["Polyhedra",2],["Stick",3],["Line",4]],
    model.get("modelStyle"),
    v => set("modelStyle", parseInt(v))
  ));
  row1.appendChild(mkSelect("Colour scheme",
    [["JMOL","JMOL"],["VESTA","VESTA"],["CPK","CPK"]],
    model.get("colorType"),
    v => set("colorType", v)
  ));
  row1.appendChild(mkSelect("Material",
    [["Standard","Standard"],["Phong","Phong"],["Basic","Basic"]],
    model.get("materialType"),
    v => set("materialType", v)
  ));

  // Row 2 – colouring / labelling
  row2.appendChild(mkSelect("Colour by",
    [["Element","Element"],["Index","Index"],["Random","Random"],["Uniform","Uniform"]],
    model.get("colorBy"),
    v => set("colorBy", v)
  ));
  row2.appendChild(mkSelect("Radius type",
    [["Covalent","Covalent"],["VDW","VDW"]],
    model.get("radiusType"),
    v => set("radiusType", v)
  ));
  row2.appendChild(mkSelect("Atom labels",
    [["None","None"],["Symbol","Symbol"],["Index","Index"]],
    model.get("atomLabelType"),
    v => set("atomLabelType", v)
  ));

  // Row 3 – bond / display toggles
  row3.appendChild(mkCheckbox("Bonded atoms", model.get("showBondedAtoms"),
    v => set("showBondedAtoms", v)));
  row3.appendChild(mkCheckbox("Hide long bonds", model.get("hideLongBonds"),
    v => set("hideLongBonds", v)));
  row3.appendChild(mkCheckbox("H-bonds", model.get("showHydrogenBonds"),
    v => set("showHydrogenBonds", v)));
  row3.appendChild(mkCheckbox("Out-boundary bonds", model.get("showOutBoundaryBonds"),
    v => set("showOutBoundaryBonds", v)));
  row3.appendChild(mkCheckbox("Atom legend", model.get("showAtomLegend"),
    v => set("showAtomLegend", v)));
}

export default { render };
"""

    _css = """
.cvc-panel { display: flex; flex-direction: column; gap: 6px;
  padding: 8px 10px; font-size: 13px; }
.cvc-row { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; }
.cvc-field { display: flex; flex-direction: column; gap: 2px; }
.cvc-field > span:first-child { font-size: 10px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.05em; color: #888; }
.cvc-field select { font-size: 13px; padding: 3px 6px; border-radius: 4px;
  border: 1px solid #ccc; background: #fff; cursor: pointer; min-width: 90px; }
.cvc-check { flex-direction: row !important; align-items: center;
  gap: 5px; cursor: pointer; }
.cvc-check input { margin: 0; cursor: pointer; }
.cvc-check > span { font-size: 12px !important; text-transform: none !important;
  letter-spacing: normal !important; color: #444 !important;
  font-weight: normal !important; }
@media (prefers-color-scheme: dark) {
  .cvc-field > span:first-child { color: #777; }
  .cvc-field select { background: #2a2a2a; border-color: #555; color: #eee; }
  .cvc-check > span { color: #ccc !important; }
}
"""

    def __init__(self, viewer: "CrystalViewer") -> None:
        try:
            import anywidget
            import traitlets
        except ImportError as exc:
            raise ImportError(
                "anywidget and traitlets are required for CrystalViewer.panel(). "
                "Install with: pip install anywidget traitlets"
            ) from exc

        # Read initial values from BaseWidget directly (camelCase traitlets).
        weas = viewer.weas  # BaseWidget – bypasses AtomsViewer setters

        ControlsWidget = type("ControlsWidget", (anywidget.AnyWidget,), {
            "_esm": self._esm,
            "_css": self._css,
            # Mirror the camelCase BaseWidget traitlets.
            "modelStyle": traitlets.Int(int(weas.modelStyle)).tag(sync=True),
            "colorType": traitlets.Unicode(str(weas.colorType)).tag(sync=True),
            "colorBy": traitlets.Unicode(str(weas.colorBy)).tag(sync=True),
            "materialType": traitlets.Unicode(str(weas.materialType)).tag(sync=True),
            "radiusType": traitlets.Unicode(str(weas.radiusType)).tag(sync=True),
            "atomLabelType": traitlets.Unicode(str(weas.atomLabelType)).tag(sync=True),
            "showBondedAtoms": traitlets.Bool(bool(weas.showBondedAtoms)).tag(sync=True),
            "hideLongBonds": traitlets.Bool(bool(weas.hideLongBonds)).tag(sync=True),
            "showHydrogenBonds": traitlets.Bool(bool(weas.showHydrogenBonds)).tag(sync=True),
            "showOutBoundaryBonds": traitlets.Bool(bool(weas.showOutBoundaryBonds)).tag(sync=True),
            "showAtomLegend": traitlets.Bool(bool(weas.showAtomLegend)).tag(sync=True),
        })

        self._widget = ControlsWidget()

        # Forward each change directly to the BaseWidget traitlet, bypassing
        # AtomsViewer setters.  This fires backbone change:KEY in JS (handled
        # by weas) without triggering update_atoms() or any cascade.
        def _on_change(change: dict) -> None:
            setattr(weas, change["name"], change["new"])

        for name in [
            "modelStyle", "colorType", "colorBy", "materialType", "radiusType",
            "atomLabelType", "showBondedAtoms", "hideLongBonds",
            "showHydrogenBonds", "showOutBoundaryBonds", "showAtomLegend",
        ]:
            self._widget.observe(_on_change, names=[name])



class CrystalViewer:
    """Thin wrapper around weas-widget's BaseWidget/AtomsViewer for marimo notebooks.

    Load a crystal structure with :meth:`load_example`, :meth:`from_ase`, or
    :meth:`from_pymatgen`, then display it::

        cv = CrystalViewer(model_style=2, color_type="VESTA")
        cv.load_example("tio2.cif")
        cv.weas   # renders the interactive 3D canvas

    Args:
        model_style: Render style.
            0 = Ball, 1 = Ball+Stick, 2 = Polyhedra, 3 = Stick, 4 = Line.
        color_type: Colour scheme – ``"JMOL"``, ``"VESTA"``, or ``"CPK"``.
        show_bonded_atoms: Whether to show atoms bonded across cell boundaries.
        boundary: Fractional-coordinate boundary ranges, e.g.
            ``[[-0.1, 1.1], [-0.1, 1.1], [-0.1, 1.1]]``.
        hide_long_bonds: Hide bonds longer than the weas threshold (default
            ``True``).
        show_hydrogen_bonds: Show hydrogen bonds (default ``False``).
        width: Viewer canvas width (CSS string, e.g. ``"100%"`` or ``"600px"``).
        height: Viewer canvas height (CSS string, e.g. ``"500px"``).
        show_gui: Whether to show the weas built-in GUI panel.
    """

    MODEL_STYLES: dict[str, int] = {
        "Ball": 0,
        "Ball+Stick": 1,
        "Polyhedra": 2,
        "Stick": 3,
        "Line": 4,
    }
    COLOR_TYPES: tuple[str, ...] = ("JMOL", "VESTA", "CPK")

    def __init__(
        self,
        *,
        model_style: int = 1,
        color_type: str = "JMOL",
        show_bonded_atoms: bool = False,
        boundary: list | None = None,
        hide_long_bonds: bool = True,
        show_hydrogen_bonds: bool = False,
        width: str = "100%",
        height: str = "500px",
        show_gui: bool = False,
    ) -> None:
        try:
            from weas_widget.base_widget import BaseWidget
            from weas_widget.atoms_viewer import AtomsViewer
        except ImportError as exc:
            raise ImportError(
                "weas-widget is required for CrystalViewer. "
                "Install with: pip install weas-widget"
            ) from exc

        gui_config: dict[str, object] = (
            {} if show_gui
            else {"controls": {"enabled": False}, "buttons": {"enabled": False}}
        )
        self.weas = BaseWidget(
            guiConfig=gui_config,
            viewerStyle={"width": width, "height": height},
        )
        self._avr = AtomsViewer(self.weas)
        self._avr.model_style = model_style
        self._avr.color_type = color_type
        self._avr.show_bonded_atoms = show_bonded_atoms
        self._avr.hide_long_bonds = hide_long_bonds
        self._avr.show_hydrogen_bonds = show_hydrogen_bonds
        if boundary is not None:
            self._avr.boundary = boundary

    def load_example(self, name: str = "tio2.cif") -> "CrystalViewer":
        """Load a built-in example structure (e.g. ``"tio2.cif"``)."""
        from weas_widget.utils import ASEAdapter, load_online_example
        self._avr.atoms = ASEAdapter.to_weas(load_online_example(name))
        return self

    def from_ase(self, atoms: Any) -> "CrystalViewer":
        """Load an ASE ``Atoms`` object (or list of ``Atoms`` for trajectories)."""
        from weas_widget.utils import ASEAdapter
        if isinstance(atoms, list):
            self._avr.atoms = [ASEAdapter.to_weas(a) for a in atoms]
        else:
            self._avr.atoms = ASEAdapter.to_weas(atoms)
        return self

    def from_pymatgen(self, structure: Any) -> "CrystalViewer":
        """Load a pymatgen ``Structure`` or ``IStructure``."""
        from weas_widget.utils import PymatgenAdapter
        self._avr.atoms = PymatgenAdapter.to_weas(structure)
        return self

    @property
    def model_style(self) -> int:
        """Current render style (0–4)."""
        return int(self._avr.model_style)

    @model_style.setter
    def model_style(self, value: int) -> None:
        self._avr.model_style = int(value)

    @property
    def color_type(self) -> str:
        """Current colour scheme (``"JMOL"``, ``"VESTA"``, ``"CPK"``)."""
        return str(self._avr.color_type)

    @color_type.setter
    def color_type(self, value: str) -> None:
        self._avr.color_type = value

    @property
    def show_bonded_atoms(self) -> bool:
        """Whether bonded atoms outside the unit cell are shown."""
        return bool(self._avr.show_bonded_atoms)

    @show_bonded_atoms.setter
    def show_bonded_atoms(self, value: bool) -> None:
        self._avr.show_bonded_atoms = bool(value)

    @property
    def hide_long_bonds(self) -> bool:
        """Whether bonds longer than the weas threshold are hidden."""
        return bool(self._avr.hide_long_bonds)

    @hide_long_bonds.setter
    def hide_long_bonds(self, value: bool) -> None:
        self._avr.hide_long_bonds = bool(value)

    @property
    def show_hydrogen_bonds(self) -> bool:
        """Whether hydrogen bonds are shown."""
        return bool(self._avr.show_hydrogen_bonds)

    @show_hydrogen_bonds.setter
    def show_hydrogen_bonds(self, value: bool) -> None:
        self._avr.show_hydrogen_bonds = bool(value)

    @property
    def boundary(self) -> list:
        """Fractional-coordinate boundary for periodic images.

        A list of three ``[min, max]`` ranges for the a, b, c axes, e.g.
        ``[[-0.1, 1.1], [-0.1, 1.1], [-0.1, 1.1]]``.
        """
        return list(self._avr.boundary)

    @boundary.setter
    def boundary(self, value: list) -> None:
        self._avr.boundary = value

    @property
    def color_by(self) -> str:
        """Array name used to colour atoms (e.g. ``"force_magnitude"``)."""
        return str(self._avr.color_by)

    @color_by.setter
    def color_by(self, value: str) -> None:
        self._avr.color_by = value

    @property
    def color_ramp(self) -> list:
        """List of hex colour stops used when :attr:`color_by` is set."""
        return list(self._avr.color_ramp)

    @color_ramp.setter
    def color_ramp(self, value: list) -> None:
        self._avr.color_ramp = value

    def to_ase(self) -> Any:
        """Export the current structure as an ASE ``Atoms`` object."""
        from weas_widget.utils import ASEAdapter
        return ASEAdapter.to_ase(self._avr.atoms)

    def to_pymatgen(self) -> Any:
        """Export the current structure as a pymatgen ``Structure``."""
        from weas_widget.utils import PymatgenAdapter
        return PymatgenAdapter.to_pymatgen(self._avr.atoms)

    def panel(self) -> Any:
        """Return a controls panel widget bound to this viewer.

        The panel communicates with the 3-D viewer directly via the weas
        backbone model so changes take effect live without requiring cell
        re-execution. Wrap it with ``mo.ui.anywidget`` before displaying::

            mo.ui.anywidget(cv.panel())

        **Live controls** (three rows):

        *Appearance row:* model style, colour scheme, material type.

        *Colouring row:* colour by, radius type, atom label type.

        *Toggle row:* show bonded atoms, hide long bonds, H-bonds,
        out-boundary bonds, atom legend.

        **Constructor-only** (set as :class:`CrystalViewer` kwargs; not
        adjustable in the panel because they involve JS array/dict traitlets
        that cause a backbone echo loop on every ``viewerUpdated`` event):

        - ``boundary`` – backbone compares JS arrays by reference, so every
          ``applyState → viewerUpdated`` cycle echoes it back as "changed".
        """
        return _CrystalViewerControls(self)._widget
