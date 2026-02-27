"""CrystalViewer – a marimo-friendly wrapper around weas-widget.

Usage pattern::

    from marimo_materials import CrystalViewer

    cv = CrystalViewer(model_style=2, color_type="VESTA")
    cv.load_example("tio2.cif")

    # Render the 3D viewer as a plain cell output:
    cv.weas

    # Or load your own structure:
    cv.from_ase(atoms)
    cv.weas
"""

from __future__ import annotations

from typing import Any


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
