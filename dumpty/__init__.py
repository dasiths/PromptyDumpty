"""PromptyDumpty - Universal package manager for AI coding assistants."""

try:
    from importlib.metadata import version

    __version__ = version("prompty-dumpty")
except Exception:
    # Fallback for development/editable installs
    __version__ = "0.0.0+dev"
