"""
Documentation pages module.

This module contains individual documentation pages for components.
Each page is a separate module with a get_routes() function that registers
its routes with the FastAPI app.
"""

from . import codeblock, tabs, accordion

def register_all_routes(app):
    """Register all component documentation routes with the app"""
    codeblock.get_routes(app)
    tabs.get_routes(app)
    accordion.get_routes(app)