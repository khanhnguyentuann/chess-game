# Chess Game - Clean Architecture

Một ứng dụng chơi cờ vua được xây dựng với Clean Architecture, sử dụng Python và pygame.

## 📋 Mục lục

- [Tính năng](#tính-năng)
- [Cài đặt](#cài-đặt)
- [Chạy ứng dụng](#chạy-ứng-dụng)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
- [Cấu trúc project](#cấu-trúc-project)
- [Kiến trúc](#kiến-trúc)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## ✨ Tính năng

- ✅ **Clean Architecture** với Dependency Injection
- ✅ **Event-driven design** cho loose coupling
- ✅ **Domain-driven design** với entities và services
- ✅ **Move validation** và game rules đầy đủ
- ✅ **Move history tracking** và undo/redo
- ✅ **Comprehensive logging** và error handling
- ✅ **Configuration management** tập trung
- ✅ **Giao diện người dùng** với Pygame
- ✅ **Menu system** với các tùy chọn
- ✅ **Hướng dẫn chơi game** tích hợp
- ✅ **Save/Load game** với SaveManager
- ✅ **Window centering** tự động
- ✅ **Quit dialog** với Save & Continue options

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Python 3.8+
- pip

### Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Dependencies chính
- `pygame==2.5.2` - Giao diện game
- `python-chess==1.999` - Logic cờ vua
- `PyYAML==6.0.1` - Quản lý cấu hình
- `pydantic==2.5.0` - Data validation
- `aiofiles==23.2.0` - Async file operations

## 🎮 Chạy ứng dụng

### Chạy game
```bash
python main.py
```

Game sẽ khởi động trực tiếp với menu chính.

## 🎯 Hướng dẫn sử dụng

### Menu chính

Khi khởi động game, bạn sẽ thấy menu chính với các tùy chọn:

#### 1. New Game
- Bắt đầu một ván cờ mới
- Bàn cờ sẽ được reset về vị trí ban đầu
- Người chơi trắng đi trước

#### 2. Continue Game
- Tiếp tục ván cờ đã lưu (nếu có)
- Sử dụng SaveManager để load game

#### 3. Help
- Xem hướng dẫn chơi game
- Hiển thị các quy tắc cờ vua
- Hướng dẫn điều khiển

#### 4. Quit
- Thoát khỏi game

### Điều khiển trong game

#### Chuột
- **Click trái**: Chọn quân cờ hoặc di chuyển
- **Click vào quân cờ**: Chọn quân cờ (hiển thị màu vàng)
- **Click vào ô hợp lệ**: Di chuyển quân cờ (hiển thị màu xanh)

#### Bàn phím
- **R**: Reset game (bắt đầu lại)
- **U**: Undo move (hoàn tác nước đi)
- **ESC**: Quay lại menu chính

#### Quit Dialog
- **Continue**: Tiếp tục chơi
- **Save & Quit**: Lưu game và thoát về menu

### Cách chơi

#### 1. Chọn quân cờ
- Click vào quân cờ của bạn (màu trắng hoặc đen)
- Quân cờ được chọn sẽ hiển thị màu vàng
- Các ô có thể di chuyển đến sẽ hiển thị màu xanh

#### 2. Di chuyển quân cờ
- Click vào ô màu xanh để di chuyển
- Nếu di chuyển hợp lệ, quân cờ sẽ được di chuyển
- Lượt chơi sẽ chuyển sang người chơi khác

#### 3. Luật chơi cơ bản
- **Tốt (Pawn)**: Di chuyển thẳng về phía trước 1 ô
- **Mã (Knight)**: Di chuyển theo hình chữ L
- **Tượng (Bishop)**: Di chuyển theo đường chéo
- **Xe (Rook)**: Di chuyển theo hàng ngang hoặc dọc
- **Hậu (Queen)**: Di chuyển theo mọi hướng
- **Vua (King)**: Di chuyển 1 ô theo mọi hướng

#### 4. Các trạng thái đặc biệt
- **Chiếu (Check)**: Vua bị tấn công
- **Chiếu hết (Checkmate)**: Vua bị chiếu và không thể thoát
- **Hòa (Draw)**: Không có nước đi hợp lệ hoặc lặp lại vị trí

### Giao diện game

#### Thông tin hiển thị
- **Current Player**: Người chơi hiện tại
- **Selected Square**: Ô được chọn (nếu có)
- **Last Move**: Nước đi cuối cùng

#### Màu sắc
- **Ô trắng/nâu**: Bàn cờ
- **Màu vàng**: Quân cờ được chọn
- **Màu xanh**: Ô có thể di chuyển đến
- **Màu đen**: Nền giao diện

## 📁 Cấu trúc project

```
chess-game/
├── src/
│   ├── application/          # Application layer
│   │   ├── commands/         # Command pattern
│   │   │   ├── base_command.py
│   │   │   └── move_command.py
│   │   ├── use_cases/        # Use cases
│   │   │   └── make_move.py
│   │   ├── handlers/         # Event handlers (empty)
│   │   └── queries/          # Queries (empty)
│   ├── domain/               # Domain layer
│   │   ├── entities/         # Domain entities
│   │   │   ├── board.py
│   │   │   ├── game.py
│   │   │   └── move_history.py
│   │   ├── events/           # Domain events
│   │   │   ├── event_dispatcher.py
│   │   │   └── game_events.py
│   │   ├── interfaces/       # Domain interfaces
│   │   │   ├── repositories.py
│   │   │   └── services.py
│   │   └── services/         # Domain services
│   │       └── move_validator.py
│   ├── infrastructure/       # Infrastructure layer
│   │   ├── repositories/     # Data access
│   │   │   ├── memory_game_repo.py
│   │   │   └── memory_move_history_repo.py
│   │   ├── ui/              # UI implementations
│   │   │   └── pygame/
│   │   └── services/        # External services
│   │       └── dummy_notification_service.py
│   ├── presentation/         # Presentation layer
│   │   ├── controllers/      # Controllers (empty)
│   │   ├── presenters/       # Presenters (empty)
│   │   ├── viewmodels/       # ViewModels (empty)
│   │   └── ui/              # UI components
│   │       ├── chess_game_ui.py    # Game UI
│   │       ├── menu_system.py      # Menu system
│   │       └── piece_renderer.py   # Piece rendering
│   └── shared/              # Shared components
│       ├── config/          # Configuration
│       │   └── game_config.py
│       ├── types/           # Type definitions
│       │   ├── enums.py
│       │   └── type_definitions.py
│       ├── utils/           # Utilities
│       │   ├── logging_utils.py
│       │   └── save_manager.py
│       └── exceptions/      # Custom exceptions
│           └── game_exceptions.py
├── saves/                   # Save game files
│   └── saved_game.json     # Current save file
├── main.py                 # Main entry point
├── requirements.txt        # Dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🏗️ Kiến trúc

### Clean Architecture Layers

#### 1. Domain Layer (`src/domain/`)
- **Entities**: Game, Board, MoveHistory
- **Events**: Game events và event dispatching
- **Services**: Move validation, game rules
- **Interfaces**: Repository contracts

#### 2. Application Layer (`src/application/`)
- **Use Cases**: MakeMoveUseCase
- **Commands**: Command pattern implementation
- **Handlers**: Event handlers (currently empty)
- **Queries**: Query handlers (currently empty)

#### 3. Infrastructure Layer (`src/infrastructure/`)
- **Repositories**: Memory-based data storage
- **UI**: Pygame implementation
- **Services**: External service integrations

#### 4. Presentation Layer (`src/presentation/`)
- **Controllers**: Game controllers (currently empty)
- **Presenters**: Data presentation (currently empty)
- **ViewModels**: View models (currently empty)
- **UI**: User interface components

### Dependency Injection

Project sử dụng Service Container pattern để quản lý dependencies:

```python
from src.composition_root import get_container

container = get_container()
move_validator = container.get("move_validator")
game_repo = container.get("game_repository")
```

### Event System

Event-driven architecture cho loose coupling:

```python
from src.domain.events.game_events import EventType, GameEvent

# Publish event
event_dispatcher.publish(GameEvent.game_started(game_id))

# Subscribe to events
event_dispatcher.subscribe(EventType.MOVE_MADE, handle_move)
```

### Save Manager

Hệ thống lưu/tải game với SaveManager:

```python
from src.shared.utils.save_manager import save_manager

# Save game
data = game.to_dict()
save_manager.save_game(data)

# Load game
data = save_manager.load_game()
game = Game.from_dict(data)
```

## 🛠️ Development

### Thêm use case mới

1. Tạo file trong `src/application/use_cases/`
2. Implement interface từ domain layer
3. Register trong composition root
4. Test với unit tests

### Thêm domain event

1. Định nghĩa event type trong `src/domain/events/game_events.py`
2. Tạo event class
3. Publish từ domain entities
4. Handle trong application layer

### Configuration

Cấu hình được quản lý trong `src/shared/config/game_config.py`:

```python
from src.shared.config.game_config import GameConfig

config = GameConfig()
print(config.ui.board_size)  # 640
print(config.ai.skill_level)  # 10
```

### Code Formatting

Format code với Black:

```bash
black src/ main.py
```

## 📝 Logging

Logging được cấu hình tự động:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Game started")
```

Logs được lưu trong:
- Console output (mặc định)
- File logs (nếu cấu hình)

## 🚨 Troubleshooting

### Lỗi thường gặp

#### 1. ImportError: No module named 'chess'
```bash
pip install python-chess
```

#### 2. Pygame warning về pkg_resources
- Đây là warning từ pygame, không ảnh hưởng đến chức năng
- Có thể bỏ qua hoặc update setuptools

#### 3. ModuleNotFoundError
```bash
# Đảm bảo đang ở thư mục gốc của project
cd chess-game
python main.py
```

#### 4. "Invalid selection"
- Bạn đã click vào quân cờ không phải của mình
- Hoặc click vào ô trống khi chưa chọn quân cờ

#### 5. "Invalid move"
- Nước đi không hợp lệ theo luật cờ vua
- Hoặc nước đi sẽ khiến vua bị chiếu

#### 6. "No moves to undo"
- Không có nước đi nào để hoàn tác

### Debug

Để debug, set logging level thành DEBUG:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

Hoặc sử dụng environment variable:

```bash
export CHESS_LOG_LEVEL=DEBUG
python main.py
```

### Khắc phục
- Đọc kỹ hướng dẫn trong menu Help
- Đảm bảo click đúng quân cờ của mình
- Kiểm tra các ô màu xanh trước khi di chuyển

## 🤝 Contributing

1. Fork project
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📄 License

MIT License - xem file LICENSE để biết thêm chi tiết.

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra `requirements.txt` đã được cài đặt
2. Chạy `python main.py` để kiểm tra
3. Xem logs trong console để debug
4. Đọc file `README.md` để biết thêm chi tiết
