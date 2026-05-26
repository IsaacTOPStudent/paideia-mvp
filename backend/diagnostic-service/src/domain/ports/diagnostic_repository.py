from abc import ABC, abstractmethod
from typing import Optional, List 
from ..entities.diagnostic_catalog import Diagnostic

class DiagnosticCatalogRepository(ABC):
    """Port: Diagnostic Catalog Repository"""

    @abstractmethod
    def save(self, diagnostic: Diagnostic) -> Diagnostic:
        """Save or update diagnosis"""
        pass

    @abstractmethod
    def find_by_id(self, diagnostic_id: int) -> Optional[Diagnostic]:
        """Search diagnosis by ID"""
        pass

    @abstractmethod
    def find_by_code(self, code: str) -> Optional[Diagnostic]:
        """Search diagnosis by code"""
        pass

    @abstractmethod
    def find_all_active(self) -> List[Diagnostic]:
        """List all active diagnoses (RN-05)"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Diagnostic]:
        """List all diagnoses"""
        pass

    @abstractmethod
    def exists_by_code(self, code: str) -> bool:
        """Check if there is a diagnosis with that code."""
        pass
    
    @abstractmethod
    def is_any_active(self) -> bool:
        """Check if there is at least one active diagnosis (RN-05)"""
        pass