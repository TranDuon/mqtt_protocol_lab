# Bài 2 – Mô phỏng cảm biến nhiệt độ và độ ẩm

Một thiết bị IoT giả lập gửi dữ liệu **định kỳ** dưới dạng **JSON**; một chương trình giám sát nhận, phân tích và **cảnh báo** khi vượt ngưỡng.

| | |
|---|---|
| Topic | `iot/lab/sensor01/data` (tổng quát: `iot/lab/<device_id>/data`) |
| Payload | `{"device_id": "sensor01", "temperature": 28.5, "humidity": 65.2}` |
| Chu kỳ | 3 giây |
| Ngưỡng | Nhiệt độ **> 35 °C** → `CANH BAO: Nhiet do cao`; độ ẩm **< 40 %** → `CANH BAO: Do am thap` |

## Chương trình

| File | Vai trò | Làm gì |
|---|---|---|
| `sensor_publisher_bai2.py` | Publisher định kỳ | Mỗi 3 giây sinh nhiệt độ ngẫu nhiên 25–40 °C, độ ẩm 30–80 % (khoảng vượt qua ngưỡng để thấy cảnh báo), đóng gói JSON và publish. |
| `monitor_subscriber_bai2.py` | Subscriber + xử lý | Subscribe topic dữ liệu, `json.loads` payload, in Device/Temperature/Humidity, kiểm tra 2 ngưỡng **độc lập** (một bản ghi có thể có cả 2 cảnh báo). |

## Luồng chạy

```
sensor:   dict ─json.dumps─▶ chuỗi JSON ─PUBLISH─▶ iot/lab/sensor01/data   (lặp mỗi 3s)
                                                     │
monitor:  on_message ◀───────── broker ◀─────────────┘
          json.loads ─▶ dict ─▶ in dữ liệu ─▶ check_alerts() ─▶ in cảnh báo
```

- MQTT chỉ chuyển bytes; JSON là "hợp đồng" giữa hai bên về tên trường.
- Toàn bộ phần phân tích trong `on_message` nằm trong `try/except`: payload không phải JSON hoặc thiếu trường chỉ in một dòng lỗi. Nếu để exception thoát khỏi callback, paho sẽ dừng `loop_forever()` và monitor bị tắt.
- Nếu broker mất kết nối, sensor báo lỗi từng lần gửi và tự kết nối lại khi broker chạy lại.

## Cách chạy

```powershell
python bai2_sensor/monitor_subscriber_bai2.py     # terminal 1 – chạy trước
python bai2_sensor/sensor_publisher_bai2.py       # terminal 2 – Ctrl+C để dừng
```

Mở rộng nhiều thiết bị:

```powershell
python bai2_sensor/sensor_publisher_bai2.py sensor01 sensor02     # gửi cho 2 sensor, mỗi sensor 1 topic
python bai2_sensor/monitor_subscriber_bai2.py sensor01 sensor02   # giám sát 2 sensor
python bai2_sensor/monitor_subscriber_bai2.py +                   # wildcard iot/lab/+/data: mọi sensor
```

Tùy chọn sensor: `-i` chu kỳ gửi (giây), ví dụ `-i 1`.

## Output thực tế

Sensor publisher:

```
Da ket noi broker 127.0.0.1:1883
Gui du lieu cua sensor01 moi 3 giay (Ctrl+C de dung)

[10:12:58] iot/lab/sensor01/data <- {"device_id": "sensor01", "temperature": 33.0, "humidity": 47.5}
[10:13:01] iot/lab/sensor01/data <- {"device_id": "sensor01", "temperature": 34.4, "humidity": 53.3}
[10:13:04] iot/lab/sensor01/data <- {"device_id": "sensor01", "temperature": 38.4, "humidity": 35.7}
Da dung sensor publisher.
```

Monitor subscriber (hai bản ghi cuối được gửi tay bằng `mosquitto_pub` để kiểm tra cảnh báo và payload lỗi):

```
Da ket noi broker 127.0.0.1:1883
Dang giam sat: iot/lab/sensor01/data (Ctrl+C de thoat)

[10:12:58] iot/lab/sensor01/data
Device: sensor01
Temperature: 33.0 C
Humidity: 47.5 %

[10:13:01] iot/lab/sensor01/data
Device: sensor01
Temperature: 34.4 C
Humidity: 53.3 %

[10:13:04] iot/lab/sensor01/data
Device: sensor01
Temperature: 38.4 C
Humidity: 35.7 %
CANH BAO: Nhiet do cao
CANH BAO: Do am thap

[10:13:06] iot/lab/sensor01/data
Device: sensor01
Temperature: 36.1 C
Humidity: 38.7 %
CANH BAO: Nhiet do cao
CANH BAO: Do am thap

[10:13:06] iot/lab/sensor01/data
LOI: Payload khong phai JSON hop le: b'du lieu loi'
```

## Đối chiếu tiêu chí đánh giá

- [x] Payload đúng định dạng JSON với 3 trường `device_id`, `temperature`, `humidity`
- [x] Dữ liệu gửi tuần hoàn mỗi 3 giây
- [x] Subscriber phân tích được dữ liệu
- [x] Cảnh báo đúng điều kiện (đúng ngưỡng 35.0 / 40.0 thì không cảnh báo)
- [x] Mở rộng: hiển thị từng dòng kèm thời gian và topic; nhiều thiết bị sensor01, sensor02
