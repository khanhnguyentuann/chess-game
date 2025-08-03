"""
Application Contracts (DTOs)
Defines input/output contracts for application layer operations.
"""

from .move_contracts import MoveRequest, MoveResponse
from .game_contracts import GameStateResponse, LegalMovesResponse
from .base_contracts import BaseRequest, BaseResponse

__all__ = [
    "MoveRequest",
    "MoveResponse", 
    "GameStateResponse",
    "LegalMovesResponse",
    "BaseRequest",
    "BaseResponse",
] 