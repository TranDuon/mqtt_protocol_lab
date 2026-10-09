# Lab MQTT – Lập trình Python với giao thức MQTT

Sinh viên: **Trần Đăng Dương** – MSSV: **B23DCCN227**

Bài thực hành gồm 3 bài, mỗi bài là một cặp chương trình Python giao tiếp với nhau qua MQTT broker:

| Bài | Folder | Chương trình | Topic | Nội dung |
|---|---|---|---|---|
| 1 | [bai1_messaging](bai1_messaging/) | `publisher_bai1.py`, `subscriber_bai1.py` | `iot/lab/message` | Gửi/nhận thông điệp cơ bản |
| 2 | [bai2_sensor](bai2_sensor/) | `sensor_publisher_bai2.py`, `monitor_subscriber_bai2.py` | `iot/lab/sensor01/data` | Cảm biến gửi JSON mỗi 3 giây, giám sát và cảnh báo ngưỡng |
| 3 | [bai3_smart_light](bai3_smart_light/) | `device_bai3.py`, `controller_bai3.py` | `iot/lab/light01/cmd`, `iot/lab/light01/status` | Điều khiển đèn thông minh hai chiều |

Mỗi folder bài có `README.md` riêng mô tả yêu cầu, luồng dữ liệu, cách chạy và output thực tế.

---

## 1. Công nghệ sử dụng

| Thành phần | Phiên bản | Vai trò |
|---|---|---|
| Python | 3.x (đã chạy thử trên 3.13.6) | Ngôn ngữ lập trình |
| [paho-mqtt](https://pypi.org/project/paho-mqtt/) | 2.1.0 | Thư viện MQTT client (đề bài yêu cầu) |
| [Eclipse Mosquitto](https://mosquitto.org/) | 2.1.2 | MQTT broker chạy trên máy local |
| MQTT | 3.1.1, QoS 1 | Giao thức publish/subscribe |
| JSON | – | Định dạng payload Bài 2 và Bài 3 |

## 2. Kiến trúc

Các chương trình **không kết nối trực tiếp với nhau**. Tất cả chỉ kết nối tới broker và trao đổi qua topic:

```
                       ┌────────────────────────────────┐
                       │  Mosquitto broker 127.0.0.1:1883 │
                       └────────────────────────────────┘
                          ▲                          │
Bài 1  publisher_bai1 ────┘ iot/lab/message          └──▶ subscriber_bai1

Bài 2  sensor_publisher ──▶ iot/lab/sensor01/data (JSON, 3s) ──▶ monitor_subscriber (+ cảnh báo)

Bài 3  controller ──▶ iot/lab/light01/cmd    ("ON"/"OFF") ──▶ device_bai3
       controller ◀── iot/lab/light01/status (JSON)       ◀── device_bai3
```

Quy ước topic theo mô hình **thiết bị – topic – payload**: `iot/lab/<device_id>/<loại>` với loại là `data`, `cmd` hoặc `status`. Thêm thiết bị mới (sensor02, fan01, pump01) chỉ cần truyền `device_id` khác, không phải sửa code.

## 3. Luồng MQTT

```
Bài 1:  publisher ──PUBLISH "Xin chao..."──▶ broker ──▶ subscriber in Topic/Payload/Time

Bài 2:  sensor ──PUBLISH {"device_id","temperature","humidity"}──▶ broker ──▶ monitor
        monitor: json.loads → in dữ liệu → nhiệt độ > 35 hoặc độ ẩm < 40 thì cảnh báo

Bài 3:  controller ──PUBLISH "ON"──▶ iot/lab/light01/cmd ──▶ device (đổi trạng thái)
        device ──PUBLISH {"device_id":"light01","status":"ON"}──▶ iot/lab/light01/status ──▶ controller
```

## 4. Cấu trúc project

```
mqtt_protocol/
├── README.md                 # file này: tổng quan, cài đặt broker, cách chạy
├── README.txt                # bản tóm tắt ngắn theo mục 4 của đề
├── requirements.txt          # paho-mqtt==2.1.0
├── mosquitto.conf            # cấu hình broker cho bài lab
├── common/
│   └── config.py             # dùng chung: broker host/port, họ tên + MSSV, topic, hàm tạo client
├── bai1_messaging/           # Bài 1: publisher_bai1.py, subscriber_bai1.py, README.md
├── bai2_sensor/              # Bài 2: sensor_publisher_bai2.py, monitor_subscriber_bai2.py, README.md
├── bai3_smart_light/         # Bài 3: device_bai3.py, controller_bai3.py, README.md
└── docs/
    ├── de-bai.md / de-bai.docx      # đề bài gốc
    ├── kien-thuc-mqtt.md            # kiến thức MQTT và paho-mqtt dùng trong lab
    ├── ket-qua-kiem-thu.md          # checklist đối chiếu đề bài và kết quả test
    └── huong-dan-tu-lam-lai.md      # hướng dẫn tự làm lại một bài MQTT tương tự
```

`common/config.py` chứa những gì cả 3 bài cùng dùng: địa chỉ broker, thông tin sinh viên, các hàm tạo topic, `create_client()`, `connect_or_exit()` và `publish_confirmed()`. Mỗi script tự thêm thư mục gốc lab vào `sys.path` nên có thể chạy từ bất kỳ thư mục nào.

---

## 5. Cài đặt và cấu hình MQTT broker (Mosquitto)

### 5.1. Cài Mosquitto trên Windows

Cách 1 – winget (PowerShell):

```powershell
winget install --id EclipseFoundation.Mosquitto -e
```

Cách 2 – tải bộ cài `mosquitto-2.x-install-windows-x64.exe` từ https://mosquitto.org/download/ và cài mặc định.

Mosquitto được cài vào `C:\Program Files\mosquitto\` (thư mục này **không** nằm trong PATH, nên khi gọi lệnh phải ghi đường dẫn đầy đủ). Bộ cài cũng đăng ký một Windows service tên `mosquitto` tự chạy khi khởi động máy.

### 5.2. File cấu hình `mosquitto.conf`

```conf
listener 1883 127.0.0.1
allow_anonymous true
```

| Dòng | Ý nghĩa |
|---|---|
| `listener 1883 127.0.0.1` | Nghe cổng 1883 (cổng MQTT mặc định, không TLS), chỉ nhận kết nối từ chính máy này. Muốn máy khác trong mạng LAN kết nối được thì đổi thành `listener 1883` và mở cổng 1883 trên Windows Firewall. |
| `allow_anonymous true` | Cho phép client kết nối không cần username/password. Từ Mosquitto 2.0, nếu đã khai báo `listener` mà không có dòng này thì broker **từ chối** client ẩn danh (lỗi `Not authorized`). |

### 5.3. Chạy broker

**Cách A – dùng service có sẵn (đơn giản nhất).** Sau khi cài, service `mosquitto` đã chạy ở chế độ mặc định: nghe `localhost:1883`, cho phép ẩn danh từ máy local. Như vậy là đủ cho bài lab. Kiểm tra:

```powershell
Get-Service mosquitto            # Status phải là Running
netstat -ano | findstr :1883     # phải thấy 127.0.0.1:1883 LISTENING
```

**Cách B – chạy broker bằng file cấu hình của repo (thấy log trực tiếp).** Phải tắt service trước vì hai broker không thể cùng giữ cổng 1883 (mở PowerShell bằng *Run as Administrator*):

```powershell
net stop mosquitto
& "C:\Program Files\mosquitto\mosquitto.exe" -c mosquitto.conf -v
```

`-v` in log chi tiết: thấy từng client kết nối, subscribe, publish. Rất hữu ích khi debug. Bật lại service sau khi xong: `net start mosquitto`.

### 5.4. Kiểm tra broker trước khi chạy code Python

Mở 2 terminal:

```powershell
# Terminal 1: nghe mọi topic của lab
& "C:\Program Files\mosquitto\mosquitto_sub.exe" -h 127.0.0.1 -t "iot/lab/#" -v

# Terminal 2: gửi thử
& "C:\Program Files\mosquitto\mosquitto_pub.exe" -h 127.0.0.1 -t iot/lab/test -m hello
```

Terminal 1 in ra `iot/lab/test hello` là broker hoạt động.

### 5.5. Dùng broker khác (tùy chọn)

Địa chỉ broker đọc từ biến môi trường, không cần sửa code:

```powershell
$env:MQTT_HOST = "broker.hivemq.com"   # PowerShell;  cmd: set MQTT_HOST=broker.hivemq.com
$env:MQTT_PORT = "1883"
```

Lưu ý: broker công cộng ai cũng publish được vào cùng topic `iot/lab/...`, nên có thể nhận lẫn message của người khác. Bài lab dùng broker local làm cấu hình chính.

---

## 6. Cài môi trường Python

Tại thư mục `mqtt_protocol`:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Nếu PowerShell chặn `activate` (lỗi *running scripts is disabled*), chạy một lần `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, hoặc bỏ qua bước activate và gọi trực tiếp `.venv\Scripts\python` thay cho `python` trong các lệnh bên dưới.

Họ tên và MSSV dùng trong Bài 1 nằm ở `common/config.py` (`STUDENT_NAME`, `STUDENT_ID`).

## 7. Cách chạy

**Nguyên tắc: chạy bên nhận (subscriber/device) trước, bên gửi sau.** Broker không lưu message cho subscriber chưa kết nối, nên nếu chạy publisher trước thì message gửi đi sẽ không ai nhận.

Mỗi chương trình chạy trong một terminal riêng (đã activate venv, đứng ở thư mục `mqtt_protocol`):

```powershell
# Bài 1
python bai1_messaging/subscriber_bai1.py            # terminal 1, Ctrl+C để dừng
python bai1_messaging/publisher_bai1.py             # terminal 2, gửi 5 message rồi tự thoát (-n 10 -i 2 để đổi)

# Bài 2
python bai2_sensor/monitor_subscriber_bai2.py       # terminal 1
python bai2_sensor/sensor_publisher_bai2.py         # terminal 2, gửi mỗi 3 giây, Ctrl+C để dừng

# Bài 3
python bai3_smart_light/device_bai3.py              # terminal 1
python bai3_smart_light/controller_bai3.py          # terminal 2, gõ ON / OFF / EXIT
```

Các tùy chọn mở rộng (nhiều thiết bị, nhiều sensor...) xem trong README của từng bài.

## 8. Cách kiểm tra

- Mở thêm một terminal chạy `mosquitto_sub -h 127.0.0.1 -t "iot/lab/#" -v` (xem mục 5.4) để thấy **mọi** message đi qua broker, kể cả lệnh và trạng thái Bài 3.
- Có thể đóng vai một bên bằng `mosquitto_pub`, ví dụ gửi dữ liệu nóng cho monitor Bài 2:
  ```powershell
  & "C:\Program Files\mosquitto\mosquitto_pub.exe" -h 127.0.0.1 -t iot/lab/sensor01/data -m '{\"device_id\":\"sensor01\",\"temperature\":36.1,\"humidity\":38.7}'
  ```
  (Cú pháp trên cho Windows PowerShell 5.1. Với PowerShell 7.3 trở lên thì bỏ các dấu `\` trước dấu nháy kép.)
- Các ca test chi tiết và kết quả: [docs/ket-qua-kiem-thu.md](docs/ket-qua-kiem-thu.md).

## 9. Kết quả đạt được

- Bài 1: subscriber nhận đúng thông điệp `Xin chao tu client Python MQTT - B23DCCN227 - Tran Dang Duong` và in Topic, Payload, Time; publisher gửi được nhiều message liên tiếp.
- Bài 2: sensor gửi JSON đúng 3 trường mỗi 3 giây; monitor phân tích JSON, in dữ liệu và cảnh báo đúng ngưỡng (nhiệt độ > 35 °C, độ ẩm < 40 %); payload hỏng không làm sập monitor; hỗ trợ nhiều sensor.
- Bài 3: controller điều khiển được đèn qua MQTT, thiết bị phản hồi trạng thái mới sau mỗi lệnh hợp lệ; lệnh sai bị từ chối; có lệnh EXIT; hỗ trợ nhiều thiết bị (light01, fan01, pump01).
- Tất cả chương trình báo lỗi rõ ràng khi broker không chạy hoặc từ chối kết nối, tự kết nối lại khi broker khởi động lại, và thoát gọn khi nhấn Ctrl+C.

Output thực tế của từng bài nằm trong README của folder bài.

## 10. Xử lý sự cố

| Hiện tượng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| `LOI: Khong ket noi duoc MQTT broker tai 127.0.0.1:1883 ... refused` | Broker chưa chạy | `Get-Service mosquitto`; `net start mosquitto` hoặc chạy cách B ở mục 5.3 |
| `LOI: Broker tu choi ket noi: Not authorized` | Broker không cho client ẩn danh | Thêm `allow_anonymous true` vào file cấu hình broker |
| `ModuleNotFoundError: No module named 'paho'` | Chưa cài thư viện hoặc chưa activate venv | `.venv\Scripts\activate` rồi `pip install -r requirements.txt` |
| Subscriber không nhận được gì | Chạy publisher trước subscriber; sai topic; hai bên dùng broker khác nhau | Chạy subscriber trước; kiểm tra bằng `mosquitto_sub -t "iot/lab/#" -v` |
| Nhận message trùng hoặc lạ | Còn một chương trình cũ chạy ngầm cùng topic | Tắt các terminal/tiến trình Python cũ |
| Bài 3: `Khong nhan duoc phan hoi tu light01` | `device_bai3.py` chưa chạy hoặc khác `device_id` | Chạy device trước, cùng `device_id` với controller |
| `Error: Only one usage of each socket address` khi chạy `mosquitto.exe` | Service mosquitto đang giữ cổng 1883 | `net stop mosquitto` (quyền Administrator) |

## 11. Tài liệu kèm theo

- [docs/de-bai.md](docs/de-bai.md) – đề bài.
- [docs/kien-thuc-mqtt.md](docs/kien-thuc-mqtt.md) – kiến thức MQTT và paho-mqtt áp dụng trong lab.
- [docs/ket-qua-kiem-thu.md](docs/ket-qua-kiem-thu.md) – checklist đối chiếu đề và kết quả kiểm thử.
- [docs/huong-dan-tu-lam-lai.md](docs/huong-dan-tu-lam-lai.md) – các bước tự làm lại một bài MQTT tương tự.
