"""Tests for CrystalViewer.

weas-widget is an optional dependency so we mock it entirely to keep
plain ``uv run pytest`` fast and dependency-free.
"""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers: build a minimal mock of weas_widget so the import inside
# CrystalViewer.__init__ succeeds without the real package.
# ---------------------------------------------------------------------------

def _make_avr_mock():
    """Return a fresh mock AtomsViewer instance."""
    avr = MagicMock()
    avr.model_style = 1
    avr.color_type = "JMOL"
    avr.show_bonded_atoms = False
    avr.boundary = [[-0.1, 1.1], [-0.1, 1.1], [-0.1, 1.1]]
    avr.color_by = ""
    avr.color_ramp = []
    avr.atoms = None
    return avr


def _weas_module_mock(avr_mock):
    """Inject fake weas_widget submodules into sys.modules."""
    weas_widget = ModuleType("weas_widget")
    base_widget_mod = ModuleType("weas_widget.base_widget")
    atoms_viewer_mod = ModuleType("weas_widget.atoms_viewer")
    utils_mod = ModuleType("weas_widget.utils")

    class FakeBaseWidget:
        def __init__(self, **kwargs):
            self.guiConfig = kwargs.get("guiConfig", {})
            self.viewerStyle = kwargs.get("viewerStyle", {})

    def FakeAtomsViewer(base_widget):
        return avr_mock

    fake_ase_adapter = MagicMock()
    fake_ase_adapter.to_weas = MagicMock(side_effect=lambda a: f"weas:{a}")
    fake_ase_adapter.to_ase = MagicMock(return_value="ase_atoms")

    fake_pmg_adapter = MagicMock()
    fake_pmg_adapter.to_weas = MagicMock(side_effect=lambda s: f"weas:{s}")
    fake_pmg_adapter.to_pymatgen = MagicMock(return_value="pmg_structure")

    fake_load_online_example = MagicMock(return_value="online_atoms")

    base_widget_mod.BaseWidget = FakeBaseWidget
    atoms_viewer_mod.AtomsViewer = FakeAtomsViewer
    utils_mod.ASEAdapter = fake_ase_adapter
    utils_mod.PymatgenAdapter = fake_pmg_adapter
    utils_mod.load_online_example = fake_load_online_example

    weas_widget.base_widget = base_widget_mod
    weas_widget.atoms_viewer = atoms_viewer_mod
    weas_widget.utils = utils_mod

    sys.modules["weas_widget"] = weas_widget
    sys.modules["weas_widget.base_widget"] = base_widget_mod
    sys.modules["weas_widget.atoms_viewer"] = atoms_viewer_mod
    sys.modules["weas_widget.utils"] = utils_mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clean_import():
    """Remove CrystalViewer from sys.modules before each test so patches apply fresh."""
    yield
    for key in list(sys.modules):
        if "crystal_viewer" in key:
            del sys.modules[key]


@pytest.fixture()
def avr_mock():
    return _make_avr_mock()


@pytest.fixture()
def viewer_cls(avr_mock):
    """Return (CrystalViewer, avr_mock) with weas-widget mocked out."""
    _weas_module_mock(avr_mock)
    from marimo_materials.crystal_viewer import CrystalViewer
    return CrystalViewer, avr_mock


# ---------------------------------------------------------------------------
# Class-level constants
# ---------------------------------------------------------------------------

class TestClassAttributes:
    def test_model_styles_keys(self, viewer_cls):
        CrystalViewer, _ = viewer_cls
        assert set(CrystalViewer.MODEL_STYLES) == {"Ball", "Ball+Stick", "Polyhedra", "Stick", "Line"}

    def test_model_styles_values(self, viewer_cls):
        CrystalViewer, _ = viewer_cls
        assert list(CrystalViewer.MODEL_STYLES.values()) == [0, 1, 2, 3, 4]

    def test_color_types(self, viewer_cls):
        CrystalViewer, _ = viewer_cls
        assert set(CrystalViewer.COLOR_TYPES) == {"JMOL", "VESTA", "CPK"}


# ---------------------------------------------------------------------------
# Constructor — defaults
# ---------------------------------------------------------------------------

class TestConstructorDefaults:
    def test_default_model_style(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        assert mock.model_style == 1

    def test_default_color_type(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        assert mock.color_type == "JMOL"

    def test_default_show_bonded(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        assert mock.show_bonded_atoms is False

    def test_viewer_style_set(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer(width="800px", height="600px")
        assert cv.weas.viewerStyle == {"width": "800px", "height": "600px"}

    def test_gui_hidden_by_default(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        assert cv.weas.guiConfig["controls"]["enabled"] is False
        assert cv.weas.guiConfig["buttons"]["enabled"] is False

    def test_show_gui_true(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer(show_gui=True)
        assert cv.weas.guiConfig == {}


# ---------------------------------------------------------------------------
# Constructor — custom args forwarded to _avr
# ---------------------------------------------------------------------------

class TestConstructorCustomArgs:
    def test_model_style_forwarded(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer(model_style=3)
        assert mock.model_style == 3

    def test_color_type_forwarded(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer(color_type="VESTA")
        assert mock.color_type == "VESTA"

    def test_show_bonded_forwarded(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer(show_bonded_atoms=True)
        assert mock.show_bonded_atoms is True

    def test_boundary_none_does_not_set(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        original = mock.boundary
        cv = CrystalViewer()  # boundary defaults to None
        # _avr.boundary should not have been reassigned
        assert mock.boundary is original

    def test_boundary_forwarded(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        b = [[0.0, 1.0], [0.0, 1.0], [0.0, 1.0]]
        cv = CrystalViewer(boundary=b)
        assert mock.boundary == b


# ---------------------------------------------------------------------------
# ImportError when weas-widget absent
# ---------------------------------------------------------------------------

class TestImportError:
    def test_raises_import_error_without_weas(self):
        for key in list(sys.modules):
            if "weas" in key:
                del sys.modules[key]
        for key in list(sys.modules):
            if "crystal_viewer" in key:
                del sys.modules[key]

        with patch.dict(sys.modules, {
            "weas_widget": None,
            "weas_widget.base_widget": None,
            "weas_widget.atoms_viewer": None,
        }):
            from marimo_materials.crystal_viewer import CrystalViewer
            with pytest.raises(ImportError, match="weas-widget"):
                CrystalViewer()


# ---------------------------------------------------------------------------
# Load helpers
# ---------------------------------------------------------------------------

class TestLoadHelpers:
    def test_load_example_returns_self(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        result = cv.load_example("tio2.cif")
        assert result is cv

    def test_load_example_sets_atoms(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        cv.load_example("tio2.cif")
        # ASEAdapter.to_weas(load_online_example("tio2.cif")) was assigned
        assert mock.atoms == "weas:online_atoms"

    def test_from_ase_returns_self(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        result = cv.from_ase("fake_atoms")
        assert result is cv

    def test_from_ase_sets_atoms(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        cv.from_ase("fake_atoms")
        assert mock.atoms == "weas:fake_atoms"

    def test_from_ase_list_sets_atoms_list(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        cv.from_ase(["a1", "a2"])
        assert mock.atoms == ["weas:a1", "weas:a2"]

    def test_from_pymatgen_returns_self(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        result = cv.from_pymatgen("fake_structure")
        assert result is cv

    def test_from_pymatgen_sets_atoms(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        cv.from_pymatgen("fake_structure")
        assert mock.atoms == "weas:fake_structure"


# ---------------------------------------------------------------------------
# Style property getters and setters
# ---------------------------------------------------------------------------

class TestStyleProperties:
    def test_model_style_getter(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        mock.model_style = 2
        cv = CrystalViewer(model_style=2)
        assert cv.model_style == 2

    def test_model_style_setter(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        cv.model_style = 4
        assert mock.model_style == 4

    def test_color_type_getter(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        mock.color_type = "CPK"
        cv = CrystalViewer(color_type="CPK")
        assert cv.color_type == "CPK"

    def test_color_type_setter(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        cv.color_type = "CPK"
        assert mock.color_type == "CPK"

    def test_show_bonded_getter(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        mock.show_bonded_atoms = True
        cv = CrystalViewer(show_bonded_atoms=True)
        assert cv.show_bonded_atoms is True

    def test_show_bonded_setter(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        cv.show_bonded_atoms = True
        assert mock.show_bonded_atoms is True

    def test_boundary_getter(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        b = [[-0.1, 1.1], [-0.1, 1.1], [-0.1, 1.1]]
        mock.boundary = b
        cv = CrystalViewer()
        assert cv.boundary == b

    def test_boundary_setter(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        b = [[0.0, 2.0], [0.0, 2.0], [0.0, 2.0]]
        cv.boundary = b
        assert mock.boundary == b

    def test_color_by_getter(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        mock.color_by = "force_magnitude"
        cv = CrystalViewer()
        assert cv.color_by == "force_magnitude"

    def test_color_by_setter(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        cv.color_by = "force_magnitude"
        assert mock.color_by == "force_magnitude"

    def test_color_ramp_getter(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        ramp = ["#ff0000", "#00ff00", "#0000ff"]
        mock.color_ramp = ramp
        cv = CrystalViewer()
        assert cv.color_ramp == ramp

    def test_color_ramp_setter(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        ramp = ["#440154", "#31688e", "#35b779", "#fde724"]
        cv.color_ramp = ramp
        assert mock.color_ramp == ramp


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

class TestExportHelpers:
    def test_to_ase_returns_ase_atoms(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        # ASEAdapter.to_ase is mocked to return "ase_atoms"
        assert cv.to_ase() == "ase_atoms"

    def test_to_pymatgen_returns_pmg_structure(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        # PymatgenAdapter.to_pymatgen is mocked to return "pmg_structure"
        assert cv.to_pymatgen() == "pmg_structure"


# ---------------------------------------------------------------------------
# weas is the BaseWidget (display target); _avr is the AtomsViewer controller
# ---------------------------------------------------------------------------

class TestAttributes:
    def test_weas_attr_is_base_widget(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        # cv.weas should be a FakeBaseWidget (has guiConfig/viewerStyle)
        assert hasattr(cv.weas, "guiConfig")
        assert hasattr(cv.weas, "viewerStyle")

    def test_avr_attr_is_avr_mock(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        assert cv._avr is mock

    def test_no_state_widget_attr(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        assert not hasattr(cv, "state_widget")

    def test_no_base_widget_attr(self, viewer_cls):
        CrystalViewer, mock = viewer_cls
        cv = CrystalViewer()
        assert not hasattr(cv, "base_widget")



