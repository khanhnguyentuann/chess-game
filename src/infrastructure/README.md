# Infrastructure Layer

The infrastructure layer contains all external concerns, data persistence implementations, and infrastructure services. It implements the interfaces defined in the domain layer and provides concrete implementations for external dependencies.

## Structure

```
src/infrastructure/
├── persistence/           # Data access implementations
│   ├── memory_game_repository.py
│   ├── memory_move_history_repository.py
│   └── __init__.py
├── services/             # Infrastructure services
│   ├── notification_service.py
│   ├── config_service.py
│   ├── logging_service.py
│   └── __init__.py
├── event_publisher/      # Event publishing infrastructure
│   ├── event_publisher.py
│   └── __init__.py
└── __init__.py
```

## Key Components

### Persistence Layer

- **MemoryGameRepository**: In-memory implementation of game persistence
- **MemoryMoveHistoryRepository**: In-memory implementation of move history persistence

### Infrastructure Services

- **DummyNotificationService**: Dummy implementation for testing notifications
- **ConfigService**: Application configuration management
- **LoggingService**: Centralized logging infrastructure

### Event Publishing

- **EventPublisher**: Domain event publishing and subscription management

## Design Principles

### 1. Dependency Inversion
Infrastructure implements domain interfaces:
```python
from ...domain.interfaces.repositories import IGameRepository

class MemoryGameRepository(IGameRepository):
    # Implementation of domain interface
```

### 2. External Concerns Isolation
All external dependencies are contained in this layer:
- Database connections
- File system operations
- External API calls
- Logging configuration
- Configuration management

### 3. Pluggable Implementations
Easy to swap implementations:
```python
# In-memory for development
game_repo = MemoryGameRepository()

# Database for production
game_repo = DatabaseGameRepository()
```

## Usage Examples

### Configuration Management
```python
from src.infrastructure import ConfigService

config_service = ConfigService()
debug_mode = config_service.is_debug_mode()
game_config = config_service.get_game_config()
```

### Event Publishing
```python
from src.infrastructure import EventPublisher
from src.domain.events import MoveMadeEvent

publisher = EventPublisher()

# Subscribe to events
publisher.subscribe("MoveMade", handle_move_made)

# Publish events
await publisher.publish(move_event)
```

### Logging
```python
from src.infrastructure import LoggingService

logging_service = LoggingService()
logger = logging_service.get_logger("game")
logger.info("Game started")
```

### Repository Usage
```python
from src.infrastructure import MemoryGameRepository

repo = MemoryGameRepository()
game_id = await repo.save_game(game)
loaded_game = await repo.load_game(game_id)
```

## Benefits

1. **Separation of Concerns**: External dependencies isolated from business logic
2. **Testability**: Easy to mock infrastructure components
3. **Flexibility**: Can swap implementations without affecting other layers
4. **Maintainability**: Clear structure for infrastructure concerns
5. **Scalability**: Easy to add new infrastructure components

## Dependencies

The infrastructure layer depends on:
- Domain layer (for interfaces and entities)
- Shared layer (for utilities and types)
- External libraries (database drivers, logging, etc.)

It does NOT depend on:
- Application layer
- Presentation layer

## Future Enhancements

### Database Implementations
- **PostgreSQLGameRepository**: PostgreSQL-based game persistence
- **RedisGameRepository**: Redis-based game persistence
- **MongoDBGameRepository**: MongoDB-based game persistence

### External Services
- **EmailNotificationService**: Email-based notifications
- **WebSocketNotificationService**: Real-time WebSocket notifications
- **SlackNotificationService**: Slack integration

### Caching
- **RedisCacheService**: Redis-based caching
- **MemoryCacheService**: In-memory caching

### Monitoring
- **MetricsService**: Application metrics collection
- **HealthCheckService**: Health monitoring 