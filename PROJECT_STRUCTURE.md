# Chess Game - Project Structure

A chess game built with Clean Architecture and Domain-Driven Design principles.

## Overall Architecture

```
chess-game/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── PROJECT_STRUCTURE.md       # This file
└── src/
    ├── application/           # Application Layer (Use Cases, Commands)
    ├── domain/               # Domain Layer (Business Logic, Entities)
    ├── infrastructure/       # Infrastructure Layer (External Concerns)
    ├── presentation/         # Presentation Layer (UI, Controllers)
    ├── shared/              # Shared Layer (Utilities, Types)
    └── composition_root.py   # Dependency Injection Container
```

## Layer Details

### 🎯 Application Layer (`src/application/`)
**Purpose**: Orchestrates use cases and coordinates between domain and infrastructure.

```
application/
├── contracts/           # DTOs and API contracts
│   ├── base_contracts.py
│   ├── move_contracts.py
│   └── game_contracts.py
├── services/           # Application services
│   └── game_application_service.py
├── validators/         # Application-level validation
│   ├── move_validator.py
│   └── game_validator.py
├── use_cases/          # Business use cases
│   ├── make_move.py
│   ├── get_legal_moves.py
│   ├── undo_move.py
│   └── redo_move.py
├── commands/           # Command pattern implementations
│   ├── base_command.py
│   └── move_command.py
└── README.md
```

### 🧠 Domain Layer (`src/domain/`)
**Purpose**: Core business logic, entities, and domain rules.

```
domain/
├── entities/           # Core business entities
│   ├── board.py
│   ├── game.py
│   └── move_history.py
├── value_objects/      # Immutable value objects
│   ├── square.py
│   ├── move.py
│   └── position.py
├── services/          # Domain services
│   ├── move_validator.py
│   └── game_rules_service.py
├── events/            # Domain events
│   ├── domain_events.py
│   ├── event_dispatcher.py
│   └── game_events.py
├── exceptions/        # Domain-specific exceptions
│   ├── game_exceptions.py
│   └── move_exceptions.py
├── interfaces/        # Repository and service contracts
│   ├── repositories.py
│   └── services.py
└── README.md
```

### 🔧 Infrastructure Layer (`src/infrastructure/`)
**Purpose**: External concerns, data persistence, and infrastructure implementations.

```
infrastructure/
├── persistence/        # Data access implementations
│   ├── memory_game_repository.py
│   ├── memory_move_history_repository.py
│   └── __init__.py
├── services/          # Infrastructure services
│   ├── notification_service.py
│   ├── config_service.py
│   ├── logging_service.py
│   └── __init__.py
├── event_publisher/   # Event publishing infrastructure
│   ├── event_publisher.py
│   └── __init__.py
└── README.md
```

### 🎨 Presentation Layer (`src/presentation/`)
**Purpose**: User interface and presentation logic.

```
presentation/
├── ui/               # User interface components
│   ├── chess_game_ui.py
│   ├── modern_chess_ui.py
│   ├── menu_system.py
│   ├── piece_renderer.py
│   ├── components/   # UI components
│   ├── animations/   # Animation system
│   └── themes/       # UI themes
├── controllers/      # Presentation controllers
└── __init__.py
```

### 🔗 Shared Layer (`src/shared/`)
**Purpose**: Shared utilities, types, and configurations.

```
shared/
├── config/          # Configuration management
│   └── game_config.py
├── exceptions/      # Shared exceptions
│   └── game_exceptions.py
├── types/          # Type definitions and enums
│   ├── enums.py
│   └── type_definitions.py
└── utils/          # Utility functions
    ├── logging_utils.py
    └── save_manager.py
```

## Design Principles

### 1. Clean Architecture
- **Dependency Rule**: Dependencies point inward
- **Domain Layer**: Independent of all other layers
- **Application Layer**: Orchestrates domain and infrastructure
- **Infrastructure Layer**: Implements domain interfaces
- **Presentation Layer**: Handles user interaction

### 2. Domain-Driven Design (DDD)
- **Entities**: Core business objects with identity
- **Value Objects**: Immutable objects with validation
- **Domain Services**: Business logic that doesn't belong to entities
- **Domain Events**: Important business occurrences
- **Repository Pattern**: Data access abstraction

### 3. SOLID Principles
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes are substitutable
- **Interface Segregation**: Clients depend only on interfaces they use
- **Dependency Inversion**: High-level modules don't depend on low-level modules

## Key Features

### ✅ Implemented
- **Clean Architecture Structure**: Proper layer separation
- **Domain-Driven Design**: Rich domain model with value objects
- **Event-Driven Architecture**: Domain events and event publishing
- **Dependency Injection**: Composition root for dependency management
- **Repository Pattern**: Abstract data access
- **Command Pattern**: Undo/redo functionality
- **Validation**: Multi-layer validation (domain, application)
- **Error Handling**: Domain-specific exceptions
- **Configuration Management**: Centralized configuration
- **Logging**: Structured logging infrastructure

### 🚀 Future Enhancements
- **Database Persistence**: PostgreSQL, Redis implementations
- **Real-time Notifications**: WebSocket integration
- **AI Integration**: Chess engine integration
- **Multiplayer Support**: Network game functionality
- **Tournament System**: Tournament management
- **Analytics**: Game analysis and statistics
- **Mobile Support**: Mobile UI implementation

## Technology Stack

- **Language**: Python 3.12
- **UI Framework**: Pygame
- **Chess Engine**: python-chess
- **Architecture**: Clean Architecture + DDD
- **Patterns**: Repository, Command, Event Sourcing
- **Testing**: pytest (planned)
- **Documentation**: Markdown + docstrings

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Game**:
   ```bash
   python main.py
   ```

3. **Development**:
   - Follow Clean Architecture principles
   - Add new features in appropriate layers
   - Maintain separation of concerns
   - Write tests for new functionality

## Benefits

1. **Maintainability**: Clear structure makes code easy to understand and modify
2. **Testability**: Isolated components are easy to test
3. **Scalability**: Easy to add new features and swap implementations
4. **Flexibility**: Can change infrastructure without affecting business logic
5. **Team Collaboration**: Clear boundaries and responsibilities 