# Hướng dẫn sử dụng Chess Game

## Khởi động game

### Cách 1: Chạy trực tiếp với menu (Khuyến nghị)
```bash
python run_ui.py
```

### Cách 2: Chạy với lựa chọn
```bash
python main.py
```
Sau đó chọn:
- `1`: Chạy demo console
- `2`: Chạy game với giao diện
- `3`: Thoát

## Menu chính

Khi khởi động game, bạn sẽ thấy menu chính với các tùy chọn:

### 1. New Game
- Bắt đầu một ván cờ mới
- Bàn cờ sẽ được reset về vị trí ban đầu
- Người chơi trắng đi trước

### 2. Continue Game
- Tiếp tục ván cờ đã lưu (nếu có)
- Hiện tại đang phát triển tính năng này

### 3. Help
- Xem hướng dẫn chơi game
- Hiển thị các quy tắc cờ vua
- Hướng dẫn điều khiển

### 4. Quit
- Thoát khỏi game

## Điều khiển trong game

### Chuột
- **Click trái**: Chọn quân cờ hoặc di chuyển
- **Click vào quân cờ**: Chọn quân cờ (hiển thị màu vàng)
- **Click vào ô hợp lệ**: Di chuyển quân cờ (hiển thị màu xanh)

### Bàn phím
- **R**: Reset game (bắt đầu lại)
- **U**: Undo move (hoàn tác nước đi)
- **ESC**: Quay lại menu chính

## Cách chơi

### 1. Chọn quân cờ
- Click vào quân cờ của bạn (màu trắng hoặc đen)
- Quân cờ được chọn sẽ hiển thị màu vàng
- Các ô có thể di chuyển đến sẽ hiển thị màu xanh

### 2. Di chuyển quân cờ
- Click vào ô màu xanh để di chuyển
- Nếu di chuyển hợp lệ, quân cờ sẽ được di chuyển
- Lượt chơi sẽ chuyển sang người chơi khác

### 3. Luật chơi cơ bản
- **Tốt (Pawn)**: Di chuyển thẳng về phía trước 1 ô
- **Mã (Knight)**: Di chuyển theo hình chữ L
- **Tượng (Bishop)**: Di chuyển theo đường chéo
- **Xe (Rook)**: Di chuyển theo hàng ngang hoặc dọc
- **Hậu (Queen)**: Di chuyển theo mọi hướng
- **Vua (King)**: Di chuyển 1 ô theo mọi hướng

### 4. Các trạng thái đặc biệt
- **Chiếu (Check)**: Vua bị tấn công
- **Chiếu hết (Checkmate)**: Vua bị chiếu và không thể thoát
- **Hòa (Draw)**: Không có nước đi hợp lệ hoặc lặp lại vị trí

## Giao diện game

### Thông tin hiển thị
- **Current Player**: Người chơi hiện tại
- **Moves**: Số nước đi đã thực hiện
- **State**: Trạng thái game (playing, checkmate, draw)

### Màu sắc
- **Ô trắng/nâu**: Bàn cờ
- **Màu vàng**: Quân cờ được chọn
- **Màu xanh**: Ô có thể di chuyển đến
- **Màu đen**: Nền giao diện

## Xử lý lỗi

### Lỗi thường gặp

1. **"Invalid selection"**
   - Bạn đã click vào quân cờ không phải của mình
   - Hoặc click vào ô trống khi chưa chọn quân cờ

2. **"Invalid move"**
   - Nước đi không hợp lệ theo luật cờ vua
   - Hoặc nước đi sẽ khiến vua bị chiếu

3. **"No moves to undo"**
   - Không có nước đi nào để hoàn tác

### Khắc phục
- Đọc kỹ hướng dẫn trong menu Help
- Đảm bảo click đúng quân cờ của mình
- Kiểm tra các ô màu xanh trước khi di chuyển

## Tính năng nâng cao

### Clean Architecture
Game được xây dựng theo kiến trúc Clean Architecture:
- **Domain Layer**: Logic nghiệp vụ cờ vua
- **Application Layer**: Use cases và commands
- **Infrastructure Layer**: Lưu trữ và external services
- **Presentation Layer**: Giao diện người dùng

### Event-driven Design
- Hệ thống event để xử lý các thay đổi trong game
- Loose coupling giữa các component

### Dependency Injection
- Service container để quản lý dependencies
- Dễ dàng test và maintain

## Phát triển

### Thêm tính năng mới
1. Tạo use case trong `src/application/use_cases/`
2. Implement domain logic trong `src/domain/`
3. Cập nhật UI trong `src/presentation/ui/`
4. Test với `python test_basic.py`

### Cấu hình
- Chỉnh sửa cấu hình trong `src/shared/config/game_config.py`
- Thay đổi theme, kích thước bàn cờ, v.v.

## Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra `requirements.txt` đã được cài đặt
2. Chạy `python test_basic.py` để kiểm tra
3. Xem logs trong console để debug
4. Đọc file `README.md` để biết thêm chi tiết 