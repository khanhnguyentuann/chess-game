"""
Base Contracts
Defines base classes for request and response contracts.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass
class BaseRequest(ABC):
    """Base class for all request contracts."""
    
    request_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate the request data."""
        pass
    
    @abstractmethod
    def get_validation_errors(self) -> list[str]:
        """Get validation errors if any."""
        pass


@dataclass
class BaseResponse(ABC):
    """Base class for all response contracts."""
    
    success: bool
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success_response(cls, data: Dict[str, Any], message: str = "Success") -> "BaseResponse":
        """Create a successful response."""
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def error_response(cls, error: str, message: str = "Error occurred") -> "BaseResponse":
        """Create an error response."""
        return cls(success=False, error=error, message=message) 