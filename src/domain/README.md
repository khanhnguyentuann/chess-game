# Domain Layer

The domain layer contains the core business logic and entities for the chess game. It follows Domain-Driven Design (DDD) principles and is completely independent of external concerns.

## Structure

```
src/domain/
├── entities/           # Core business entities
│   ├── board.py       # Chess board entity
│   ├── game.py        # Game entity
│   └── move_history.py # Move history entity
├── events/            # Domain events
│   ├── domain_events.py # Business events
│   ├── event_dispatcher.py # Event dispatching
│   └── game_events.py # Game-specific events
├── exceptions/        # Domain-specific exceptions
│   ├── game_exceptions.py # Game-related exceptions
│   └── move_exceptions.py # Move-related exceptions
├── interfaces/        # Repository interfaces
│   ├── repositories.py # Data access contracts
│   └── services.py    # Service contracts
├── services/         # Domain services
│   ├── game_rules_service.py # Game rules logic
│   └── move_validator.py # Move validation
└── value_objects/    # Immutable value objects
    ├── move.py       # Move value object
    ├── position.py   # Position value object
    └── square.py     # Square value object
```

## Key Components

### Entities

- **Board**: Represents the chess board state and provides board operations
- **Game**: Orchestrates game state and rules, manages game flow
- **MoveHistory**: Tracks move history and provides undo/redo functionality

### Value Objects

- **Square**: Immutable representation of a chess square with validation
- **Move**: Immutable representation of a chess move with business rules
- **Position**: Immutable representation of a chess position (FEN-based)

### Domain Services

- **MoveValidatorService**: Validates moves according to chess rules
- **GameRulesService**: Manages game state transitions and rules

### Domain Events

- **GameStartedEvent**: Raised when a new game starts
- **MoveMadeEvent**: Raised when a move is executed
- **GameEndedEvent**: Raised when a game ends
- **GameStateChangedEvent**: Raised when game state changes

### Exceptions

- **InvalidMoveException**: Base exception for move-related errors
- **GameAlreadyEndedException**: Raised when trying to act on ended game
- **WrongPlayerException**: Raised when wrong player tries to move

## Design Principles

### 1. Immutability
Value objects are immutable and contain validation logic:
```python
square = Square(32)  # e4
move = Move.from_squares(Square(52), Square(36))  # e2e4
```

### 2. Rich Domain Model
Entities contain business logic and enforce invariants:
```python
game = Game(white_player="Alice", black_player="Bob")
game.make_move_from_squares(52, 36)  # e2e4
```

### 3. Domain Events
Important business occurrences are captured as events:
```python
# Events are raised automatically when moves are made
# and can be handled by event handlers
```

### 4. Repository Pattern
Data access is abstracted through repository interfaces:
```python
class IGameRepository(ABC):
    @abstractmethod
    async def save_game(self, game: Game) -> str:
        pass
```

## Usage Examples

### Creating a Game
```python
from src.domain import Game, GameRulesService

game = Game(white_player="Alice", black_player="Bob")
rules_service = GameRulesService()

# Check if move can be made
if rules_service.can_make_move(game):
    # Make move
    pass
```

### Validating Moves
```python
from src.domain import MoveValidatorService, Move, Square

validator = MoveValidatorService()
move = Move.from_squares(Square(52), Square(36))

try:
    validator.validate_move(game, move)
    # Move is valid
except InvalidMoveException as e:
    # Handle invalid move
    pass
```

### Working with Value Objects
```python
from src.domain import Square, Move, Position

# Create square from algebraic notation
square = Square.from_algebraic("e4")

# Create move from squares
move = Move.from_squares(Square.from_algebraic("e2"), Square.from_algebraic("e4"))

# Create position from FEN
position = Position.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
```

## Benefits

1. **Separation of Concerns**: Business logic is isolated from infrastructure
2. **Testability**: Domain logic can be tested independently
3. **Maintainability**: Clear structure makes code easier to understand and modify
4. **Type Safety**: Value objects provide compile-time validation
5. **Event-Driven**: Domain events enable loose coupling between components

## Dependencies

The domain layer has no dependencies on:
- Infrastructure (databases, external APIs)
- Application layer (use cases, commands)
- Presentation layer (UI, controllers)

It only depends on:
- Python standard library
- python-chess library (for chess rules)
- Shared types and enums 