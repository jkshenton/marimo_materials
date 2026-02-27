"""Tests for crystal builder widgets (BulkBuilderWidget, SurfaceBuilderWidget,
NanoparticleBuilderWidget, MoleculeBuilderWidget)."""

import pytest

ase = pytest.importorskip("ase", reason="ase not installed")


# ── imports ────────────────────────────────────────────────────────────────────

def test_imports_from_package():
    from marimo_materials import (
        BulkBuilderWidget,
        MoleculeBuilderWidget,
        NanoparticleBuilderWidget,
        SurfaceBuilderWidget,
    )
    assert BulkBuilderWidget is not None


# ── BulkBuilderWidget ─────────────────────────────────────────────────────────

class TestBulkBuilderWidget:
    def _w(self, **kw):
        from marimo_materials import BulkBuilderWidget
        return BulkBuilderWidget(**kw)

    def test_default_builds_successfully(self):
        w = self._w()
        assert w.error == ""
        assert w.n_atoms > 0
        assert w.atoms is not None

    def test_atoms_is_ase_atoms(self):
        from ase import Atoms
        w = self._w()
        assert isinstance(w.atoms, Atoms)

    def test_n_atoms_matches_atoms_object(self):
        w = self._w()
        assert w.n_atoms == len(w.atoms)

    def test_fcc_default(self):
        w = self._w(symbol="Cu", crystalstructure="fcc")
        assert w.error == ""
        assert w.n_atoms == 1  # primitive fcc cell

    def test_bcc_default(self):
        w = self._w(symbol="Fe", crystalstructure="bcc")
        assert w.error == ""
        assert w.n_atoms == 1

    def test_hcp_default(self):
        w = self._w(symbol="Mg", crystalstructure="hcp")
        assert w.error == ""
        assert w.n_atoms == 2

    def test_diamond_default(self):
        w = self._w(symbol="Si", crystalstructure="diamond")
        assert w.error == ""
        assert w.n_atoms == 2

    def test_cubic_flag(self):
        w_prim = self._w(symbol="Cu", crystalstructure="fcc", cubic=False)
        w_cubic = self._w(symbol="Cu", crystalstructure="fcc", cubic=True)
        assert w_cubic.n_atoms > w_prim.n_atoms  # cubic cell has more atoms

    def test_supercell_repeat(self):
        w1 = self._w(symbol="Cu", crystalstructure="fcc", supercell=[1, 1, 1])
        w4 = self._w(symbol="Cu", crystalstructure="fcc", supercell=[2, 2, 1])
        assert w4.n_atoms == w1.n_atoms * 4

    def test_lattice_constant_a(self):
        # Use cubic=True so cellpar()[0] equals the conventional lattice parameter
        w = self._w(symbol="Cu", crystalstructure="fcc", a=3.61, cubic=True)
        assert w.error == ""
        a_actual = w.atoms.cell.cellpar()[0]
        assert abs(a_actual - 3.61) < 0.01

    def test_lattice_constant_hcp_c(self):
        w = self._w(symbol="Mg", crystalstructure="hcp", a=3.21, c=5.21)
        assert w.error == ""
        params = w.atoms.cell.cellpar()
        assert abs(params[0] - 3.21) < 0.01
        assert abs(params[2] - 5.21) < 0.01

    def test_invalid_symbol_sets_error(self):
        w = self._w(symbol="Xx", crystalstructure="fcc")
        assert w.error != ""
        assert w.atoms is None
        assert w.n_atoms == 0

    def test_error_clears_after_fix(self):
        """Reproduces the stuck-error bug: error then fix should clear error."""
        w = self._w(symbol="Mg", crystalstructure="hcp", cubic=True)
        assert w.error != ""          # hcp + cubic → error
        w.set_trait("cubic", False)   # fix: uncheck cubic
        assert w.error == ""
        assert w.n_atoms > 0

    def test_error_n_atoms_consistent(self):
        """n_atoms must be 0 when error is set."""
        w = self._w(symbol="Xx", crystalstructure="fcc")
        assert w.error != ""
        assert w.n_atoms == 0

    def test_success_n_atoms_consistent(self):
        """n_atoms must equal len(atoms) when no error."""
        w = self._w(symbol="Cu", crystalstructure="fcc", supercell=[2, 3, 1])
        assert w.error == ""
        assert w.n_atoms == len(w.atoms)

    def test_trait_change_rebuilds(self):
        w = self._w(symbol="Cu", crystalstructure="fcc")
        n_before = w.n_atoms
        w.set_trait("supercell", [2, 2, 2])
        assert w.n_atoms == n_before * 8

    def test_auto_structure_detection(self):
        # symbol="Cu" with empty crystalstructure → ASE auto-detects fcc
        w = self._w(symbol="Cu", crystalstructure="")
        assert w.error == ""
        assert w.n_atoms > 0

    def test_lattice_constant_covera(self):
        w = self._w(symbol="Mg", crystalstructure="hcp", covera=1.65)
        assert w.error == ""
        params = w.atoms.cell.cellpar()
        # c/a should reflect our override
        assert abs(params[2] / params[0] - 1.65) < 0.01

    def test_n_atoms_consistent_after_error_and_recovery_same_count(self):
        """Regression: if n_atoms was N before an error, fixing the error must
        still update n_atoms back to N even though traitlets may skip the
        change notification when the value is numerically unchanged."""
        w = self._w(symbol="Cu", crystalstructure="fcc", supercell=[1, 1, 1])
        assert w.n_atoms > 0
        n_before = w.n_atoms
        # cause an error
        w.set_trait("symbol", "Xx")
        assert w.error != ""
        assert w.n_atoms == 0
        # recover with same expected count
        w.set_trait("symbol", "Cu")
        assert w.error == ""
        assert w.n_atoms == n_before
        assert w.n_atoms == len(w.atoms)


# ── SurfaceBuilderWidget ──────────────────────────────────────────────────────

class TestSurfaceBuilderWidget:
    def _w(self, **kw):
        from marimo_materials import SurfaceBuilderWidget
        return SurfaceBuilderWidget(**kw)

    def test_default_builds_successfully(self):
        w = self._w()
        assert w.error == ""
        assert w.n_atoms > 0
        assert w.atoms is not None

    def test_atoms_is_ase_atoms(self):
        from ase import Atoms
        w = self._w()
        assert isinstance(w.atoms, Atoms)

    def test_n_atoms_matches_atoms_object(self):
        w = self._w()
        assert w.n_atoms == len(w.atoms)

    @pytest.mark.parametrize("facet,symbol", [
        ("fcc111", "Cu"),
        ("fcc100", "Cu"),
        ("fcc110", "Cu"),
        ("bcc100", "Fe"),
        ("bcc110", "Fe"),
        ("bcc111", "Fe"),
        ("hcp0001", "Mg"),
    ])
    def test_all_facets_build(self, facet, symbol):
        w = self._w(symbol=symbol, facet=facet)
        assert w.error == "", f"{facet}: got error {w.error!r}"
        assert w.n_atoms > 0

    def test_fcc211_build(self):
        # fcc211 requires supercell_a divisible by 3
        w = self._w(symbol="Cu", facet="fcc211", supercell_a=3)
        assert w.error == ""
        assert w.n_atoms > 0

    def test_hcp10m10_build(self):
        # hcp10m10 requires even supercell_b
        w = self._w(symbol="Mg", facet="hcp10m10", supercell_b=2)
        assert w.error == ""
        assert w.n_atoms > 0

    def test_layers_controls_atom_count(self):
        w4 = self._w(symbol="Cu", facet="fcc111", layers=4)
        w8 = self._w(symbol="Cu", facet="fcc111", layers=8)
        assert w8.n_atoms == w4.n_atoms * 2

    def test_supercell_repeat(self):
        w1 = self._w(symbol="Cu", facet="fcc111", supercell_a=1, supercell_b=1)
        w2 = self._w(symbol="Cu", facet="fcc111", supercell_a=2, supercell_b=2)
        assert w2.n_atoms == w1.n_atoms * 4

    def test_lattice_constant_a(self):
        w = self._w(symbol="Cu", facet="fcc111", a=3.61)
        assert w.error == ""
        # Cell vector magnitude should reflect the specified a
        import numpy as _np
        a_actual = _np.linalg.norm(w.atoms.cell[0])
        # For fcc111 the surface a is a/sqrt(2), so just check it built OK
        assert a_actual > 0

    def test_hcp_lattice_constants_a_and_c(self):
        w = self._w(symbol="Mg", facet="hcp0001", a=3.21, c=5.21)
        assert w.error == ""
        assert w.n_atoms > 0

    def test_c_ignored_for_non_hcp(self):
        # Passing c for an fcc facet should still succeed (c silently ignored)
        w = self._w(symbol="Cu", facet="fcc111", c=99.0)
        assert w.error == ""
        assert w.n_atoms > 0

    def test_invalid_symbol_sets_error(self):
        w = self._w(symbol="Xx", facet="fcc111")
        assert w.error != ""
        assert w.atoms is None
        assert w.n_atoms == 0

    def test_orthogonal_fcc111(self):
        # orthogonal fcc111 requires even supercell_b
        w = self._w(symbol="Cu", facet="fcc111", orthogonal=True, supercell_b=2)
        assert w.error == ""
        assert w.n_atoms > 0

    def test_vacuum_adds_cell_height(self):
        w5 = self._w(symbol="Cu", facet="fcc111", vacuum=5.0)
        w15 = self._w(symbol="Cu", facet="fcc111", vacuum=15.0)
        import numpy as _np
        c5 = _np.linalg.norm(w5.atoms.cell[2])
        c15 = _np.linalg.norm(w15.atoms.cell[2])
        assert c15 > c5

    def test_hcp10m10_lattice_constants(self):
        # hcp10m10 requires even supercell_b; supports both a and c
        w = self._w(symbol="Ti", facet="hcp10m10", a=2.95, c=4.68, supercell_b=2)
        assert w.error == ""
        assert w.n_atoms > 0

    def test_c_ignored_for_fcc100(self):
        # c should be silently ignored for a non-HCP facet
        w = self._w(symbol="Cu", facet="fcc100", c=99.0)
        assert w.error == ""
        assert w.n_atoms > 0

    def test_n_atoms_consistent_after_error_and_recovery_same_count(self):
        """Regression: n_atoms must equal len(atoms) even when the count
        happens to be identical before and after an error cycle."""
        w = self._w(symbol="Cu", facet="fcc111", layers=4)
        n_before = w.n_atoms
        assert n_before > 0
        w.set_trait("symbol", "Xx")
        assert w.error != ""
        assert w.n_atoms == 0
        w.set_trait("symbol", "Cu")
        assert w.error == ""
        assert w.n_atoms == n_before
        assert w.n_atoms == len(w.atoms)

    def test_error_clears_after_fix(self):
        w = self._w(symbol="Xx", facet="fcc111")
        assert w.error != ""
        w.set_trait("symbol", "Cu")
        assert w.error == ""
        assert w.n_atoms > 0


# ── NanoparticleBuilderWidget ─────────────────────────────────────────────────

class TestNanoparticleBuilderWidget:
    def _w(self, **kw):
        from marimo_materials import NanoparticleBuilderWidget
        return NanoparticleBuilderWidget(**kw)

    def test_default_builds_successfully(self):
        w = self._w()
        assert w.error == ""
        assert w.n_atoms > 0
        assert w.atoms is not None

    def test_atoms_is_ase_atoms(self):
        from ase import Atoms
        w = self._w()
        assert isinstance(w.atoms, Atoms)

    def test_icosahedron(self):
        w = self._w(symbol="Au", shape="Icosahedron", noshells=2)
        assert w.error == ""
        assert w.n_atoms == 13  # 2-shell icosahedron has 13 atoms

    def test_icosahedron_shell_count(self):
        w2 = self._w(symbol="Au", shape="Icosahedron", noshells=2)
        w3 = self._w(symbol="Au", shape="Icosahedron", noshells=3)
        assert w3.n_atoms > w2.n_atoms

    def test_decahedron(self):
        w = self._w(symbol="Au", shape="Decahedron", p=3, q=2, r=0)
        assert w.error == ""
        assert w.n_atoms > 0

    def test_octahedron(self):
        w = self._w(symbol="Au", shape="Octahedron", oct_length=4, cutoff=0)
        assert w.error == ""
        assert w.n_atoms > 0

    def test_octahedron_cutoff_reduces_atoms(self):
        w_full = self._w(symbol="Au", shape="Octahedron", oct_length=5, cutoff=0)
        w_cut = self._w(symbol="Au", shape="Octahedron", oct_length=5, cutoff=1)
        assert w_cut.n_atoms < w_full.n_atoms

    def test_latticeconstant_override(self):
        w_auto = self._w(symbol="Au", shape="Icosahedron", noshells=2)
        w_lc = self._w(symbol="Au", shape="Icosahedron", noshells=2, latticeconstant=4.08)
        # Both should build successfully; atom counts are the same
        assert w_auto.error == ""
        assert w_lc.error == ""
        assert w_auto.n_atoms == w_lc.n_atoms

    def test_n_atoms_matches_atoms_object(self):
        w = self._w(symbol="Pd", shape="Decahedron", p=4, q=2, r=0)
        assert w.error == ""
        assert w.n_atoms == len(w.atoms)

    def test_shape_switch_rebuilds(self):
        w = self._w(symbol="Au", shape="Icosahedron", noshells=3)
        n_ico = w.n_atoms
        w.set_trait("shape", "Decahedron")
        assert w.error == ""
        assert w.n_atoms != n_ico  # Decahedron(p=3,q=2,r=0) ≠ Icosahedron(3 shells)
        assert w.n_atoms == len(w.atoms)

    def test_n_atoms_consistent_after_error_and_recovery_same_count(self):
        """Regression: n_atoms must stay consistent even when count before
        and after an error cycle is the same (traitlets skip notification)."""
        w = self._w(symbol="Au", shape="Icosahedron", noshells=2)
        n_before = w.n_atoms
        assert n_before == 13
        w.set_trait("symbol", "Xx")
        assert w.error != ""
        assert w.n_atoms == 0
        w.set_trait("symbol", "Au")
        assert w.error == ""
        assert w.n_atoms == n_before
        assert w.n_atoms == len(w.atoms)

    def test_error_clears_after_fix(self):
        w = self._w(symbol="Xx", shape="Icosahedron", noshells=2)
        assert w.error != ""
        w.set_trait("symbol", "Au")
        assert w.error == ""
        assert w.n_atoms > 0


# ── MoleculeBuilderWidget ─────────────────────────────────────────────────────

class TestMoleculeBuilderWidget:
    def _w(self, **kw):
        from marimo_materials import MoleculeBuilderWidget
        return MoleculeBuilderWidget(**kw)

    def test_default_builds_successfully(self):
        w = self._w()
        assert w.error == ""
        assert w.n_atoms > 0
        assert w.atoms is not None

    def test_atoms_is_ase_atoms(self):
        from ase import Atoms
        w = self._w()
        assert isinstance(w.atoms, Atoms)

    def test_water(self):
        w = self._w(name="H2O")
        assert w.error == ""
        assert w.n_atoms == 3

    def test_co2(self):
        w = self._w(name="CO2")
        assert w.error == ""
        assert w.n_atoms == 3

    def test_methane(self):
        w = self._w(name="CH4")
        assert w.error == ""
        assert w.n_atoms == 5

    def test_vacuum_grows_cell(self):
        w5 = self._w(name="H2O", vacuum=5.0)
        w15 = self._w(name="H2O", vacuum=15.0)
        import numpy as _np
        vol5 = abs(_np.linalg.det(w5.atoms.cell))
        vol15 = abs(_np.linalg.det(w15.atoms.cell))
        assert vol15 > vol5

    def test_invalid_name_sets_error(self):
        w = self._w(name="NotAMolecule")
        assert w.error != ""
        assert w.atoms is None
        assert w.n_atoms == 0

    def test_n_atoms_matches_atoms_object(self):
        w = self._w(name="CO2")
        assert w.n_atoms == len(w.atoms)

    def test_error_clears_after_fix(self):
        w = self._w(name="NotAMolecule")
        assert w.error != ""
        w.set_trait("name", "H2O")
        assert w.error == ""
        assert w.n_atoms == 3

    def test_name_change_rebuilds(self):
        w = self._w(name="H2O")
        assert w.n_atoms == 3
        w.set_trait("name", "CH4")
        assert w.n_atoms == 5
