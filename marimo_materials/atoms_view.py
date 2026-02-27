"""Standardised marimo renderer for ``ase.Atoms`` objects.

Usage::

    from marimo_materials import show_atoms
    import marimo as mo

    # In a marimo cell:
    show_atoms(atoms, mo)

    # With optional heading and trajectory info:
    show_atoms(atoms, mo, title="OUTCAR", frames_count=42)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


def show_atoms(
    atoms: Any,
    mo: Any,
    *,
    title: str | None = None,
    frames_count: int | None = None,
) -> Any:
    """Return a marimo element that renders a summary of an ``ase.Atoms`` object.

    The output has two parts:

    * A compact **summary table** (always visible) with formula, atom count,
      elements, periodicity, cell parameters, and PBC axes.
    * A collapsible **accordion** with three optional sections:

      - *Sites* – per-atom index, symbol, Cartesian coordinates (Å), and (when
        the structure is periodic) fractional coordinates.
      - *Arrays* – any extra per-atom data arrays beyond the built-in
        ``numbers`` and ``positions`` (e.g. forces, magmoms, charges).
      - *Info* – the key/value pairs stored in ``atoms.info``.

    Parameters
    ----------
    atoms:
        The structure to display.  Passing ``None`` returns a placeholder
        message rather than raising.
    mo:
        The ``marimo`` module.  Pass it as a parameter so this function works
        inside marimo's reactive cell graph without importing marimo at module
        level.
    title:
        Optional heading rendered above the summary table (e.g. a filename).
    frames_count:
        When displaying a frame from a trajectory, pass the total number of
        frames to include it in the summary.
    """
    if atoms is None:
        return mo.md("_No structure loaded._")

    import numpy as np

    # ── Summary ───────────────────────────────────────────────────────────────
    formula  = atoms.get_chemical_formula()
    n        = len(atoms)
    elements = sorted(set(atoms.get_chemical_symbols()))
    pbc      = atoms.get_pbc().tolist()
    periodic = any(pbc)
    pbc_axes = [ax for ax, p in zip("xyz", pbc) if p]

    rows = [
        f"| **Formula** | {formula} |",
        f"| **Atoms** | {n} |",
        f"| **Elements** | {', '.join(elements)} |",
        f"| **Periodic** | {'Yes' if periodic else 'No'} |",
    ]
    if periodic:
        cp = [round(v, 4) for v in atoms.cell.cellpar().tolist()]
        rows.append(f"| **PBC axes** | {', '.join(pbc_axes) if pbc_axes else '—'} |")
        rows.append(f"| **a, b, c (Å)** | {cp[0]}, {cp[1]}, {cp[2]} |")
        rows.append(f"| **α, β, γ (°)** | {cp[3]}, {cp[4]}, {cp[5]} |")
    if frames_count and frames_count > 1:
        rows.append(f"| **Frames** | {frames_count} |")

    heading  = f"### {title}\n\n" if title else ""
    table_md = "\n".join(rows)
    summary  = mo.md(f"{heading}| Property | Value |\n|---|---|\n{table_md}")

    # ── Accordion sections ────────────────────────────────────────────────────
    accordion: dict[str, Any] = {}

    # Sites ───────────────────────────────────────────────────────────────────
    positions = atoms.get_positions()
    scaled    = atoms.get_scaled_positions() if periodic else None
    site_rows = []
    for i, (sym, pos) in enumerate(zip(atoms.get_chemical_symbols(), positions)):
        row: dict[str, Any] = {
            "#":     i,
            "Symbol": sym,
            "x (Å)": round(float(pos[0]), 6),
            "y (Å)": round(float(pos[1]), 6),
            "z (Å)": round(float(pos[2]), 6),
        }
        if scaled is not None:
            row["x_frac"] = round(float(scaled[i][0]), 6)
            row["y_frac"] = round(float(scaled[i][1]), 6)
            row["z_frac"] = round(float(scaled[i][2]), 6)
        site_rows.append(row)
    accordion["Sites"] = mo.ui.table(site_rows, label="")

    # Extra arrays ────────────────────────────────────────────────────────────
    _BUILTIN = {"numbers", "positions"}
    extra = {k: v for k, v in atoms.arrays.items() if k not in _BUILTIN}
    if extra:
        syms     = atoms.get_chemical_symbols()
        arr_rows = []
        for i in range(n):
            row = {"#": i, "Symbol": syms[i]}
            for k, arr in extra.items():
                val = arr[i]
                if np.ndim(val) == 0:
                    try:
                        row[k] = round(float(val), 6)
                    except (TypeError, ValueError):
                        row[k] = str(val)
                else:
                    flat = np.asarray(val).flatten()
                    for j, v in enumerate(flat):
                        try:
                            row[f"{k}[{j}]"] = round(float(v), 6)
                        except (TypeError, ValueError):
                            row[f"{k}[{j}]"] = str(v)
            arr_rows.append(row)
        accordion["Arrays"] = mo.ui.table(arr_rows, label="")

    # Info dict ───────────────────────────────────────────────────────────────
    if getattr(atoms, "info", None):
        info_rows = [{"Key": str(k), "Value": str(v)} for k, v in atoms.info.items()]
        accordion["Info"] = mo.ui.table(info_rows, label="")

    if accordion:
        return mo.vstack([summary, mo.accordion(accordion)])
    return summary
