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
