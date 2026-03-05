# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.18.0",
#     "marimo_materials[crystal]==0.1.0a2",
# ]
# ///

import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    from marimo_materials import CrystalDownloadWidget

    return CrystalDownloadWidget, mo


@app.cell
def _(mo):
    mo.md("""
    # Crystal Structure Download

    `CrystalDownloadWidget` serialises any `ase.Atoms` object to a chosen file
    format and triggers a browser download with a single click.

    Select a format from the dropdown and press **Download** to save the file.
    """)
    return


@app.cell
def _(mo):
    from marimo_materials import BulkBuilderWidget

    bulk_widget = mo.ui.anywidget(BulkBuilderWidget())
    bulk_widget
    return (bulk_widget,)


@app.cell
def _(CrystalDownloadWidget, bulk_widget, mo):
    _atoms = bulk_widget.widget.atoms
    if _atoms is not None:
        dl_widget = mo.ui.anywidget(CrystalDownloadWidget(_atoms))
    else:
        dl_widget = mo.md("_Build a structure above first._")
    dl_widget
    return (dl_widget,)


@app.cell
def _(mo):
    mo.md("""
    ---
    ## Standalone usage

    You can also pass any `ase.Atoms` directly, without a builder widget:
    """)
    return


@app.cell
def _(CrystalDownloadWidget, mo):
    from ase.build import bulk as _bulk

    _atoms = _bulk("Au", "fcc", a=4.08)
    static_dl = mo.ui.anywidget(CrystalDownloadWidget(_atoms, format="vasp"))
    static_dl
    return (static_dl,)


@app.cell
def _(mo):
    mo.md("""
    ## Passing write kwargs

    Extra `ase.io.write` options can be forwarded via `write_kwargs`.
    For example, to sort atoms by chemical symbol in a POSCAR file:
    """)
    return


@app.cell
def _(CrystalDownloadWidget, mo):
    from ase.build import bulk as _bulk

    _atoms = _bulk("NaCl", "rocksalt", a=5.64)
    kwargs_dl = mo.ui.anywidget(
        CrystalDownloadWidget(_atoms, format="vasp", write_kwargs={"sort": True})
    )
    kwargs_dl
    return (kwargs_dl,)


if __name__ == "__main__":
    app.run()
