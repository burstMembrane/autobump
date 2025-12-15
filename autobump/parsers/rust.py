# parsers/rust.py
from pathlib import Path

import tomlkit

from .base import ConfigParser


class RustConfigParser(ConfigParser):
    """Parser for Rust Cargo.toml files."""
    
    def get_version(self) -> str:
        """Extract the current version from Cargo.toml."""
        content = self.file_path.read_text()
        doc = tomlkit.parse(content)
        
        if "package" not in doc or "version" not in doc["package"]:
            raise KeyError("No 'package.version' field found in Cargo.toml")
        
        return doc["package"]["version"]
    
    def set_version(self, new_version: str) -> str:
        """
        Update the version in Cargo.toml.
        
        Args:
            new_version: The new version string
            
        Returns:
            The updated file content as a string
        """
        content = self.file_path.read_text()
        doc = tomlkit.parse(content)
        doc["package"]["version"] = new_version
        return tomlkit.dumps(doc)
    
    def write_changes(self, content: str) -> None:
        """Write the updated content back to Cargo.toml."""
        self.file_path.write_text(content)