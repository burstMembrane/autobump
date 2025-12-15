# parsers/base.py
from abc import ABC, abstractmethod
from pathlib import Path


class ConfigParser(ABC):
    """Abstract base class for configuration file parsers."""
    
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
    
    @abstractmethod
    def get_version(self) -> str:
        """Extract the current version from the config file."""
        pass
    
    @abstractmethod
    def set_version(self, new_version: str) -> str:
        """
        Update the version in the config file.
        
        Args:
            new_version: The new version string
            
        Returns:
            The updated file content as a string
        """
        pass
    
    @abstractmethod
    def write_changes(self, content: str) -> None:
        """Write the updated content back to the config file."""
        pass
    
    def get_file_path(self) -> Path:
        """Return the config file path."""
        return self.file_path