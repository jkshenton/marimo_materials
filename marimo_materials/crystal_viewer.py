"""CrystalViewer – a marimo-friendly wrapper around weas-widget.

Usage pattern::

    from marimo_materials import CrystalViewer
    import marimo as mo

    cv = CrystalViewer()
    cv.load_example("tio2.cif")

    # 1. Display the 3D viewer (plain cell output – do NOT wrap in mo.ui.anywidget)
    cv.base_widget          # renders the interactive 3D canvas

    # 2. In a *separate* cell, wrap only the thin state widget for reactivity
    state = mo.ui.anywidget(cv.state_widget)
    state                   # invisible placeholder – just needed for reactivity

    # 3. In dependent cells, read interactive state back from marimo:
    selected = state.value["selected_atoms"]    # list[int]  – 0-based indices
    cam_pos  = state.value["camera_position"]   # list[float]
    cam_zoom = state.value["camera_zoom"]       # float

Why two widgets?
    Wrapping ``base_widget`` in ``mo.ui.anywidget()`` and then writing style
    traitlets from Python cells creates a JS feedback loop (Python sets
    modelStyle → weas JS re-applies it → fires viewerUpdated → model.set()
    triggers change:modelStyle again → infinite recursion).  By keeping the
    3D canvas widget separate from the reactive state widget we avoid any
    Python→JS→Python cycles.
"""

from __future__ import annotations

from typing import Any

import anywidget
import traitlets


class _StateWidget(anywidget.AnyWidget):
    """Minimal anywidget that carries only the state we want marimo to react to.

    We never write to this widget from reactive marimo cells – only from
    Python ``observe`` callbacks registered on the weas base widget.  That
    means the JS side is a no-op (empty render function) and there is no
    feedback loop.
    """

    _esm = """
    function render({ model, el }) {
        // no visual output – state-only widget
    }
    export default { render };
    """

    selected_atoms: list = traitlets.List([]).tag(sync=True)
    camera_position: list = traitlets.List([]).tag(sync=True)
    camera_look_at: list = traitlets.List([]).tag(sync=True)
    camera_zoom: float = traitlets.Float(1.0).tag(sync=True)
    model_style: int = traitlets.Int(0).tag(sync=True)
    color_type: str = traitlets.Unicode("JMOL").tag(sync=True)


class CrystalViewer:
    """Thin wrapper around ``WeasWidget`` for use in marimo notebooks.

    Load a crystal structure with ``load_example()``, ``from_ase()``, or
    ``from_pymatgen()``, then render it in marimo like this::

        cv = CrystalViewer(model_style=2, color_type="VESTA")
        cv.load_example("tio2.cif")

        # Cell A – display the 3D canvas (plain output, NOT mo.ui.anywidget)
        cv.base_widget

        # Cell B – wrap only the thin state widget so marimo can react to it
        state = mo.ui.anywidget(cv.state_widget)
        state   # (invisible – just hooks into the reactive graph)

        # Cell C – read back interactive state (re-runs on every change)
        state.value["selected_atoms"]    # list[int]
        state.value["camera_position"]   # list[float]
        state.value["camera_zoom"]       # float

    **Why not ``mo.ui.anywidget(cv.base_widget)``?**
    Wrapping the weas canvas widget AND writing style traitlets from Python
    reactive cells creates an infinite JS recursion: Python sets ``modelStyle``
    → weas JS re-applies it → fires ``viewerUpdated`` → ``model.set()``
    re-triggers ``change:modelStyle`` in the same JS tick → loop.
    This design separates concerns: the 3D canvas is display-only; state is
    mirrored one-way (weas → ``_StateWidget``) via Python ``observe`` callbacks.

    Args:
        model_style: Initial render style.
            0 = Ball, 1 = Ball+Stick, 2 = Polyhedra, 3 = Stick, 4 = Line.
        color_type: Initial colour scheme – ``"JMOL"``, ``"VESTA"``, or
            ``"CPK"``.
        show_bonded_atoms: Whether to show atoms bonded across cell boundaries.
        width: Viewer canvas width (CSS string, e.g. ``"100%"`` or ``"600px"``).
        height: Viewer canvas height (CSS string, e.g. ``"500px"``).
        show_gui: Whether to show the weas built-in GUI panel.  Set to
            ``False`` to hide it and avoid overflow in narrow layouts.
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
        width: str = "100%",
        height: str = "500px",
        show_gui: bool = False,
    ) -> None:
        try:
            from weas_widget.weas_core import WeasWidgetCore as WeasWidget
        except ImportError as exc:
            raise ImportError(
                "weas-widget (local anywidget build) is required for CrystalViewer. "
                "Install with: uv add --editable /path/to/weas-widget"
            ) from exc

        # Build guiConfig: WeasWidgetCore deep-merges this into its marimo defaults.
        gui_override: dict[str, object] = {}
        if not show_gui:
            gui_override = {
                "controls": {"enabled": False},
                "buttons": {"enabled": False},
            }
        self.weas = WeasWidget(guiConfig=gui_override)

        # Size the 3D canvas via the viewerStyle traitlet on WeasWidgetCore itself
        # (WeasWidgetCore IS the BaseWidget – it has no separate ._widget attribute).
        self.weas.viewerStyle = {"width": width, "height": height}

        # Set initial render style via the AtomsViewer helper.
        self.weas.avr.model_style = model_style
        self.weas.avr.color_type = color_type
        self.weas.avr.show_bonded_atoms = show_bonded_atoms

        # Thin state widget – only this one is wrapped in mo.ui.anywidget().
        self._state = _StateWidget()
        self._state.model_style = model_style
        self._state.color_type = color_type

        # Mirror weas traitlets → _StateWidget via one-way Python observe.
        # We NEVER write back to self.weas._widget from a reactive marimo cell,
        # so there is no Python→JS→Python feedback loop.
        # WeasWidgetCore IS the anywidget; observe its traitlets directly.
        bw = self.weas

        def _on_selection(change: dict) -> None:
            self._state.selected_atoms = list(change["new"] or [])

        def _on_cam_pos(change: dict) -> None:
            self._state.camera_position = list(change["new"] or [])

        def _on_cam_look(change: dict) -> None:
            self._state.camera_look_at = list(change["new"] or [])

        def _on_cam_zoom(change: dict) -> None:
            self._state.camera_zoom = float(change["new"] or 1.0)

        def _on_model_style(change: dict) -> None:
            self._state.model_style = int(change["new"] or 0)

        def _on_color_type(change: dict) -> None:
            self._state.color_type = str(change["new"] or "JMOL")

        bw.observe(_on_selection, names=["selectedAtomsIndices"])
        bw.observe(_on_cam_pos, names=["cameraPosition"])
        bw.observe(_on_cam_look, names=["cameraLookAt"])
        bw.observe(_on_cam_zoom, names=["cameraZoom"])
        bw.observe(_on_model_style, names=["modelStyle"])
        bw.observe(_on_color_type, names=["colorType"])

    # ------------------------------------------------------------------
    # Load helpers
    # ------------------------------------------------------------------

    def load_example(self, name: str = "tio2.cif") -> "CrystalViewer":
        """Load a built-in example structure (e.g. ``"tio2.cif"``)."""
        self.weas.load_example(name)
        return self

    def from_ase(self, atoms: Any) -> "CrystalViewer":
        """Load an ASE ``Atoms`` object (or a list of ``Atoms`` for trajectories)."""
        self.weas.from_ase(atoms)
        return self

    def from_pymatgen(self, structure: Any) -> "CrystalViewer":
        """Load a pymatgen ``Structure`` or ``IStructure``."""
        self.weas.from_pymatgen(structure)
        return self

    # ------------------------------------------------------------------
    # marimo surface
    # ------------------------------------------------------------------

    @property
    def base_widget(self) -> Any:
        """The weas ``BaseWidget`` (anywidget).

        Render this as a plain cell output to display the 3D canvas::

            cv.base_widget   # do NOT pass to mo.ui.anywidget()

        Writing traitlets to this object from marimo reactive cells causes
        an infinite JS recursion – use :attr:`state_widget` for reactivity.
        """
        return self.weas

    @property
    def state_widget(self) -> _StateWidget:
        """Thin read-only state widget to wrap with ``mo.ui.anywidget()``.

        This is the correct object to make reactive in marimo::

            state = mo.ui.anywidget(cv.state_widget)

        Its ``.value`` dict exposes:
        ``selected_atoms``, ``camera_position``, ``camera_look_at``,
        ``camera_zoom``, ``model_style``, ``color_type``.
        """
        return self._state

    # ------------------------------------------------------------------
    # Style setters (safe to call imperatively – not from reactive cells)
    # ------------------------------------------------------------------

    @property
    def model_style(self) -> int:
        """Current render style (0–4)."""
        return int(self.weas.avr.model_style)

    @model_style.setter
    def model_style(self, value: int) -> None:
        self.weas.avr.model_style = int(value)

    @property
    def color_type(self) -> str:
        """Current colour scheme (``"JMOL"``, ``"VESTA"``, ``"CPK"``)."""
        return str(self.weas.avr.color_type)

    @color_type.setter
    def color_type(self, value: str) -> None:
        self.weas.avr.color_type = value

    @property
    def show_bonded_atoms(self) -> bool:
        """Whether bonded atoms outside the unit cell are shown."""
        return bool(self.weas.avr.show_bonded_atoms)

    @show_bonded_atoms.setter
    def show_bonded_atoms(self, value: bool) -> None:
        self.weas.avr.show_bonded_atoms = bool(value)

    # ------------------------------------------------------------------
    # Point-in-time state snapshots (non-reactive)
    # ------------------------------------------------------------------

    @property
    def selected_atoms(self) -> list[int]:
        """Snapshot of the current atom selection (0-based indices).

        For reactive access use ``state.value["selected_atoms"]``
        where *state* is ``mo.ui.anywidget(cv.state_widget)``.
        """
        return list(self.weas.avr.selected_atoms_indices or [])

    @property
    def camera_position(self) -> list[float]:
        """Camera position in world-space ``[x, y, z]``."""
        return list(self.weas.cameraPosition)

    @property
    def camera_look_at(self) -> list[float]:
        """Camera look-at point in world-space ``[x, y, z]``."""
        return list(self.weas.cameraLookAt)

    @property
    def camera_zoom(self) -> float:
        """Camera zoom level."""
        return float(self.weas.cameraZoom)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def to_ase(self) -> Any:
        """Export the current structure as an ASE ``Atoms`` object."""
        return self.weas.to_ase()

    def to_pymatgen(self) -> Any:
        """Export the current structure as a pymatgen ``Structure``."""
        return self.weas.to_pymatgen()
