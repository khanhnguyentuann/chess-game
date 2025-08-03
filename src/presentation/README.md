# Presentation Layer

The presentation layer handles user interface, user interactions, and presentation logic. It coordinates between the user and the application layer, providing a clean separation between UI concerns and business logic.

## Structure

```
src/presentation/
├── controllers/          # User interaction controllers
│   ├── game_controller.py
│   ├── input_handler.py
│   └── __init__.py
├── viewmodels/          # UI state management
│   ├── game_view_model.py
│   └── __init__.py
├── ui/                  # User interface components
│   ├── chess_game_ui.py
│   ├── modern_chess_ui.py
│   ├── menu_system.py
│   ├── piece_renderer.py
│   ├── components/      # Reusable UI components
│   ├── themes/         # UI themes and styling
│   ├── animations/     # Animation system
│   └── __init__.py
└── __init__.py
```

## Key Components

### Controllers

- **GameController**: Handles game-related user interactions and coordinates with application layer
- **InputHandler**: Processes user input events and converts them to game actions

### View Models

- **GameViewModel**: Manages UI state and provides data for presentation
- **GameStateViewModel**: Represents current game state for UI
- **BoardSquareViewModel**: Represents individual board squares
- **MenuViewModel**: Manages menu state and navigation

### UI Components

- **ChessGameUI**: Main chess game interface
- **ModernChessUI**: Modern styled chess interface
- **MenuSystem**: Menu navigation and management
- **PieceRenderer**: Renders chess pieces
- **Button, Panel, BaseComponent**: Reusable UI components
- **ThemeManager**: Manages UI themes and styling
- **AnimationSystem**: Handles UI animations

## Design Principles

### 1. Separation of Concerns
Presentation layer is responsible only for:
- User interface rendering
- User input handling
- UI state management
- Presentation logic

### 2. Dependency Direction
Presentation layer depends on:
- Application layer (for business operations)
- Domain layer (for entities and value objects)

It does NOT depend on:
- Infrastructure layer (directly)

### 3. Controller Pattern
Controllers handle user interactions and coordinate between UI and application layer:
```python
class GameController:
    def __init__(self, game_service: IGameApplicationService):
        self._game_service = game_service
    
    async def make_move(self, from_square: int, to_square: int) -> Dict[str, Any]:
        # Coordinate between UI and application layer
        return await self._game_service.make_move(...)
```

### 4. View Model Pattern
View models manage UI state and provide data for presentation:
```python
class GameViewModel:
    def update_from_game(self, game: Game) -> None:
        # Update UI state from domain model
        self._ui_state.game_state.current_player = game.current_player.value
```

## Usage Examples

### Game Controller
```python
from src.presentation import GameController
from src.application import get_game_application_service

# Create controller
game_service = get_game_application_service()
controller = GameController(game_service)

# Start new game
result = await controller.start_new_game("Player 1", "Player 2")

# Make move
move_result = await controller.make_move(52, 36)  # e2e4
```

### Input Handler
```python
from src.presentation import InputHandler
import pygame

# Create input handler
input_handler = InputHandler()

# Register event handlers
def handle_mouse_click(event_data):
    print(f"Mouse clicked at {event_data['data']['pos']}")

input_handler.register_event_handler("mouse_down", handle_mouse_click)

# Process events
events = pygame.event.get()
processed_events = input_handler.handle_events(events)
```

### Game View Model
```python
from src.presentation import GameViewModel
from src.domain.entities.game import Game

# Create view model
view_model = GameViewModel()

# Update from game state
game = Game.create_new_game()
view_model.update_from_game(game, selected_square=52, legal_moves=[36, 44])

# Get UI state
ui_state = view_model.get_ui_state()
game_state = view_model.get_game_state()

# Access board squares
square = view_model.get_square_at(52)
print(f"Square {square.algebraic_notation} has piece: {square.piece_type}")
```

### UI Components
```python
from src.presentation import ChessGameUI, ThemeManager
import pygame

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))

# Create UI components
theme_manager = ThemeManager()
chess_ui = ChessGameUI(screen, theme_manager)

# Render game
game_state = view_model.get_game_state()
chess_ui.render_game(game_state)
```

## Benefits

1. **Clean Separation**: UI concerns separated from business logic
2. **Testability**: Controllers and view models can be easily tested
3. **Maintainability**: Clear structure makes UI changes easier
4. **Reusability**: UI components can be reused across different views
5. **Flexibility**: Easy to swap UI implementations or add new features

## Dependencies

The presentation layer depends on:
- Application layer (for business operations)
- Domain layer (for entities and value objects)
- Pygame (for rendering and input)

It does NOT depend on:
- Infrastructure layer (directly)

## Future Enhancements

### UI Improvements
- **Web UI**: Web-based interface using React/Vue
- **Mobile UI**: Mobile-optimized interface
- **3D UI**: 3D chess board rendering
- **VR/AR**: Virtual/Augmented reality interface

### Input Enhancements
- **Touch Support**: Touch gestures for mobile
- **Voice Commands**: Voice-controlled chess moves
- **AI Suggestions**: Visual move suggestions
- **Haptic Feedback**: Tactile feedback for moves

### Accessibility
- **Screen Reader**: Support for screen readers
- **High Contrast**: High contrast themes
- **Keyboard Navigation**: Full keyboard support
- **Color Blind Support**: Color blind friendly themes 