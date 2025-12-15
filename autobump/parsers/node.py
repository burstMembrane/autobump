# parsers/node.py
import json
from pathlib import Path

from .base import ConfigParser


class NodeConfigParser(ConfigParser):
    """Parser for Node.js package.json files."""
    
    def get_version(self) -> str:
        """Extract the current version from package.json."""
        content = self.file_path.read_text()
        data = json.loads(content)
        
        if "version" not in data:
            raise KeyError("No 'version' field found in package.json")
        
        return data["version"]
    
    def set_version(self, new_version: str) -> str:
        """
        Update the version in package.json.
        
        Args:
            new_version: The new version string
            
        Returns:
            The updated file content as a string
        """
        content = self.file_path.read_text()
        data = json.loads(content)
        data["version"] = new_version
        
        # Preserve formatting by using indent=2 (common Node.js convention)
        return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    
    def write_changes(self, content: str) -> None:
        """Write the updated content back to package.json."""
        self.file_path.write_text(content)