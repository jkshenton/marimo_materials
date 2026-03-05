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

## Usage

Wrap an `ase.Atoms` object and render the editor:

```python
import marimo as mo
from ase.build import bulk
from marimo_materials import CrystalEditorWidget

atoms = bulk("Cu", "fcc", a=3.61) * (2, 2, 2)
editor = CrystalEditorWidget(atoms)
widget = mo.ui.anywidget(editor)
widget
```

Read the edited structure back in a downstream cell (reactive – re-runs whenever edits are applied):

```python
from marimo_materials import CrystalViewer, show_atoms

edited_atoms = editor.atoms
cv = CrystalViewer(height="400px")
cv.from_ase(edited_atoms)
mo.vstack([show_atoms(edited_atoms, mo), cv.weas])
```

Toggle fractional coordinates display:

```python
editor.show_fractional = True
```
