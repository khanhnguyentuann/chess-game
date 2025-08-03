# Application Layer

The application layer contains the business logic and orchestration for the chess game. It follows Clean Architecture principles with clear separation of concerns.

## Structure

```
src/application/
├── __init__.py                 # Package exports
├── README.md                   # This file
├── commands/                   # Command pattern implementations
│   ├── __init__.py
│   ├── base_command.py        # Base command interfaces and executor
│   └── move_command.py        # Chess move commands
├── contracts/                  # Input/Output contracts (DTOs)
│   ├── __init__.py
│   ├── base_contracts.py      # Base request/response classes
│   ├── move_contracts.py      # Move operation contracts
│   └── game_contracts.py      # Game state contracts
├── services/                   # Application services
│   ├── __init__.py
│   └── game_application_service.py  # Main application service
├── use_cases/                  # Business logic use cases
│   ├── __init__.py
│   ├── make_move.py           # Make move use case
│   ├── get_legal_moves.py     # Get legal moves use case
│   ├── undo_move.py           # Undo move use case
│   └── redo_move.py           # Redo move use case
└── validators/                 # Application-level validators
    ├── __init__.py
    ├── move_validator.py      # Move request validation
    └── game_validator.py      # Game state validation
```

## Key Components

### Contracts (DTOs)
- **BaseRequest/BaseResponse**: Base classes for all request/response objects
- **MoveRequest/MoveResponse**: Contracts for move operations
- **GameStateRequest/GameStateResponse**: Contracts for game state operations
- **LegalMovesRequest/LegalMovesResponse**: Contracts for legal moves operations

### Use Cases
- **MakeMoveUseCase**: Handles move execution with validation and persistence
- **GetLegalMovesUseCase**: Retrieves legal moves for current position
- **UndoMoveUseCase**: Handles move undo operations
- **RedoMoveUseCase**: Handles move redo operations

### Services
- **GameApplicationService**: Main orchestrator that coordinates use cases and provides unified interface

### Validators
- **MoveRequestValidator**: Validates move requests against business rules
- **GameStateValidator**: Validates game state requests

### Commands
- **CommandExecutor**: Manages command execution with undo/redo support
- **MakeMoveCommand**: Command for executing chess moves
- **CompositeCommand**: For complex operations involving multiple commands

## Usage

### Basic Usage

```python
from src.composition_root import get_game_application_service
from src.application.contracts.move_contracts import MoveRequest

# Get the application service
app_service = get_game_application_service()

# Create a move request
move_request = MoveRequest(
    from_square=chess.E2,
    to_square=chess.E4,
    game_id="game-123"
)

# Execute the move
result = await app_service.make_move(move_request)

if result.success:
    print(f"Move executed: {result.message}")
else:
    print(f"Move failed: {result.error}")
```

### Getting Legal Moves

```python
from src.application.contracts.game_contracts import LegalMovesRequest

# Get all legal moves
request = LegalMovesRequest(game_id="game-123")
result = await app_service.get_legal_moves(request)

# Get moves for specific square
request = LegalMovesRequest(game_id="game-123", square=chess.E2)
result = await app_service.get_legal_moves(request)
```

### Undo/Redo Operations

```python
# Undo last move
result = await app_service.undo_last_move("game-123")

# Redo last undone move
result = await app_service.redo_last_move("game-123")
```

## Benefits of This Structure

1. **Clear Separation of Concerns**: Each component has a single responsibility
2. **Testability**: Easy to unit test individual components
3. **Maintainability**: Changes are isolated to specific components
4. **Extensibility**: Easy to add new use cases or modify existing ones
5. **Type Safety**: Strong typing with contracts ensures data integrity
6. **Validation**: Multiple layers of validation (contract, application, domain)
7. **Error Handling**: Consistent error handling across all operations

## Dependency Injection

All components are wired through the composition root (`src/composition_root.py`). This ensures:
- Loose coupling between components
- Easy testing with mock dependencies
- Centralized configuration management

## Testing

Each component can be tested independently:

```python
# Test a use case
def test_make_move_use_case():
    mock_validator = Mock()
    mock_repo = Mock()
    use_case = MakeMoveUseCase(mock_validator, mock_repo, ...)
    
    result = await use_case.execute(game, move_request)
    assert result.success

# Test a validator
def test_move_validator():
    validator = MoveRequestValidator(mock_domain_validator)
    errors = validator.get_validation_errors(request, game)
    assert len(errors) == 0
``` 