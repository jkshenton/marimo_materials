"""CrystalEditorWidget – interactively edit an ASE Atoms object.

Usage pattern::

    from marimo_materials import CrystalEditorWidget
    from ase.build import bulk
    import marimo as mo

    editor = CrystalEditorWidget(bulk("Cu", "fcc", a=3.61))
    widget = mo.ui.anywidget(editor)
    widget

    # In a dependent cell:
    atoms = editor.atoms   # edited ase.Atoms

The widget provides three panels:

* **Sites** – table of per-atom symbol and x/y/z coordinates; add or delete
  individual sites.
* **Unit cell** – lattice parameters (a, b, c, α, β, γ), PBC toggles per axis,
  with an option to scale atomic positions with the cell.
* **Operations** – one-click buttons for ``wrap``, ``center``, ``repeat``,
  ``translate``, ``scale cell``, and ``sort by element``.

All changes require an explicit button click; nothing is applied automatically.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

import anywidget
import numpy as np
import traitlets


def _atoms_to_json(atoms: Any) -> str:
    """Serialise an ``ase.Atoms`` object to the JSON format consumed by the JS."""
    cellpar = atoms.cell.cellpar().tolist()  # [a,b,c,α,β,γ]
    return json.dumps({
        "symbols": list(atoms.get_chemical_symbols()),
        "positions": atoms.get_positions().tolist(),
        "scaled_positions": atoms.get_scaled_positions().tolist(),
        "cellpar": [round(v, 8) for v in cellpar],
        "pbc": atoms.get_pbc().tolist(),
    })


def _atoms_from_payload(payload: dict) -> Any:
    """Build an ``ase.Atoms`` from a JS payload dict (no ``_op`` key)."""
    import ase
    from ase.cell import Cell

    symbols = payload["symbols"]
    cellpar = payload.get("cellpar", [1, 1, 1, 90, 90, 90])
    pbc     = payload.get("pbc", [False, False, False])
    cell    = Cell.fromcellpar(cellpar)

    if payload.get("coords_are_fractional"):
        atoms = ase.Atoms(
            symbols=symbols,
            scaled_positions=payload["scaled_positions"],
            cell=cell,
            pbc=pbc,
        )
    else:
        atoms = ase.Atoms(
            symbols=symbols,
            positions=payload["positions"],
            cell=cell,
            pbc=pbc,
        )
    return atoms


def _apply_op(atoms: Any, op: dict) -> Any:
    """Apply a single operation dict ``{"name": ..., "params": {...}}`` to atoms.

    Returns the (possibly new) Atoms object.  Raises ``ValueError`` on bad
    inputs so callers can surface the message to the user.
    """
    name   = op["name"]
    params = op.get("params", {})

    if name == "wrap":
        atoms.wrap()

    elif name == "center":
        vacuum = float(params.get("vacuum", 0))
        axis   = params.get("axis", [0, 1, 2])
        atoms.center(vacuum=vacuum, axis=axis)

    elif name == "repeat":
        rep = params.get("rep", [1, 1, 1])
        atoms = atoms.repeat(rep)

    elif name == "translate":
        d = params.get("displacement", [0, 0, 0])
        atoms.translate(d)

    elif name == "scale_cell":
        factor = float(params.get("factor", 1))
        atoms.set_cell(atoms.cell * factor, scale_atoms=True)

    elif name == "sort":
        from ase.build import sort as ase_sort
        atoms = ase_sort(atoms)

    elif name == "set_cell":
        from ase.cell import Cell
        cellpar     = params.get("cellpar", atoms.cell.cellpar().tolist())
        pbc         = params.get("pbc", atoms.get_pbc().tolist())
        scale_atoms = bool(params.get("scale_atoms", False))
        new_cell    = Cell.fromcellpar(cellpar)
        atoms.set_pbc(pbc)
        atoms.set_cell(new_cell, scale_atoms=scale_atoms)

    elif name == "delete_atom":
        idx = int(params.get("index", -1))
        del atoms[idx]

    elif name == "add_atom":
        import ase
        symbol   = params.get("symbol", "X")
        position = params.get("position", [0, 0, 0])
        if params.get("fractional"):
            position = np.dot(position, atoms.cell)
        atoms.append(ase.Atom(symbol, position))

    else:
        raise ValueError(f"Unknown operation: {name!r}")

    return atoms


class CrystalEditorWidget(anywidget.AnyWidget):
    """Interactive editor for an ``ase.Atoms`` object.

    Parameters
    ----------
    atoms:
        The structure to load into the editor.  Passing ``None`` starts with
        an empty widget; you can still load a structure later by setting
        ``editor.atoms = some_atoms``.
    """

    _esm = Path(__file__).parent / "static" / "crystal-editor.js"
    _css = Path(__file__).parent / "static" / "crystal-editor.css"

    # Synced with JS
    atoms_json:    str = traitlets.Unicode("").tag(sync=True)
    atoms_trigger: int = traitlets.Int(0).tag(sync=True)
    error:         str = traitlets.Unicode("").tag(sync=True)
    n_atoms:       int = traitlets.Int(0).tag(sync=True)

    def __init__(self, atoms: Any = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._atoms: Any = None
        if atoms is not None:
            self._load(atoms)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self, atoms: Any) -> None:
        """Store atoms and push to JS."""
        self._atoms = atoms.copy()
        self.atoms_json = _atoms_to_json(self._atoms)
        self.n_atoms = len(self._atoms)
        self.error = ""

    # ------------------------------------------------------------------
    # Observer
    # ------------------------------------------------------------------

    @traitlets.observe("atoms_trigger")
    def _on_trigger(self, _change: dict) -> None:  # noqa: ARG002
        """Apply site edits (and optional operation) sent by the JS."""
        if not self.atoms_json:
            return

        self.error = ""
        try:
            payload = json.loads(self.atoms_json)
            op      = payload.pop("_op", None)

            with warnings.catch_warnings():
                warnings.simplefilter("error")
                atoms = _atoms_from_payload(payload)
                if op is not None:
                    atoms = _apply_op(atoms, op)

            self._atoms  = atoms
            self.atoms_json = _atoms_to_json(atoms)
            self.n_atoms = len(atoms)

        except Exception as exc:
            self.error = str(exc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def atoms(self) -> Any:
        """The current ``ase.Atoms`` object, or ``None`` if nothing is loaded."""
        return self._atoms

    @atoms.setter
    def atoms(self, new_atoms: Any) -> None:
        """Replace the structure in the editor programmatically."""
        if new_atoms is None:
            self._atoms = None
            self.atoms_json = ""
            self.n_atoms = 0
            self.error = ""
        else:
            self._load(new_atoms)
