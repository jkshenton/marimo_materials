# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.18.0",
#     "marimo_materials[crystal]",
# ]
#
# [tool.uv.sources]
# marimo_materials = { path = ".." }
# ///

import marimo

__generated_with = "0.18.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    from marimo_materials import CrystalViewer

    cv = CrystalViewer(
        model_style=2,
        color_type="VESTA",
        show_bonded_atoms=True,
        boundary=[[-0.1, 1.1], [-0.1, 1.1], [-0.1, 1.1]],
        width="100%",
        height="520px",
    )
    cv.load_example("tio2.cif")
    return (cv,)


@app.cell
def _(cv, mo):
    mo.ui.anywidget(cv.panel())
    return


@app.cell
def _(cv):
    cv.weas
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
