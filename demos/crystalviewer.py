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
    # Style controls that feed into the CrystalViewer constructor.
    # Changing a dropdown recreates the viewer with the new style – this is the
    # safe pattern because we never write to weas traitlets after init.
    model_style_ctrl = mo.ui.dropdown(
        options={"Ball": 0, "Ball+Stick": 1, "Polyhedra": 2, "Stick": 3, "Line": 4},
        value="Polyhedra",
        label="Model style",
    )
    color_type_ctrl = mo.ui.dropdown(
        options=["JMOL", "VESTA", "CPK"],
        value="VESTA",
        label="Colour scheme",
    )
    show_bonded_ctrl = mo.ui.checkbox(True, label="Show bonded atoms")
    return color_type_ctrl, model_style_ctrl, show_bonded_ctrl


@app.cell
def _(color_type_ctrl, model_style_ctrl, show_bonded_ctrl):
    from marimo_materials import CrystalViewer

    cv = CrystalViewer(
        model_style=model_style_ctrl.value,
        color_type=color_type_ctrl.value,
        show_bonded_atoms=show_bonded_ctrl.value,
        width="100%",
        height="520px",
        show_gui=False,
    )
    cv.load_example("tio2.cif")
    # Slightly extend boundary for a nicer crystal view
    cv.weas.boundary = [[-0.1, 1.1], [-0.1, 1.1], [-0.1, 1.1]]
    return (cv,)


@app.cell
def _(color_type_ctrl, mo, model_style_ctrl, show_bonded_ctrl):
    mo.hstack(
        [model_style_ctrl, color_type_ctrl, show_bonded_ctrl],
        justify="start",
        gap=1,
    )
    return


@app.cell
def _(cv):
    cv.weas
    return


if __name__ == "__main__":
    app.run()
