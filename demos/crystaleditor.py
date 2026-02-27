import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # Crystal Structure Editor

    Edit an `ase.Atoms` object interactively.  The editor provides three panels:

    * **Sites** – edit per-atom element symbols and Cartesian coordinates; add or delete atoms.
    * **Unit cell** – adjust lattice parameters (a, b, c, α, β, γ) and periodic boundary flags.
    * **Operations** – one-click buttons for `wrap`, `center`, `repeat`, `translate`, `scale cell`, and `sort`.

    All changes require an explicit button click — nothing is applied automatically.
    """)
    return


@app.cell
def _(mo):
    from marimo_materials import CrystalEditorWidget
    from ase.build import bulk

    _atoms = bulk("Cu", "fcc", a=3.61) * (2, 2, 2)
    editor = CrystalEditorWidget(_atoms)
    widget = mo.ui.anywidget(editor)
    widget
    return editor, widget


@app.cell
def _(editor, mo, widget):
    from marimo_materials import show_atoms

    _error = widget.value.get("error", "")
    atoms = editor.atoms

    if _error:
        _result = mo.callout(
            mo.md(f"**Edit error**\n\n```\n{_error}\n```"),
            kind="danger",
        )
    elif atoms is None:
        _result = mo.md("_Load a structure to begin editing._")
    else:
        _result = show_atoms(atoms, mo)
    _result
    return


if __name__ == "__main__":
    app.run()
