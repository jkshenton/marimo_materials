# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.18.0",
#     "marimo_materials[crystal]==0.1.0a0",
# ]
# ///

import marimo

__generated_with = "0.18.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # Crystal Structure Builders

    Interactive widgets that build `ase.Atoms` objects from a form UI.
    There is one widget per structure type.  Each widget exposes an `.atoms`
    property (an `ase.Atoms` object) that updates whenever the form changes.
    Pass the result to `CrystalViewer.from_ase()` to view the structure in 3D.

    Requires `ase` (`pip install ase`).
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Bulk crystal
    """)
    return


@app.cell
def _(mo):
    from marimo_materials import BulkBuilderWidget

    bulk_widget = mo.ui.anywidget(BulkBuilderWidget())
    bulk_widget
    return (bulk_widget,)


@app.cell
def _(bulk_widget, mo):
    from marimo_materials import CrystalViewer as _CrystalViewer, show_atoms as _show_atoms

    _atoms = bulk_widget.widget.atoms
    _err = bulk_widget.widget.error

    if _err:
        _result = mo.callout(mo.md(f"**Build error:** {_err}"), kind="danger")
    elif _atoms is None or len(_atoms) == 0:
        _result = mo.md("_Configure the form above._")
    else:
        _cv = _CrystalViewer(height="400px")
        _cv.from_ase(_atoms)
        _result = mo.vstack([_show_atoms(_atoms, mo), _cv.weas])
    _result
    return


@app.cell
def _(mo):
    mo.md("""
    ## Surface slab
    """)
    return


@app.cell
def _(mo):
    from marimo_materials import SurfaceBuilderWidget

    surface_widget = mo.ui.anywidget(SurfaceBuilderWidget())
    surface_widget
    return (surface_widget,)


@app.cell
def _(mo, surface_widget):
    from marimo_materials import CrystalViewer as _CrystalViewer, show_atoms as _show_atoms

    _atoms = surface_widget.widget.atoms
    _err = surface_widget.widget.error

    if _err:
        _result = mo.callout(mo.md(f"**Build error:** {_err}"), kind="danger")
    elif _atoms is None or len(_atoms) == 0:
        _result = mo.md("_Configure the form above._")
    else:
        _cv = _CrystalViewer(height="400px")
        _cv.from_ase(_atoms)
        _result = mo.vstack([_show_atoms(_atoms, mo), _cv.weas])
    _result
    return


@app.cell
def _(mo):
    mo.md("""
    ## Nanoparticle
    """)
    return


@app.cell
def _(mo):
    from marimo_materials import NanoparticleBuilderWidget

    nano_widget = mo.ui.anywidget(NanoparticleBuilderWidget())
    nano_widget
    return (nano_widget,)


@app.cell
def _(mo, nano_widget):
    from marimo_materials import CrystalViewer as _CrystalViewer, show_atoms as _show_atoms

    _atoms = nano_widget.widget.atoms
    _err = nano_widget.widget.error

    if _err:
        _result = mo.callout(mo.md(f"**Build error:** {_err}"), kind="danger")
    elif _atoms is None or len(_atoms) == 0:
        _result = mo.md("_Configure the form above._")
    else:
        _cv = _CrystalViewer(height="400px")
        _cv.from_ase(_atoms)
        _result = mo.vstack([_show_atoms(_atoms, mo), _cv.weas])
    _result
    return


@app.cell
def _(mo):
    mo.md("""
    ## Molecule
    """)
    return


@app.cell
def _(mo):
    from marimo_materials import MoleculeBuilderWidget

    mol_widget = mo.ui.anywidget(MoleculeBuilderWidget())
    mol_widget
    return (mol_widget,)


@app.cell
def _(mo, mol_widget):
    from marimo_materials import CrystalViewer as _CrystalViewer, show_atoms as _show_atoms

    _atoms = mol_widget.widget.atoms
    _err = mol_widget.widget.error

    if _err:
        _result = mo.callout(mo.md(f"**Build error:** {_err}"), kind="danger")
    elif _atoms is None or len(_atoms) == 0:
        _result = mo.md("_Configure the form above._")
    else:
        _cv = _CrystalViewer(height="400px")
        _cv.from_ase(_atoms)
        _result = mo.vstack([_show_atoms(_atoms, mo), _cv.weas])
    _result
    return


if __name__ == "__main__":
    app.run()
