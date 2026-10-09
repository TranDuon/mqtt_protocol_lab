# Kết quả kiểm thử và đối chiếu đề bài

Môi trường kiểm thử: Windows 11, Python 3.13.6, paho-mqtt 2.1.0, Mosquitto 2.1.2 (service local `127.0.0.1:1883`).

## 1. Đối chiếu yêu cầu đề bài

### Yêu cầu chung (mục 1, 2, 4 của đề)

- [x] Python 3.x + thư viện paho-mqtt
- [x] Cấu hình MQTT broker (Mosquitto, file `mosquitto.conf`, hướng dẫn trong `README.md` mục 5)
- [x] Đủ 6 file đúng tên: `publisher_bai1.py`, `subscriber_bai1.py`, `sensor_publisher_bai2.py`, `monitor_subscriber_bai2.py`, `device_bai3.py`, `controller_bai3.py`
- [x] `README.md` hướng dẫn chạy code và cách cấu hình MQTT broker
- [x] `README.txt` ngắn: broker sử dụng, cách chạy từng chương trình, kết quả đạt được
- [ ] Đẩy lên GitHub và gửi link vào nhóm Zalo của lớp (hạn 23:59 thứ Bảy 10/10/2026)

### Bài 1

- [x] Publisher kết nối broker, gửi lên `iot/lab/message`
- [x] Nội dung gồm họ tên, MSSV, lời chào: `Xin chao tu client Python MQTT - B23DCCN227 - Tran Dang Duong`
- [x] Subscriber kết nối cùng broker, subscribe `iot/lab/message`
- [x] Khi nhận in ra Topic, nội dung (Payload), thời điểm nhận (Time) đúng format mẫu
- [x] Mở rộng: gửi nhiều thông điệp liên tiếp (`-n`, `-i`)
- [x] Mở rộng: subscriber chạy liên tục đến khi Ctrl+C

### Bài 2

- [x] Sensor gửi mỗi 3 giây lên `iot/lab/sensor01/data`
- [x] Payload JSON gồm `device_id`, `temperature`, `humidity`
- [x] Giá trị ngẫu nhiên trong khoảng hợp lý (25–40 °C, 30–80 %)
- [x] Monitor subscribe `iot/lab/sensor01/data`, in dữ liệu
- [x] Nhiệt độ > 35 → `CANH BAO: Nhiet do cao`
- [x] Độ ẩm < 40 → `CANH BAO: Do am thap`
- [x] Mở rộng: hiển thị từng dòng kèm thời gian và topic
- [x] Mở rộng: nhiều thiết bị (sensor01, sensor02; monitor hỗ trợ wildcard `+`)

### Bài 3

- [x] Device subscribe `iot/lab/light01/cmd`, publish `iot/lab/light01/status`
- [x] `ON` → bật, `OFF` → tắt; sau mỗi lệnh hợp lệ gửi trạng thái mới `{"device_id":"light01","status":"..."}`
- [x] Controller nhập lệnh từ bàn phím, publish lên `/cmd`
- [x] Controller subscribe `/status` và hiển thị trạng thái nhận được
- [x] Mở rộng: lệnh khác ON/OFF bị báo lỗi
- [x] Mở rộng: lệnh EXIT
- [x] Mở rộng: nhiều thiết bị (light01, fan01, pump01)

## 2. Các ca kiểm thử đã chạy

| # | Ca kiểm thử | Cách thực hiện | Kết quả |
|---|---|---|---|
| 1 | Broker hoạt động | `mosquitto_sub -t "iot/lab/#"` + `mosquitto_pub -t iot/lab/test -m hello` | Nhận `iot/lab/test hello` |
| 2 | Subscriber Bài 1 nhận message gửi tay | `mosquitto_pub -t iot/lab/message` | In đúng 4 dòng |
| 3 | Bài 1 đầu cuối | Publisher `-n 3` | Subscriber nhận đủ 3, payload đúng; publisher tự thoát |
| 4 | Chu kỳ Bài 2 | Sensor mặc định chạy ~8 giây | Gửi lúc :58, :01, :04 – đúng 3 giây |
| 5 | Cảnh báo Bài 2 | Gửi tay 36.1 / 38.7 | Cả 2 cảnh báo |
| 6 | Giá trị biên | Gửi tay 35.0 / 40.0 | Không cảnh báo (đề dùng `>` và `<`) |
| 7 | Chỉ một cảnh báo | Gửi tay 20.5 / 39.9 | Chỉ cảnh báo độ ẩm |
| 8 | Payload không phải JSON | Gửi tay `du lieu loi` | In lỗi, monitor vẫn chạy |
| 9 | JSON thiếu trường | Gửi tay `{"device_id":"sensor01","temperature":30}` | In lỗi, monitor vẫn chạy |
| 10 | Nhiều sensor + wildcard | Sensor `sensor01 sensor02`, monitor `+` | Nhận và cảnh báo cho cả 2 sensor |
| 11 | Device nhận lệnh | `mosquitto_pub` gửi `ON`, `off`, `BLINK` | ON/OFF đổi trạng thái + gửi status; BLINK bị bỏ qua, không gửi status |
| 12 | Bài 3 đầu cuối | Controller nhận `ON`, `OFF`, `BLINK`, `EXIT` | Đúng thứ tự output mẫu; BLINK báo lỗi; EXIT thoát |
| 13 | Nhiều thiết bị | Device `light01 fan01 pump01`, controller `pump01` | Chỉ pump01 đổi trạng thái và phản hồi |
| 14 | Thiết bị không chạy | Controller gửi `ON` khi không có device | Báo không nhận được phản hồi sau 3 giây |
| 15 | Broker không chạy | `MQTT_PORT=1999` | Một dòng lỗi rõ ràng, exit code 1, không traceback |
| 16 | Broker từ chối (không cho ẩn danh) | Broker tạm với `allow_anonymous false` | In `Not authorized` một lần rồi thoát |
| 17 | Broker tắt giữa chừng rồi bật lại | Tắt broker khi sensor đang gửi | Báo mất kết nối, báo từng lần gửi lỗi, tự kết nối lại và gửi tiếp |
| 18 | Ctrl+C | Gửi Ctrl+C thật (`GenerateConsoleCtrlEvent`) | subscriber, publisher, sensor, monitor, device thoát gọn, exit code 0 |
| 19 | Thoát controller bằng EOF | Hết dữ liệu vào stdin | Thoát gọn |
| 20 | Chạy từ các thư mục khác nhau | `python bai1_messaging/x.py` từ gốc và `cd bai2_sensor; python x.py` | Đều import được `common/config.py` |

**Kiểm tra thủ công còn lại:** nhấn Ctrl+C khi controller Bài 3 đang chờ `Nhap lenh:`. Code đã bắt cả `KeyboardInterrupt` và `EOFError`, nhưng Ctrl+C giả lập bằng API không ngắt được `input()` đang chờ bàn phím (đã kiểm chứng bằng một script chỉ có `input()`), nên ca này cần bấm phím thật.

## 3. Lỗi tìm thấy khi kiểm thử và cách sửa

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| Broker từ chối kết nối thì subscriber in `Not authorized` lặp mãi | `loop_forever()` tự kết nối lại khi CONNACK thất bại | Gọi `client.disconnect()` trong nhánh thất bại của `on_connect` |
| Broker tắt giữa chừng thì sensor crash với `RuntimeError: The client is not currently connected` | `wait_for_publish()` ném lỗi khi mất kết nối | Hàm `publish_confirmed()` bắt lỗi và kiểm tra `is_published()` |
| Controller nhận mỗi trạng thái 2 lần (chỉ khi test) | Một tiến trình `device_bai3.py` từ lần test trước vẫn chạy ngầm: trên Windows `python.exe` của venv là launcher sinh tiến trình con, tắt launcher không tắt tiến trình con | Không phải lỗi code; tắt cả cây tiến trình (`taskkill /T`) sau mỗi lần test |
