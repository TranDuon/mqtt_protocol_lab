# Bài 1 – Gửi và nhận thông điệp MQTT cơ bản

Làm quen với cơ chế **publisher/subscriber**: một chương trình gửi, một chương trình nhận, hai bên chỉ biết chung broker và topic.

| | |
|---|---|
| Topic | `iot/lab/message` |
| Payload | Chuỗi text: `Xin chao tu client Python MQTT - <MSSV> - <Ho ten>` |
| QoS | 1 |

## Chương trình

| File | Vai trò | Làm gì |
|---|---|---|
| `subscriber_bai1.py` | Subscriber | Kết nối broker, subscribe `iot/lab/message`, mỗi message in `Topic`, `Payload`, `Time`. Chạy liên tục đến khi Ctrl+C. |
| `publisher_bai1.py` | Publisher | Kết nối broker, gửi nhiều message liên tiếp (mặc định 5, cách nhau 1 giây), chờ broker xác nhận từng message rồi tự thoát. |

Họ tên và MSSV lấy từ `common/config.py`.

## Luồng chạy

```
subscriber:  connect() ─▶ CONNACK ─▶ on_connect: subscribe("iot/lab/message")
             loop_forever() ... chờ ... PUBLISH tới ─▶ on_message: in 4 dòng

publisher:   connect() ─▶ loop_start() (thread nền) ─▶ chờ on_connect
             lặp N lần: publish(qos=1) ─▶ chờ PUBACK ─▶ in "Da gui..." ─▶ sleep
             disconnect() ─▶ loop_stop()
```

- **Subscriber** dùng `loop_forever()`: main thread chỉ có việc chờ message, nên giao luôn cho vòng lặp mạng.
- **Publisher** dùng `loop_start()`: vòng lặp mạng chạy ở thread nền (nhận CONNACK, gửi PUBLISH, nhận PUBACK), main thread rảnh để chạy vòng `for`. `publish()` chỉ đưa message vào hàng đợi, nên phải chờ PUBACK (`publish_confirmed`) trước khi `disconnect()`, nếu không message có thể bị mất.
- Subscribe được gọi **trong `on_connect`** để nếu mất kết nối rồi tự kết nối lại thì subscription được đăng ký lại.

## Cách chạy

Từ thư mục `mqtt_protocol` (đã activate venv, broker đang chạy):

```powershell
python bai1_messaging/subscriber_bai1.py      # terminal 1 – chạy trước
python bai1_messaging/publisher_bai1.py       # terminal 2
```

Tùy chọn publisher: `-n` số message, `-i` số giây giữa 2 message. Ví dụ `python bai1_messaging/publisher_bai1.py -n 10 -i 2`.

## Output thực tế

Publisher (`-n 3`):

```
Da ket noi broker 127.0.0.1:1883
Da gui message [1/3] len iot/lab/message: Xin chao tu client Python MQTT - B23DCCN227 - Tran Dang Duong
Da gui message [2/3] len iot/lab/message: Xin chao tu client Python MQTT - B23DCCN227 - Tran Dang Duong
Da gui message [3/3] len iot/lab/message: Xin chao tu client Python MQTT - B23DCCN227 - Tran Dang Duong
```

Subscriber:

```
Da ket noi broker 127.0.0.1:1883
Dang lang nghe topic iot/lab/message ... (Ctrl+C de thoat)

Nhan duoc message:
Topic: iot/lab/message
Payload: Xin chao tu client Python MQTT - B23DCCN227 - Tran Dang Duong
Time: 10:12:53

Nhan duoc message:
Topic: iot/lab/message
Payload: Xin chao tu client Python MQTT - B23DCCN227 - Tran Dang Duong
Time: 10:12:54

Nhan duoc message:
Topic: iot/lab/message
Payload: Xin chao tu client Python MQTT - B23DCCN227 - Tran Dang Duong
Time: 10:12:55

Da dung subscriber.
```

## Đối chiếu tiêu chí đánh giá

- [x] Kết nối thành công broker
- [x] Publish đúng topic `iot/lab/message`
- [x] Subscribe nhận đúng dữ liệu (họ tên, MSSV, lời chào)
- [x] Hiển thị kết quả rõ ràng (Topic, Payload, Time)
- [x] Mở rộng: publisher gửi nhiều thông điệp liên tiếp; subscriber chạy đến khi Ctrl+C
