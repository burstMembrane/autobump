# language_detection.py
from pathlib import Path
from typing import Optional, Tuple


class UnsupportedLanguageError(Exception):
    pass


def detect_language() -> Tuple[str, Path]:
    """
    Detect the programming language and return the language type and config file path.
    
    Returns:
        Tuple of (language_type, config_file_path)
        
    Raises:
        UnsupportedLanguageError: If no supported project files are found
    """
    cwd = Path.cwd()
    
    # Check for Node.js/TypeScript projects
    package_json = cwd / "package.json"
    if package_json.exists():
        return ("node", package_json)
    
    # Check for Python projects (prioritize pyproject.toml over setup.py)
    pyproject_toml = cwd / "pyproject.toml"
    if pyproject_toml.exists():
        return ("python", pyproject_toml)
    
    setup_py = cwd / "setup.py"
    if setup_py.exists():
        return ("python", setup_py)
    
    # Check for Rust projects
    cargo_toml = cwd / "Cargo.toml"
    if cargo_toml.exists():
        return ("rust", cargo_toml)
    
    # Check for Go projects
    go_mod = cwd / "go.mod"
    if go_mod.exists():
        return ("go", go_mod)
    
    # No supported project files found
    raise UnsupportedLanguageError(
        "No supported project files found. Supported files: package.json, pyproject.toml, setup.py, Cargo.toml, go.mod"
    )


def get_supported_languages() -> list[str]:
    """Return list of supported languages."""
    return ["node", "python", "rust", "go"]


def get_config_file_for_language(language: str, custom_path: Optional[Path] = None) -> Path:
    """
    Get the config file path for a specific language.
    
    Args:
        language: The language type
        custom_path: Optional custom config file path
        
    Returns:
        Path to the config file
        
    Raises:
        UnsupportedLanguageError: If language is not supported
        FileNotFoundError: If the config file doesn't exist
    """
    if custom_path:
        if not custom_path.exists():
            raise FileNotFoundError(f"Custom config file not found: {custom_path}")
        return custom_path
    
    cwd = Path.cwd()
    
    if language == "node":
        config_file = cwd / "package.json"
    elif language == "python":
        # Prefer pyproject.toml over setup.py
        pyproject = cwd / "pyproject.toml"
        setup_py = cwd / "setup.py"
        config_file = pyproject if pyproject.exists() else setup_py
    elif language == "rust":
        config_file = cwd / "Cargo.toml"
    elif language == "go":
        config_file = cwd / "go.mod"
    else:
        raise UnsupportedLanguageError(f"Unsupported language: {language}")
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    return config_file