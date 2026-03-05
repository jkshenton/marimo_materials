# CrystalViewer API

::: marimo_materials.crystal_viewer.CrystalViewer

## Key attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `weas` | `BaseWidget` | The underlying weas-widget `BaseWidget` – pass this to `mo.ui.anywidget()` or display it directly. |
| `_avr` | `AtomsViewer` | The weas `AtomsViewer` controller; use `model_style`, `color_type`, etc. via the `CrystalViewer` properties instead. |

## Style constants

| Constant | Value |
| --- | --- |
| `MODEL_STYLES` | `{"Ball": 0, "Ball+Stick": 1, "Polyhedra": 2, "Stick": 3, "Line": 4}` |
| `COLOR_TYPES` | `("JMOL", "VESTA", "CPK")` |

## Usage

Load a built-in example structure:

```python
import marimo as mo
from marimo_materials import CrystalViewer

cv = CrystalViewer(model_style=2, color_type="VESTA")
cv.load_example("tio2.cif")
```

Render the interactive controls panel and the 3D viewer in separate cells:

```python
# Cell 1 – controls (updates viewer live without re-running the cell)
mo.ui.anywidget(cv.panel())
```

```python
# Cell 2 – 3D viewer
cv.weas
```

Load your own `ase.Atoms` object:

```python
from ase.build import bulk

atoms = bulk("Cu", "fcc", a=3.61)
cv.from_ase(atoms)
cv.weas
```
