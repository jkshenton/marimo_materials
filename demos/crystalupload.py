# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.18.0",
#     "marimo_materials[crystal]==0.1.0a0",
# ]
# ///

import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    from marimo_materials import CrystalUploadWidget

    uploader = CrystalUploadWidget()
    widget = mo.ui.anywidget(uploader)
    widget
    return uploader, widget


@app.cell
def _(mo, uploader, widget):
    from marimo_materials import show_atoms

    _filename = widget.value.get("filename", "")
    _parse_error = widget.value.get("parse_error", "")
    _parse_warnings = widget.value.get("parse_warnings", "")
    _frames_count = widget.value.get("frames_count", 0)
    atoms = uploader.atoms

    if _parse_error:
        _result = mo.callout(
            mo.md(f"**Parse error**\n\n```\n{_parse_error}\n```"),
            kind="danger",
        )
    elif atoms is None:
        _result = mo.md("_Upload a crystal structure file above (CIF, POSCAR, XYZ, …) then press **Parse structure**._")
    else:
        _result = show_atoms(atoms, mo, title=_filename, frames_count=_frames_count)

    _warning_callout = (
        mo.callout(mo.md(f"**Parse warnings**\n\n```\n{_parse_warnings}\n```"), kind="warn")
        if _parse_warnings
        else mo.md("")
    )
    mo.vstack([_result, _warning_callout])
    return


@app.cell
def _(mo, widget):
    # Always create the button so downstream cells can depend on it.
    # Only show it once a file has been loaded.
    _has_file = bool(widget.value.get("file_content_b64", ""))
    show_raw_btn = mo.ui.button(label="Show raw file", on_click=lambda _: True)
    show_raw_btn if _has_file else mo.md("")
    return (show_raw_btn,)


@app.cell
def _(mo, show_raw_btn, widget):
    import base64
    import html

    # Do nothing until the button is clicked.
    mo.stop(not show_raw_btn.value)

    _b64 = widget.value.get("file_content_b64", "")
    _raw = base64.b64decode(_b64)

    try:
        _text = _raw.decode("utf-8")
        _content = mo.Html(
            f'<pre style="max-height:400px;overflow-y:auto;margin:0;'
            f'padding:8px;font-size:12px;line-height:1.5;">'
            f"{html.escape(_text)}</pre>"
        )
    except UnicodeDecodeError:
        _content = mo.md(
            f"_Binary file ({len(_raw):,} bytes) — cannot display as text._"
        )

    _content
    return


if __name__ == "__main__":
    app.run()
