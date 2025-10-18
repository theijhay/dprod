"""Project type detectors."""

from .base import BaseDetector
from .nodejs import NodeJSDetector
from .python import PythonDetector
from .go import GoDetector
from .static import StaticDetector
from .generic import GenericDetector

__all__ = [
    "BaseDetector",
    "NodeJSDetector", 
    "PythonDetector",
    "GoDetector",
    "StaticDetector",
    "GenericDetector"
]