"""Crystal structure download widget for marimo notebooks.

Provides :class:`CrystalDownloadWidget`, an anywidget that serialises an
``ase.Atoms`` object to a chosen file format and triggers a browser download.

Usage::

    from marimo_materials import CrystalDownloadWidget
    from ase.build import bulk
    import marimo as mo

    atoms = bulk("Cu", "fcc", a=3.61)
    dl_w = mo.ui.anywidget(CrystalDownloadWidget(atoms))
    dl_w

The user selects a format from the dropdown and clicks **Download**; the
browser saves the file directly.  The ``format`` traitlet (default ``"cif"``)
is synced both ways, so you can also pre-select a format in Python::

    dl_w = mo.ui.anywidget(CrystalDownloadWidget(atoms, format="vasp"))

Supported formats: ``cif``, ``vasp`` (POSCAR), ``xyz``, ``extxyz``,
``json`` (ASE JSON), ``lammps-data``, ``pdb``.

Additional keyword arguments accepted by ``ase.io.write`` can be passed as
``write_kwargs`` to the constructor and are forwarded transparently::

    dl_w = mo.ui.anywidget(
        CrystalDownloadWidget(atoms, format="vasp", write_kwargs={"sort": True})
    )
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import anywidget
import traitlets

_STATIC = Path(__file__).parent / "static"

# Maps format key → default filename
_FILENAME_MAP: dict[str, str] = {
    "cif":         "{formula}.cif",
    "vasp":        "POSCAR",
    "xyz":         "{formula}.xyz",
    "extxyz":      "{formula}.extxyz",
    "json":        "{formula}.json",
    "lammps-data": "{formula}.lammps",
    "proteindatabank": "{formula}.pdb",
}


class CrystalDownloadWidget(anywidget.AnyWidget):
    """Download an ASE Atoms structure as a file in the browser.

    Parameters
    ----------
    atoms:
        An ``ase.Atoms`` object to serialise.  Can also be set later via
        :meth:`set_atoms`.
    format:
        Output file format understood by ``ase.io.write``.  Defaults to
        ``"cif"``.  The user can also change it interactively via the
        dropdown.
    write_kwargs:
        Extra keyword arguments forwarded verbatim to ``ase.io.write``
        (e.g. ``{"sort": True}`` for the VASP writer).

    Synced traitlets (readable via ``widget.value``):
        format      – currently selected format string.
        formula     – chemical formula of the loaded atoms (empty if none).
        n_atoms     – atom count (0 if no atoms set).
        filename    – filename that will be used for the download.
        file_content – serialised file content (updated on each format change).
        error       – empty on success, error message on failure.
    """

    _esm = _STATIC / "crystal-download.js"
    _css = _STATIC / "crystal-download.css"

    # User-selectable (bidirectional)
    format: str = traitlets.Unicode("cif").tag(sync=True)

    # Atom info (Python → JS, display only)
    formula: str = traitlets.Unicode("").tag(sync=True)
    n_atoms: int = traitlets.Int(0).tag(sync=True)

    # Generated file (Python → JS)
    file_content: str = traitlets.Unicode("").tag(sync=True)
    filename: str = traitlets.Unicode("structure.cif").tag(sync=True)

    # Status
    error: str = traitlets.Unicode("").tag(sync=True)

    def __init__(self, atoms: Any = None, write_kwargs: dict | None = None, **kwargs: Any) -> None:
        self._atoms: Any = None
        self._write_kwargs: dict = write_kwargs or {}
        super().__init__(**kwargs)
        if atoms is not None:
            self.set_atoms(atoms)

    # ── public API ────────────────────────────────────────────────────────────

    def set_atoms(self, atoms: Any, write_kwargs: dict | None = None) -> None:
        """Replace the current atoms object and regenerate the file content."""
        self._atoms = atoms
        if write_kwargs is not None:
            self._write_kwargs = write_kwargs
        if atoms is not None:
            self.set_trait("formula", atoms.get_chemical_formula())
            self.set_trait("n_atoms", len(atoms))
        else:
            self.set_trait("formula", "")
            self.set_trait("n_atoms", 0)
        self._generate()

    # ── internal ──────────────────────────────────────────────────────────────

    @traitlets.observe("format")
    def _on_format_change(self, _change: dict) -> None:
        self._generate()

    def _generate(self) -> None:
        if self._atoms is None:
            self.set_trait("file_content", "")
            self.set_trait("error", "")
            return
        try:
            import os
            import tempfile

            from ase.io import write

            # Write to a named temp file so ASE can do its own open() with the
            # right mode (some writers, e.g. CIF, require binary mode).
            suffix = f".{self.format.replace('-', '_')}"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as fh:
                tmp_path = fh.name
            try:
                write(tmp_path, self._atoms, format=self.format, **self._write_kwargs)
                with open(tmp_path, "r", encoding="utf-8", errors="replace") as fh:
                    content = fh.read()
            finally:
                os.unlink(tmp_path)

            self.set_trait("file_content", content)
            self.set_trait("filename", self._make_filename())
            self.set_trait("error", "")
        except Exception as exc:
            self.set_trait("file_content", "")
            self.set_trait("error", str(exc))

    def _make_filename(self) -> str:
        formula = self._atoms.get_chemical_formula() if self._atoms is not None else "structure"
        pattern = _FILENAME_MAP.get(self.format, f"{{formula}}.{self.format}")
        return pattern.format(formula=formula)
