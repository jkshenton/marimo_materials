"""Public widget exports for the marimo_materials package."""

import importlib.metadata

from .altair_widget import AltairWidget
try:
    from .crystal_viewer import CrystalViewer
except ImportError:
    pass

__version__ = importlib.metadata.version("marimo_materials")

__all__ = [
    "AltairWidget",
    "CrystalViewer",
]
