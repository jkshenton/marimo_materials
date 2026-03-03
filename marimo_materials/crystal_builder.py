"""ASE Crystal Structure Builder widgets for marimo notebooks.

Four widget classes are provided, one for each structure type:

- :class:`BulkBuilderWidget`  – bulk crystals via ``ase.build.bulk``
- :class:`SurfaceBuilderWidget` – surface slabs via the facet-specific builders
- :class:`NanoparticleBuilderWidget` – nanoparticles via ``ase.cluster``
- :class:`MoleculeBuilderWidget` – gas-phase molecules via ``ase.build.molecule``

All widgets share the same usage pattern::

    from marimo_materials import BulkBuilderWidget
    from marimo_materials import CrystalViewer
    import marimo as mo

    bulk_w = mo.ui.anywidget(BulkBuilderWidget())
    bulk_w          # renders the interactive form

    # In a dependent cell – re-runs whenever the form changes:
    atoms = bulk_w.widget.atoms   # ase.Atoms or None
    cv = CrystalViewer()
    cv.from_ase(atoms)
    cv.base_widget

Shared traitlets (synced to the JS widget, readable via ``widget.value``):
    error   – empty string on success, error message on failure
    n_atoms – atom count of the last successfully built structure (0 on failure)
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

import anywidget
import traitlets

_STATIC = Path(__file__).parent / "static"
_CSS = (_STATIC / "crystal-shared.css").read_text() + (_STATIC / "crystal-builder.css").read_text()


# ── shared helpers ────────────────────────────────────────────────────────────

def _set_result(widget: anywidget.AnyWidget, atoms: Any, exc: Exception | None) -> None:
    """Update n_atoms / error traitlets from a build result."""
    if exc is not None:
        widget.set_trait("error", str(exc))
        widget.set_trait("n_atoms", 0)
    else:
        widget.set_trait("error", "")
        widget.set_trait("n_atoms", len(atoms))


# ── BulkBuilderWidget ─────────────────────────────────────────────────────────

class BulkBuilderWidget(anywidget.AnyWidget):
    """Build a bulk crystal structure with ``ase.build.bulk``.

    Parameters
    ----------
    symbol:
        Chemical symbol or compound formula understood by ASE
        (e.g. ``"Cu"``, ``"NaCl"``).
    crystalstructure:
        Crystal structure type: ``"fcc"``, ``"bcc"``, ``"hcp"``,
        ``"diamond"``, ``"zincblende"``, ``"rocksalt"``,
        ``"cesiumchloride"``, ``"fluorite"``, ``"wurtzite"``.
        Leave empty (default) to let ASE auto-detect from the symbol.
    cubic:
        Request a cubic unit cell.
    supercell:
        Repeat the primitive cell along each lattice vector – a list of
        three positive integers ``[na, nb, nc]``.

    Read-back traitlets (also in ``widget.value``):
        error   – empty on success, error message on failure.
        n_atoms – atom count of the built structure, 0 on failure.

    The built ``ase.Atoms`` object is available via the ``atoms`` property.
    """

    _esm = _STATIC / "bulk-builder.js"
    _css = _CSS

    symbol: str = traitlets.Unicode("Cu").tag(sync=True)
    crystalstructure: str = traitlets.Unicode("fcc").tag(sync=True)
    cubic: bool = traitlets.Bool(False).tag(sync=True)
    supercell: list = traitlets.List(traitlets.Int(), [1, 1, 1]).tag(sync=True)
    # Lattice constants – 0.0 means "let ASE use its database default"
    a: float = traitlets.Float(0.0).tag(sync=True)
    b: float = traitlets.Float(0.0).tag(sync=True)
    c: float = traitlets.Float(0.0).tag(sync=True)
    covera: float = traitlets.Float(0.0).tag(sync=True)
    error: str = traitlets.Unicode("").tag(sync=True)
    n_atoms: int = traitlets.Int(0).tag(sync=True)

    def __init__(self, **kwargs: Any) -> None:
        self._atoms: Any = None
        super().__init__(**kwargs)
        if self._atoms is None:
            self._build()

    @traitlets.observe("symbol", "crystalstructure", "cubic", "supercell",
                       "a", "b", "c", "covera")
    def _on_change(self, _change: dict) -> None:
        self._build()

    def _build(self) -> None:
        try:
            from ase.build import bulk

            kw: dict[str, Any] = {}
            if self.crystalstructure:
                kw["crystalstructure"] = self.crystalstructure
            if self.cubic:
                kw["cubic"] = True
            if self.a > 0:
                kw["a"] = self.a
            if self.b > 0:
                kw["b"] = self.b
            if self.c > 0:
                kw["c"] = self.c
            if self.covera > 0:
                kw["covera"] = self.covera

            atoms = bulk(self.symbol, **kw)

            sc = self.supercell
            if sc != [1, 1, 1]:
                atoms = atoms.repeat(sc)

            self._atoms = atoms
            _set_result(self, atoms, None)
        except Exception as exc:
            self._atoms = None
            _set_result(self, None, exc)

    @property
    def atoms(self) -> Any:
        """The built ``ase.Atoms`` object, or ``None`` if the build failed."""
        return self._atoms


# ── SurfaceBuilderWidget ──────────────────────────────────────────────────────

# Facets that only support orthogonal cells (orthogonal=False raises an error)
_ORTHOGONAL_ONLY = {"fcc100", "fcc110", "bcc100", "hcp10m10"}

# Maps facet name → the corresponding ase.build function name
_FACET_FUNCS = {
    "fcc111": "fcc111",
    "fcc100": "fcc100",
    "fcc110": "fcc110",
    "fcc211": "fcc211",
    "bcc100": "bcc100",
    "bcc110": "bcc110",
    "bcc111": "bcc111",
    "hcp0001": "hcp0001",
    "hcp10m10": "hcp10m10",
}


class SurfaceBuilderWidget(anywidget.AnyWidget):
    """Build a surface slab with ASE's facet-specific builders.

    Parameters
    ----------
    symbol:
        Chemical symbol (e.g. ``"Cu"``).
    facet:
        Surface facet.  Supported values: ``fcc111``, ``fcc100``,
        ``fcc110``, ``fcc211``, ``bcc100``, ``bcc110``, ``bcc111``,
        ``hcp0001``, ``hcp10m10``.
    layers:
        Number of atomic layers.
    vacuum:
        Vacuum thickness in Å added above and below the slab.
    supercell_a:
        Repeat the slab along the first surface lattice vector.
    supercell_b:
        Repeat the slab along the second surface lattice vector.
    orthogonal:
        Request an orthogonal unit cell (not supported by all facets).
    a:
        In-plane lattice constant in Å.  ``0.0`` → ASE database default.
    c:
        Out-of-plane lattice constant in Å (HCP facets only).
        ``0.0`` → ASE database default.

    Read-back traitlets:
        error, n_atoms  (see :class:`BulkBuilderWidget`).
    """

    _esm = _STATIC / "surface-builder.js"
    _css = _CSS

    symbol: str = traitlets.Unicode("Cu").tag(sync=True)
    facet: str = traitlets.Unicode("fcc111").tag(sync=True)
    layers: int = traitlets.Int(4).tag(sync=True)
    vacuum: float = traitlets.Float(10.0).tag(sync=True)
    supercell_a: int = traitlets.Int(1).tag(sync=True)
    supercell_b: int = traitlets.Int(1).tag(sync=True)
    orthogonal: bool = traitlets.Bool(False).tag(sync=True)
    # Lattice constants – 0.0 means "let ASE use its database default"
    a: float = traitlets.Float(0.0).tag(sync=True)
    c: float = traitlets.Float(0.0).tag(sync=True)
    error: str = traitlets.Unicode("").tag(sync=True)
    n_atoms: int = traitlets.Int(0).tag(sync=True)

    def __init__(self, **kwargs: Any) -> None:
        self._atoms: Any = None
        super().__init__(**kwargs)
        if self._atoms is None:
            self._build()

    @traitlets.observe(
        "symbol", "facet", "layers", "vacuum",
        "supercell_a", "supercell_b", "orthogonal", "a", "c",
    )
    def _on_change(self, _change: dict) -> None:
        self._build()

    def _build(self) -> None:
        try:
            import ase.build as ab

            func_name = _FACET_FUNCS.get(self.facet)
            if func_name is None:
                raise ValueError(f"Unknown facet: {self.facet!r}")

            builder = getattr(ab, func_name)
            size = (self.supercell_a, self.supercell_b, self.layers)

            kw: dict[str, Any] = {"vacuum": self.vacuum}
            if self.a > 0:
                kw["a"] = self.a
            if self.c > 0 and self.facet in ("hcp0001", "hcp10m10"):
                kw["c"] = self.c
            # fcc211 takes no orthogonal kwarg; others in _ORTHOGONAL_ONLY only
            # support orthogonal=True, so we skip the kwarg for those too.
            if self.facet not in _ORTHOGONAL_ONLY and self.facet != "fcc211":
                kw["orthogonal"] = self.orthogonal

            atoms = builder(self.symbol, size, **kw)
            self._atoms = atoms
            _set_result(self, atoms, None)
        except Exception as exc:
            self._atoms = None
            _set_result(self, None, exc)

    @property
    def atoms(self) -> Any:
        """The built ``ase.Atoms`` object, or ``None`` if the build failed."""
        return self._atoms


# ── NanoparticleBuilderWidget ─────────────────────────────────────────────────

class NanoparticleBuilderWidget(anywidget.AnyWidget):
    """Build a nanoparticle with ``ase.cluster``.

    Three shapes are supported, each with its own parameters:

    **Icosahedron** (``shape="Icosahedron"``)
        ``noshells`` – number of complete shells.

    **Decahedron** (``shape="Decahedron"``)
        ``p`` – number of atoms on the fivefold axis edges.
        ``q`` – number of atoms on the outer (100) facets.
        ``r`` – number of (111) twin-plane layers (0 for no twins).

    **Octahedron** (``shape="Octahedron"``)
        ``oct_length`` – number of atoms along an edge.
        ``cutoff`` – number of corner layers to remove (0 → full octahedron).

    Parameters
    ----------
    symbol:
        Chemical symbol (e.g. ``"Au"``).
    shape:
        ``"Icosahedron"``, ``"Decahedron"``, or ``"Octahedron"``.

    Read-back traitlets:
        error, n_atoms  (see :class:`BulkBuilderWidget`).
    """

    _esm = _STATIC / "nanoparticle-builder.js"
    _css = _CSS

    symbol: str = traitlets.Unicode("Au").tag(sync=True)
    shape: str = traitlets.Unicode("Icosahedron").tag(sync=True)
    # Icosahedron
    noshells: int = traitlets.Int(3).tag(sync=True)
    # Decahedron
    p: int = traitlets.Int(3).tag(sync=True)
    q: int = traitlets.Int(2).tag(sync=True)
    r: int = traitlets.Int(0).tag(sync=True)
    # Octahedron  (named oct_length to avoid shadowing builtins)
    oct_length: int = traitlets.Int(3).tag(sync=True)
    cutoff: int = traitlets.Int(0).tag(sync=True)
    # Lattice constant – 0.0 means "let ASE use its database default"
    latticeconstant: float = traitlets.Float(0.0).tag(sync=True)
    # status
    error: str = traitlets.Unicode("").tag(sync=True)
    n_atoms: int = traitlets.Int(0).tag(sync=True)

    def __init__(self, **kwargs: Any) -> None:
        self._atoms: Any = None
        super().__init__(**kwargs)
        if self._atoms is None:
            self._build()

    @traitlets.observe(
        "symbol", "shape",
        "noshells", "p", "q", "r",
        "oct_length", "cutoff", "latticeconstant",
    )
    def _on_change(self, _change: dict) -> None:
        self._build()

    def _build(self) -> None:
        try:
            from ase.cluster import Decahedron, Icosahedron, Octahedron

            lc = self.latticeconstant if self.latticeconstant > 0 else None

            if self.shape == "Icosahedron":
                atoms = Icosahedron(self.symbol, self.noshells, latticeconstant=lc)
            elif self.shape == "Decahedron":
                atoms = Decahedron(self.symbol, self.p, self.q, self.r, latticeconstant=lc)
            elif self.shape == "Octahedron":
                atoms = Octahedron(self.symbol, self.oct_length, self.cutoff, latticeconstant=lc)
            else:
                raise ValueError(f"Unknown shape: {self.shape!r}")

            self._atoms = atoms
            _set_result(self, atoms, None)
        except Exception as exc:
            self._atoms = None
            _set_result(self, None, exc)

    @property
    def atoms(self) -> Any:
        """The built ``ase.Atoms`` object, or ``None`` if the build failed."""
        return self._atoms


# ── MoleculeBuilderWidget ─────────────────────────────────────────────────────

class MoleculeBuilderWidget(anywidget.AnyWidget):
    """Build a gas-phase molecule with ``ase.build.molecule``.

    Molecule names come from ASE's G2 database (e.g. ``"H2O"``, ``"CO2"``,
    ``"CH4"``, ``"C6H6"``).  See
    ``sorted(ase.collections.g2.names)`` for the full list.

    Parameters
    ----------
    name:
        Molecule name as understood by ``ase.build.molecule``.
    vacuum:
        Vacuum padding in Å added around the molecule.

    Read-back traitlets:
        error, n_atoms  (see :class:`BulkBuilderWidget`).
    """

    _esm = _STATIC / "molecule-builder.js"
    _css = _CSS

    name: str = traitlets.Unicode("H2O").tag(sync=True)
    vacuum: float = traitlets.Float(5.0).tag(sync=True)
    error: str = traitlets.Unicode("").tag(sync=True)
    n_atoms: int = traitlets.Int(0).tag(sync=True)

    def __init__(self, **kwargs: Any) -> None:
        self._atoms: Any = None
        super().__init__(**kwargs)
        if self._atoms is None:
            self._build()

    @traitlets.observe("name", "vacuum")
    def _on_change(self, _change: dict) -> None:
        self._build()

    def _build(self) -> None:
        try:
            from ase.build import molecule

            atoms = molecule(self.name, vacuum=self.vacuum)
            self._atoms = atoms
            _set_result(self, atoms, None)
        except Exception as exc:
            self._atoms = None
            _set_result(self, None, exc)

    @property
    def atoms(self) -> Any:
        """The built ``ase.Atoms`` object, or ``None`` if the build failed."""
        return self._atoms
