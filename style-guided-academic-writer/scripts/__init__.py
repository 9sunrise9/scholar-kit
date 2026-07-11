"""style-guided-academic-writer scripts package.

This package provides CLI tooling for the style-guided-academic-writer skill:

* :mod:`retrieve_templates` — query a distill package by section/intent/tense
* :mod:`apply_style_to_draft` — compute paragraph-level alignment between a
  draft and a distill package
* :mod:`_pkg_loader` — shared loader that normalizes the distill package JSON
  into a typed structure consumable by both scripts
"""

__all__ = ["retrieve_templates", "apply_style_to_draft", "_pkg_loader"]