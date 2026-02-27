# CrystalEditorWidget API

::: marimo_materials.crystal_editor.CrystalEditorWidget

## Synced traitlets

| Traitlet | Type | Direction | Notes |
| --- | --- | --- | --- |
| `atoms_json` | `str` | JS → Python | JSON representation of the current atoms state. |
| `op_payload` | `str` | JS → Python | JSON payload describing a pending operation. |
| `show_fractional` | `bool` | Python ↔ JS | Display coordinates as fractional (True) or Cartesian (False). |

## Read-back property

| Property | Returns | Notes |
| --- | --- | --- |
| `atoms` | `ase.Atoms` | Current state of the edited structure. |
