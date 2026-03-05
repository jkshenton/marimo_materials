"""Public widget exports for the marimo_materials package."""

import importlib.metadata

from .atoms_view import show_atoms
try:
    from .crystal_editor import CrystalEditorWidget
except ImportError:
    pass

try:
    from .crystal_viewer import CrystalViewer
    from .crystal_viewer_controls import (
        make_viewer_controls,
        viewer_controls_panel,
        viewer_controls_to_kwargs,
    )
except ImportError:
    pass

try:
    from .crystal_upload import CrystalUploadWidget
except ImportError:
    pass

try:
    from .crystal_download import CrystalDownloadWidget
except ImportError:
    pass

try:
    from .crystal_builder import (
        BulkBuilderWidget,
        MoleculeBuilderWidget,
        NanoparticleBuilderWidget,
        SurfaceBuilderWidget,
    )
except ImportError:
    pass

__version__ = importlib.metadata.version("marimo_materials")

__all__ = [
    "BulkBuilderWidget",
    "CrystalDownloadWidget",
    "CrystalEditorWidget",
    "CrystalUploadWidget",
    "CrystalViewer",
    "make_viewer_controls",
    "viewer_controls_panel",
    "viewer_controls_to_kwargs",
    "MoleculeBuilderWidget",
    "NanoparticleBuilderWidget",
    "SurfaceBuilderWidget",
    "show_atoms",
]
