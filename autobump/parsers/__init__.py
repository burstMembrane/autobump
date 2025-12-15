# parsers/__init__.py
from .base import ConfigParser
from .node import NodeConfigParser
from .python import PythonConfigParser
from .rust import RustConfigParser

__all__ = ["ConfigParser", "NodeConfigParser", "PythonConfigParser", "RustConfigParser"]


def get_parser(language: str, config_file_path) -> ConfigParser:
    """Factory function to get the appropriate parser for a language."""
    if language == "node":
        return NodeConfigParser(config_file_path)
    elif language == "python":
        return PythonConfigParser(config_file_path)
    elif language == "rust":
        return RustConfigParser(config_file_path)
    else:
        raise ValueError(f"Unsupported language: {language}")