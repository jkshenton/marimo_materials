import marimo

__generated_with = "0.20.2"
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
def _(color_type_ctrl, mo, model_style_ctrl, show_bonded_ctrl):
    from marimo_materials import CrystalViewer

    cv = CrystalViewer(
        model_style=model_style_ctrl.value,
        color_type=color_type_ctrl.value,
        show_bonded_atoms=show_bonded_ctrl.value,
        width="100%",
        height="520px",
        show_gui=False,   # weas built-in GUI hidden – our controls handle style
    )
    cv.load_example("tio2.cif")
    # Slightly extend boundary for a nicer crystal view
    cv.weas.avr.boundary = [[-0.1, 1.1], [-0.1, 1.1], [-0.1, 1.1]]

    # Wrap only the thin state widget in mo.ui.anywidget so marimo can react to
    # interactive changes (selection, camera).  The 3D canvas itself is rendered
    # below as a plain cell expression – NOT wrapped in mo.ui.anywidget – to
    # avoid the weas JS feedback-loop recursion.
    state = mo.ui.anywidget(cv.state_widget)
    return cv, state


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
    # Display the 3D crystal viewer as a plain cell output.
    # Do NOT wrap in mo.ui.anywidget() – that would reintroduce the infinite
    # JS recursion via the weas viewerUpdated → change:modelStyle loop.
    cv.base_widget
    return


@app.cell
def _(state):
    # Invisible placeholder – just keeps cv.state_widget in the reactive graph
    # so downstream cells re-run whenever selection/camera state changes.
    state
    return


@app.cell
def _(mo, state):
    _sel = state.value.get("selected_atoms", [])
    _pos = [round(x, 2) for x in (state.value.get("camera_position") or [])]
    _zoom = round(state.value.get("camera_zoom") or 1.0, 3)
    _style = state.value.get("model_style", "?")
    _color = state.value.get("color_type", "?")
    mo.md(f"""
    ### Live state

    | Key | Value |
    |-----|-------|
    | **Selected atoms** | {_sel if _sel else "_click an atom to select_"} |
    | **Camera position** | `{_pos}` |
    | **Camera zoom** | `{_zoom}` |
    | **Model style** | `{_style}` |
    | **Colour type** | `{_color}` |
    """)
    return


@app.cell
def _(cv, mo, state):
    _sel = state.value.get("selected_atoms", [])
    if _sel:
        _atoms = cv.to_ase()
        _rows = [
            f"| {i} | {_atoms[i].symbol} | {_atoms[i].position.round(3).tolist()} |"
            for i in _sel
        ]
        _detail = (
            "### Selected atom details\n\n"
            "| Index | Element | Position (Å) |\n"
            "|-------|---------|-------------|\n"
            + "\n".join(_rows)
        )
    else:
        _detail = "_Click one or more atoms in the viewer above to inspect them._"
    mo.md(_detail)
    return


if __name__ == "__main__":
    app.run()
