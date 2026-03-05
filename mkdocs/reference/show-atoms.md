# show_atoms API

::: marimo_materials.atoms_view.show_atoms

## Usage

Display a compact summary card for any `ase.Atoms` object:

```python
import marimo as mo
from ase.build import bulk
from marimo_materials import show_atoms

atoms = bulk("Fe", "bcc", a=2.87, cubic=True)
show_atoms(atoms, mo)
```

The card shows the chemical formula, lattice parameters (a, b, c, α, β, γ), periodic boundary conditions, and a per-species atom-count table.

Pass an optional title (defaults to the chemical formula):

```python
show_atoms(atoms, mo, title="Iron BCC (2×2×2)")
```
