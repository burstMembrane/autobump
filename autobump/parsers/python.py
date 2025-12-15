# parsers/python.py
import re
from pathlib import Path

import tomlkit

from .base import ConfigParser


class PythonConfigParser(ConfigParser):
    """Parser for Python pyproject.toml and setup.py files."""
    
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.is_pyproject = self.file_path.name == "pyproject.toml"
        self.is_setup_py = self.file_path.name == "setup.py"
        
        if not (self.is_pyproject or self.is_setup_py):
            raise ValueError(f"Unsupported Python config file: {self.file_path.name}")
    
    def get_version(self) -> str:
        """Extract the current version from the Python config file."""
        if self.is_pyproject:
            return self._get_version_from_pyproject()
        else:
            return self._get_version_from_setup_py()
    
    def set_version(self, new_version: str) -> str:
        """
        Update the version in the Python config file.
        
        Args:
            new_version: The new version string
            
        Returns:
            The updated file content as a string
        """
        if self.is_pyproject:
            return self._set_version_in_pyproject(new_version)
        else:
            return self._set_version_in_setup_py(new_version)
    
    def write_changes(self, content: str) -> None:
        """Write the updated content back to the config file."""
        self.file_path.write_text(content)
    
    def _get_version_from_pyproject(self) -> str:
        """Extract version from pyproject.toml."""
        content = self.file_path.read_text()
        doc = tomlkit.parse(content)
        
        if "project" not in doc or "version" not in doc["project"]:
            raise KeyError("No 'project.version' field found in pyproject.toml")
        
        return doc["project"]["version"]
    
    def _set_version_in_pyproject(self, new_version: str) -> str:
        """Update version in pyproject.toml."""
        content = self.file_path.read_text()
        doc = tomlkit.parse(content)
        doc["project"]["version"] = new_version
        return tomlkit.dumps(doc)
    
    def _get_version_from_setup_py(self) -> str:
        """Extract version from setup.py."""
        content = self.file_path.read_text()
        
        # Look for version= patterns in setup.py
        version_patterns = [
            r'version\s*=\s*["\']([^"\']+)["\']',
            r'__version__\s*=\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        raise ValueError("Could not find version in setup.py")
    
    def _set_version_in_setup_py(self, new_version: str) -> str:
        """Update version in setup.py."""
        content = self.file_path.read_text()
        
        # Replace version= patterns
        version_patterns = [
            (r'(version\s*=\s*["\'])([^"\']+)(["\'])', rf'\g<1>{new_version}\g<3>'),
            (r'(__version__\s*=\s*["\'])([^"\']+)(["\'])', rf'\g<1>{new_version}\g<3>'),
        ]
        
        for pattern, replacement in version_patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                return new_content
        
        raise ValueError("Could not update version in setup.py")