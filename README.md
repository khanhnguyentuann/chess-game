# Chess Game - MVC Architecture

A clean, well-structured chess game implemented in Python using the Model-View-Controller (MVC) design pattern.

## Architecture

This project follows a clean MVC architecture:

- **Model** (`models/chess_board.py`): Handles chess logic, board state, rules, and move validation
- **View** (`views/pygame_view.py`): Manages all rendering and visual presentation using Pygame
- **Controller** (`controllers/game_controller.py`): Handles user input, game flow, and coordinates between Model and View

## Project Structure

```
chess-game/
├── main.py                    # Entry point - starts the game controller
├── models/
│   └── chess_board.py        # Chess game logic and state management
├── views/
│   └── pygame_view.py        # Pygame rendering and UI
├── controllers/
│   └── game_controller.py    # Input handling and game flow
├── config.py                 # Game configuration and constants
├── assets/
│   └── images/              # Chess piece images
├── tests/
│   └── test_chess.py        # Unit tests for the chess model
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Features

- **Clean MVC Architecture**: Separation of concerns with clear responsibilities
- **Full Chess Rules**: Complete implementation using the `python-chess` library
- **Interactive GUI**: Pygame-based interface with piece selection and move highlighting
- **Game Controls**: 
  - Mouse click to select and move pieces
  - Keyboard shortcuts (R to reset, U to undo, ESC/Q to quit)
  - Visual feedback for valid moves and piece selection
- **Game States**: Proper handling of check, checkmate, stalemate, and draws
- **Unit Tests**: Comprehensive test suite for the model layer

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/khanhnguyentuann/chess-game.git
   cd chess-game
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

**Run the game:**
```bash
python main.py
```

**Run tests:**
```bash
python test_runner.py
```

## Game Controls

- **Mouse**: Click to select pieces and make moves
- **R**: Reset the game
- **U**: Undo last move
- **ESC/Q**: Quit the game
- **Space**: Continue through menus

## Dependencies

- `pygame==2.5.2` - Game graphics and input handling
- `python-chess==1.999` - Chess logic and rule validation

## Development

The codebase follows clean code principles:

- **Type hints** for better code documentation
- **Comprehensive docstrings** for all classes and methods
- **Error handling** for robust gameplay
- **Unit tests** for model validation
- **Modular design** for easy maintenance and extension

## Architecture Benefits

1. **Maintainability**: Clear separation allows easy modification of individual components
2. **Testability**: Model logic can be tested independently of UI
3. **Extensibility**: Easy to add new features like AI players, network play, or different UIs
4. **Reusability**: Model can be reused with different view implementations

## Testing

The project includes comprehensive unit tests for the chess model:

```bash
# Run all tests with custom test runner
python test_runner.py

# Run pytest tests (if pytest is installed)
pytest tests/test_chess.py -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the existing code style
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Credits

- Chess logic powered by [python-chess](https://python-chess.readthedocs.io/)
- Chess piece images from Wikimedia Commons (Creative Commons licensed)
- Built with [Pygame](https://www.pygame.org/) for graphics and input handling
