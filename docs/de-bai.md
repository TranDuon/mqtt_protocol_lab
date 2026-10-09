# BUỔI THỰC HÀNH: LẬP TRÌNH PYTHON VỚI GIAO THỨC MQTT

## 1. Mục tiêu buổi thực hành

Sau buổi này, sinh viên cần:

- Hiểu cách một ứng dụng Python kết nối tới MQTT broker.
- Biết cách **publish** và **subscribe** dữ liệu qua topic.
- Biết tổ chức dữ liệu IoT theo mô hình **thiết bị – topic – payload**.
- Vận dụng MQTT để mô phỏng bài toán giám sát và điều khiển thiết bị IoT.
- Deadline nộp bài: **23:59 Thứ Bảy 10/10/2026**
- Hình thức nộp bài:
  - Qua link github, gửi link github vào nhóm zalo chung của lớp
  - Nội dung cần nộp: các file code, mà một file readme.md hướng dẫn chạy code và cách cấu hình MQTT broker

## 2. Yêu cầu môi trường

Sinh viên chuẩn bị:

- Python 3.x
- Thư viện paho-mqtt
- Cấu hình MQTT broker
- Một IDE hoặc VS Code

Cài đặt thư viện:

```bash
pip install paho-mqtt
```

## 3. Bài tập

### Bài 1. Ứng dụng gửi và nhận thông điệp MQTT cơ bản

#### Mục tiêu

Làm quen với cơ chế **publisher/subscriber** trong MQTT.

#### Yêu cầu

Viết 2 chương trình Python:

**Chương trình 1: Publisher**

- Kết nối tới MQTT broker.
- Gửi thông điệp lên topic:

  ```
  iot/lab/message
  ```

- Nội dung thông điệp gồm:
  - Họ tên sinh viên
  - Mã sinh viên
  - Nội dung chào mừng, ví dụ: "Xin chao tu client Python MQTT"

**Chương trình 2: Subscriber**

- Kết nối tới cùng broker.
- Đăng ký lắng nghe topic:

  ```
  iot/lab/message
  ```

- Khi nhận được thông điệp, in ra màn hình:
  - Topic
  - Nội dung
  - Thời điểm nhận

#### Yêu cầu đầu ra

Ví dụ:

```
Nhan duoc message:
Topic: iot/lab/message
Payload: Xin chao tu client Python MQTT - B23DCCN001 - Nguyen Van A
Time: 10:15:20
```

#### Gợi ý mở rộng

- Cho phép publisher gửi nhiều thông điệp liên tiếp.
- Cho subscriber chạy liên tục đến khi người dùng nhấn Ctrl+C.

#### Đánh giá

- Kết nối thành công broker
- Publish đúng topic
- Subscribe nhận đúng dữ liệu
- Hiển thị kết quả rõ ràng

---

### Bài 2. Mô phỏng cảm biến nhiệt độ và độ ẩm bằng MQTT

#### Mục tiêu

Mô phỏng thiết bị IoT gửi dữ liệu cảm biến định kỳ.

#### Yêu cầu

Viết 2 chương trình Python:

**Chương trình 1: Sensor Publisher**

- Mô phỏng một cảm biến gửi dữ liệu mỗi 3 giây.
- Topic gửi dữ liệu:

  ```
  iot/lab/sensor01/data
  ```

- Payload ở dạng JSON, gồm các trường:

  ```json
  {
    "device_id": "sensor01",
    "temperature": 28.5,
    "humidity": 65.2
  }
  ```

- Giá trị nhiệt độ và độ ẩm có thể sinh ngẫu nhiên trong khoảng hợp lý.

**Chương trình 2: Monitoring Subscriber**

- Subscribe topic:

  ```
  iot/lab/sensor01/data
  ```

- Nhận dữ liệu và:
  - In ra màn hình
  - Kiểm tra ngưỡng:
    - Nếu nhiệt độ > 35°C thì in cảnh báo "CANH BAO: Nhiet do cao"
    - Nếu độ ẩm < 40% thì in cảnh báo "CANH BAO: Do am thap"

#### Yêu cầu đầu ra

Ví dụ:

```
Device: sensor01
Temperature: 36.1 C
Humidity: 38.7 %
CANH BAO: Nhiet do cao
CANH BAO: Do am thap
```

#### Gợi ý mở rộng

- Hiển thị dữ liệu đẹp hơn theo từng dòng.
- Gửi dữ liệu của nhiều thiết bị khác nhau như sensor01, sensor02.

#### Đánh giá

- Payload đúng định dạng JSON
- Dữ liệu gửi tuần hoàn
- Subscriber phân tích được dữ liệu
- Cảnh báo đúng điều kiện

---

### Bài 3. Mô phỏng hệ thống điều khiển đèn thông minh qua MQTT

#### Mục tiêu

Xây dựng mô hình IoT hai chiều: **giám sát + điều khiển**.

#### Yêu cầu

Viết 2 chương trình Python:

**Chương trình 1: Smart Light Device**

Thiết bị đèn thông minh cần:

- Subscribe topic điều khiển:

  ```
  iot/lab/light01/cmd
  ```

- Publish trạng thái hiện tại lên topic:

  ```
  iot/lab/light01/status
  ```

Thiết bị nhận các lệnh:

- `"ON"` → chuyển trạng thái đèn thành bật
- `"OFF"` → chuyển trạng thái đèn thành tắt

Sau mỗi lệnh hợp lệ, thiết bị phải gửi trạng thái mới.

Ví dụ payload trạng thái:

```json
{
  "device_id": "light01",
  "status": "ON"
}
```

**Chương trình 2: Controller App**

- Cho người dùng nhập lệnh từ bàn phím:
  - ON
  - OFF
- Publish lệnh lên topic:

  ```
  iot/lab/light01/cmd
  ```

- Đồng thời subscribe topic trạng thái:

  ```
  iot/lab/light01/status
  ```

- Hiển thị trạng thái đèn sau khi nhận phản hồi.

#### Yêu cầu đầu ra

Ví dụ:

```
Nhap lenh: ON
Da gui lenh ON toi light01

Trang thai nhan duoc:
{"device_id":"light01","status":"ON"}
```

#### Gợi ý mở rộng

- Xử lý lệnh sai: nếu người dùng nhập khác ON/OFF thì báo lỗi.
- Thêm lệnh EXIT để kết thúc chương trình.
- Mô phỏng nhiều thiết bị: light01, fan01, pump01.

#### Đánh giá

- Điều khiển được thiết bị qua MQTT
- Thiết bị phản hồi đúng trạng thái
- Có cơ chế giao tiếp hai chiều
- Tổ chức topic hợp lý

---

## 4. Yêu cầu nộp bài

Mỗi sinh viên hoặc nhóm nộp:

- File `publisher_bai1.py`
- File `subscriber_bai1.py`
- File `sensor_publisher_bai2.py`
- File `monitor_subscriber_bai2.py`
- File `device_bai3.py`
- File `controller_bai3.py`

Kèm một file `README.txt` ngắn mô tả:

- Broker sử dụng
- Cách chạy từng chương trình
- Kết quả đạt được
