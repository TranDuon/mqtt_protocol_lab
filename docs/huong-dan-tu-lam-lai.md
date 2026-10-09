# Nếu tự làm lại từ đầu

Hướng dẫn này tóm tắt cách tiếp cận một bài MQTT, để có thể tự làm một bài tương tự mà không cần nhìn code mẫu.

## 1. Đọc đề như thế nào

Đọc đề với 4 câu hỏi, và ghi câu trả lời ra giấy trước khi viết code:

1. **Có những chương trình nào?** Mỗi chương trình là một MQTT client.
2. **Mỗi chương trình gửi gì, nhận gì?** Gạch chân các động từ "gửi/publish", "nhận/subscribe/lắng nghe".
3. **Topic và payload chính xác là gì?** Copy nguyên văn: tên topic, tên trường JSON, chuỗi in ra màn hình. Đây là thứ người chấm so khớp.
4. **Tiêu chí đánh giá là gì?** Mục "Đánh giá" chính là checklist nghiệm thu.

Ghi riêng các phần "Gợi ý mở rộng" và làm sau khi phần bắt buộc đã chạy.

## 2. Xác định các thành phần cần implement

Lập bảng như sau cho từng bài:

| Chương trình | Publish lên | Subscribe | Payload | Hành vi |
|---|---|---|---|---|
| sensor | `iot/lab/sensor01/data` | – | JSON 3 trường | lặp mỗi 3 giây |
| monitor | – | `iot/lab/sensor01/data` | – | parse JSON, so ngưỡng |

Cột "Hành vi" cho biết chương trình cần vòng lặp, cần đọc bàn phím hay chỉ ngồi chờ message.

## 3. Thiết kế kiến trúc

- Vẽ sơ đồ: các client ở hai bên, broker ở giữa, mũi tên ghi tên topic.
- Mũi tên chỉ đi **một chiều** (Bài 1, 2) thì một bên chỉ pub, một bên chỉ sub.
- Có **hai chiều** (Bài 3) thì cần **hai topic** riêng: một cho lệnh, một cho phản hồi. Đừng dùng chung một topic cho cả hai chiều, nếu không thiết bị sẽ nhận lại chính trạng thái nó vừa gửi.
- Gom phần dùng chung (địa chỉ broker, cách tạo client, tên topic) vào một module cấu hình.

## 4. Xác định Publisher / Subscriber / Broker

- **Broker** luôn là một thành phần riêng (Mosquitto), không phải code của mình.
- Chương trình **tạo ra dữ liệu hoặc ra lệnh** → publisher.
- Chương trình **phản ứng với dữ liệu** → subscriber.
- Chương trình vừa nhận lệnh vừa báo kết quả (thiết bị) → cả hai.

## 5. Đặt tên topic

- Phân cấp từ chung đến riêng: `<dự án>/<khu vực>/<thiết bị>/<loại dữ liệu>`, ví dụ `iot/lab/light01/cmd`.
- Đặt **ID thiết bị vào topic** để thêm thiết bị không phải sửa code và có thể dùng wildcard `iot/lab/+/data`.
- Tách loại dữ liệu: `data` (đo đạc), `cmd` (lệnh), `status` (trạng thái).
- Không dùng dấu cách, không bắt đầu bằng `/`, không dùng `+`/`#` trong tên topic khi publish.

## 6. Xác định các hàm và class cần tạo

- **Module cấu hình chung**: hằng số broker, hàm tạo client, hàm connect có báo lỗi.
- **Mỗi chương trình**: `on_connect` (subscribe ở đây), `on_message` (xử lý message), `main()` (tạo client, gán callback, connect, chạy loop).
- **Class** khi có đối tượng mang **trạng thái + hành vi** và có thể có nhiều bản (thiết bị Bài 3: `SmartDevice`). Chương trình chỉ gửi/nhận thì hàm là đủ, không cần class.
- **Hàm thuần** cho logic nghiệp vụ, tách khỏi MQTT để dễ test: `check_alerts(temperature, humidity)`, `read_sensor(device_id)`.

## 7. Bắt đầu code từ đâu

1. Cài và **kiểm tra broker bằng `mosquitto_sub`/`mosquitto_pub`**, chưa viết dòng Python nào.
2. Cài `paho-mqtt`, viết module cấu hình.
3. Viết **subscriber trước**. Kiểm tra bằng `mosquitto_pub` gửi tay.
4. Viết publisher. Kiểm tra bằng subscriber vừa viết, hoặc `mosquitto_sub`.
5. Thêm logic nghiệp vụ (JSON, ngưỡng, trạng thái).
6. Thêm phần mở rộng.
7. Thêm xử lý lỗi: broker tắt, payload sai, Ctrl+C.

Khung tối thiểu của một subscriber với paho 2.x:

```python
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("iot/lab/message", qos=1)

def on_message(client, userdata, msg):
    print(msg.topic, msg.payload.decode())

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("127.0.0.1", 1883, 60)
client.loop_forever()
```

Khung tối thiểu của một publisher:

```python
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("127.0.0.1", 1883, 60)
client.loop_start()
info = client.publish("iot/lab/message", "hello", qos=1)
info.wait_for_publish()
client.disconnect()
client.loop_stop()
```

## 8. Test từng phần

- Mỗi chương trình test **một mình** trước, dùng `mosquitto_pub`/`mosquitto_sub` đóng vai bên còn lại.
- Luôn mở một cửa sổ `mosquitto_sub -h 127.0.0.1 -t "iot/lab/#" -v` để thấy mọi thứ đi qua broker.
- Test **giá trị biên** (35.0, 40.0), **dữ liệu sai** (không phải JSON, thiếu trường, lệnh lạ) và **môi trường hỏng** (broker tắt, sai port).
- So output với mẫu trong đề từng chữ.

## 9. Debug MQTT

Đi theo đường đi của message, từ ngoài vào trong:

1. **Broker có chạy không?** `Get-Service mosquitto`, `netstat -ano | findstr :1883`.
2. **Client có kết nối được không?** Xem `on_connect` có được gọi không, reason code là gì.
3. **Message có tới broker không?** `mosquitto_sub -t "#" -v` (hoặc chạy broker với `-v` để xem log).
4. **Topic có khớp từng ký tự không?** Lỗi hay gặp: `iot/lab/sensor01/data` vs `iot/lab/sensor1/data`, thừa `/` ở đầu, sai hoa thường (topic phân biệt hoa thường).
5. **Subscriber có đang chạy loop không?** Không gọi `loop_forever()`/`loop_start()` thì callback không bao giờ chạy.
6. **Callback có ném exception không?** Exception thoát khỏi callback làm dừng loop; bọc phần xử lý bằng `try/except`.
7. **Có client lạ nào cùng topic không?** Message trùng/lạ thường do một chương trình cũ còn chạy ngầm, hoặc dùng broker công cộng.

## 10. Lỗi người mới thường gặp

| Lỗi | Hậu quả | Cách tránh |
|---|---|---|
| Dùng `mqtt.Client()` kiểu paho 1.x | Lỗi/cảnh báo với paho 2.x | `mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, ...)` |
| Quên chạy network loop | Không nhận được gì, callback không chạy | `loop_forever()` hoặc `loop_start()` |
| `publish()` xong `disconnect()` ngay | Message bị mất | `wait_for_publish()` trước khi disconnect |
| Subscribe ngoài `on_connect` | Mất subscription sau khi kết nối lại | Subscribe trong `on_connect` |
| Chạy publisher trước subscriber | Message gửi đi không ai nhận | Chạy subscriber trước (hoặc dùng retain khi phù hợp) |
| Hai client trùng client ID | Hai bên đá nhau ra liên tục | Sinh client ID ngẫu nhiên |
| Chờ (`wait_for_publish`, `sleep` dài) trong callback | Deadlock hoặc chặn mọi message khác | Callback chỉ xử lý nhanh rồi return |
| Không bắt lỗi `json.loads` | Một payload hỏng làm sập subscriber | `try/except json.JSONDecodeError` |
| Quên `.decode()` payload | In ra `b'...'` hoặc so sánh bytes với str luôn sai | `msg.payload.decode("utf-8")` |
| Mosquitto 2.x có `listener` nhưng thiếu `allow_anonymous true` | Lỗi `Not authorized` | Thêm `allow_anonymous true` |
| Dùng `localhost` trên Windows khi broker chỉ nghe IPv4 | Kết nối chậm hoặc lỗi do thử IPv6 trước | Dùng `127.0.0.1` |
| Dùng broker công cộng với topic phổ biến | Nhận lẫn message của người khác | Dùng broker local hoặc topic có tiền tố riêng |
| Retain topic lệnh | Thiết bị khởi động lại chạy lại lệnh cũ | Chỉ retain trạng thái, không retain lệnh |
