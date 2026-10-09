# Kiến thức MQTT dùng trong lab

Tài liệu này giải thích những khái niệm MQTT và paho-mqtt thực sự được dùng trong 3 bài, theo thứ tự từ cơ bản đến phần cài đặt.

## 1. MQTT là gì

MQTT (Message Queuing Telemetry Transport) là giao thức nhắn tin kiểu **publish/subscribe**, chạy trên TCP, header rất nhỏ (tối thiểu 2 byte). Nó được thiết kế cho thiết bị yếu và mạng kém ổn định nên rất phổ biến trong IoT.

Điểm cốt lõi: các client **không nói chuyện trực tiếp** với nhau. Mọi message đi qua một máy trung gian là **broker**.

```
Publisher ──PUBLISH(topic, payload)──▶ BROKER ──chuyển tiếp──▶ mọi Subscriber đã đăng ký topic đó
```

## 2. Các thành phần

| Khái niệm | Ý nghĩa | Trong lab |
|---|---|---|
| **Client** | Bất kỳ chương trình nào kết nối tới broker. Mỗi client có một **Client ID duy nhất**; hai client trùng ID thì broker ngắt client cũ. | Cả 6 chương trình. `create_client()` tạo ID dạng `subscriber_bai1-3fa9c1`. |
| **Broker** | "Bưu điện": nhận message và phân phát theo topic. Không quan tâm nội dung message. | Mosquitto tại `127.0.0.1:1883` |
| **Publisher** | Client gửi message lên một topic. | publisher_bai1, sensor, controller (gửi lệnh), device (gửi trạng thái) |
| **Subscriber** | Client đăng ký nhận message của một hoặc nhiều topic. | subscriber_bai1, monitor, device (nhận lệnh), controller (nhận trạng thái) |
| **Topic** | Chuỗi phân cấp bằng `/`, giống đường dẫn. Không cần tạo trước; publish là có. | `iot/lab/sensor01/data` |
| **Message / Payload** | Dữ liệu gửi đi, dạng bytes. Ý nghĩa do hai bên tự thống nhất. | Bài 1: text. Bài 2, 3: JSON. |

Một client có thể vừa publish vừa subscribe: `device_bai3.py` và `controller_bai3.py` đều như vậy.

### Wildcard khi subscribe

- `+` thay đúng **một** cấp: `iot/lab/+/data` khớp `iot/lab/sensor01/data`, `iot/lab/sensor02/data`.
- `#` thay **mọi** cấp còn lại, phải đứng cuối: `iot/lab/#` khớp tất cả topic của lab (dùng với `mosquitto_sub` để quan sát).

Wildcard chỉ dùng khi **subscribe**, không dùng khi publish.

## 3. QoS – mức đảm bảo giao nhận

| QoS | Tên | Cơ chế | Đặc điểm |
|---|---|---|---|
| 0 | At most once | Gửi một lần, không xác nhận | Nhanh nhất, có thể mất |
| 1 | At least once | Bên nhận trả **PUBACK**; chưa có PUBACK thì gửi lại | Không mất, có thể trùng |
| 2 | Exactly once | Bắt tay 4 bước (PUBREC/PUBREL/PUBCOMP) | Đúng một lần, chậm nhất |

Lab dùng **QoS 1**: đủ tin cậy, và PUBACK cho phép publisher biết chắc broker đã nhận (`publish_confirmed()`).

QoS áp dụng cho từng chặng: publisher → broker và broker → subscriber. Mức thực tế subscriber nhận là mức nhỏ hơn giữa QoS lúc publish và QoS lúc subscribe.

## 4. Retain và Keep Alive

- **Retain**: publish với cờ retain thì broker giữ lại message cuối cùng của topic đó và gửi ngay cho subscriber mới vào. Lab **không** dùng retain. Đặc biệt không được retain topic lệnh `/cmd`, vì thiết bị khởi động lại sẽ nhận lại lệnh cũ.
- **Keep Alive**: số giây (lab dùng 60) client hứa sẽ có tín hiệu. Nếu không có gì để gửi, client tự gửi PINGREQ và broker trả PINGRESP. Quá 1,5 × keepalive không nghe gì thì broker coi client đã chết và đóng kết nối.

## 5. Các gói tin và vòng đời một client

```
Client                                   Broker
  │── CONNECT (client_id, keepalive) ───────▶│
  │◀────────────── CONNACK (reason code) ────│   → on_connect
  │── SUBSCRIBE (topic, qos) ───────────────▶│
  │◀────────────────────────── SUBACK ───────│   → on_subscribe
  │── PUBLISH (topic, payload, qos=1) ──────▶│
  │◀────────────────────────── PUBACK ───────│   → wait_for_publish() trả về
  │◀──────────── PUBLISH (từ client khác) ───│   → on_message
  │── PINGREQ / ◀── PINGRESP (nếu im lặng) ──│
  │── DISCONNECT ───────────────────────────▶│   → on_disconnect
```

CONNACK có **reason code**: thành công, hoặc thất bại như `Not authorized` (broker không cho client ẩn danh).

## 6. MQTT khác HTTP và TCP socket

| | TCP socket thuần | HTTP | MQTT |
|---|---|---|---|
| Mô hình | Điểm–điểm, tự định nghĩa giao thức | Request/response: client hỏi, server trả lời | Publish/subscribe qua broker |
| Kết nối | Giữ mở | Thường ngắn, mỗi request một lần | Giữ mở lâu dài; broker chủ động đẩy dữ liệu xuống |
| Hai bên có cần biết địa chỉ nhau? | Có (IP:port) | Có (URL server) | **Không**, chỉ cần biết broker và topic |
| Một gửi – nhiều nhận | Tự cài | Không có sẵn | Có sẵn: mọi subscriber của topic đều nhận |
| Overhead | Thấp nhất | Header lớn (text) | Header 2 byte, nhị phân |

Ở Bài 3, controller và đèn không biết IP của nhau. Thêm một màn hình giám sát thứ ba chỉ cần subscribe `iot/lab/light01/status`, không phải sửa thiết bị.

## 7. paho-mqtt trong Python

### 7.1. Tạo client (paho 2.x)

```python
import paho.mqtt.client as mqtt
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="...")
```

paho-mqtt 2.x bắt buộc khai báo phiên bản API của callback. Code mẫu cũ trên mạng (`mqtt.Client()` của bản 1.x) sẽ báo lỗi hoặc cảnh báo. Với `VERSION2`, các callback có chữ ký:

```python
def on_connect(client, userdata, flags, reason_code, properties): ...
def on_message(client, userdata, msg): ...           # msg.topic, msg.payload (bytes), msg.qos
def on_subscribe(client, userdata, mid, reason_code_list, properties): ...
def on_disconnect(client, userdata, disconnect_flags, reason_code, properties): ...
```

### 7.2. Network loop và thread

`connect()` chỉ gửi gói CONNECT. Việc đọc/ghi socket (nhận CONNACK, nhận message, gửi PUBACK, PINGREQ...) do **network loop** đảm nhiệm. Không chạy loop thì không nhận được gì.

| Cách | Hoạt động | Dùng khi | Trong lab |
|---|---|---|---|
| `loop_forever()` | Chạy loop trên **main thread**, chặn tại đó đến khi disconnect. Tự kết nối lại khi mất kết nối. | Chương trình chỉ ngồi chờ message | subscriber_bai1, monitor, device |
| `loop_start()` / `loop_stop()` | Tạo **thread nền** chạy loop; main thread làm việc khác | Main thread còn việc riêng: vòng gửi định kỳ, chờ bàn phím | publisher_bai1, sensor, controller |

**Callback chạy trên thread của network loop.** Hệ quả:

1. Muốn main thread biết một sự kiện đã xảy ra trong callback (đã kết nối, đã nhận phản hồi) thì dùng `threading.Event`: callback gọi `set()`, main thread gọi `wait(timeout)`.
2. **Không chờ bên trong callback.** Ví dụ `wait_for_publish()` trong `on_message`: callback đang chiếm chính thread mạng, nên PUBACK không bao giờ được xử lý, gây deadlock. Trong callback chỉ gọi `publish()` rồi return.
3. **Exception thoát khỏi callback sẽ dừng loop** (paho 2.x mặc định không nuốt lỗi). Phần xử lý dễ lỗi như `json.loads` phải nằm trong `try/except`.

### 7.3. Subscribe trong `on_connect`

Nếu mất kết nối, paho tự kết nối lại, nhưng session mới **không còn** subscription cũ (clean session). Đặt `subscribe()` trong `on_connect` thì mỗi lần kết nối lại đều đăng ký lại.

### 7.4. `publish()` không gửi ngay

`publish()` chỉ đưa message vào hàng đợi và trả về `MQTTMessageInfo`. Message thực sự đi khi network loop chạy. Vì vậy:

```python
info = client.publish(topic, payload, qos=1)
info.wait_for_publish(timeout=5)   # chờ PUBACK
info.is_published()                # True nếu broker đã xác nhận
```

`wait_for_publish()` ném `RuntimeError` nếu đang mất kết nối, và trả về im lặng khi hết timeout. `common/config.py::publish_confirmed()` gói cả hai trường hợp thành một giá trị True/False.

## 8. JSON trong MQTT

MQTT không quy định nội dung payload. JSON là cách phổ biến để gửi dữ liệu có cấu trúc:

```python
payload = json.dumps({"device_id": "sensor01", "temperature": 28.5})   # dict -> str (gửi)
data = json.loads(msg.payload)                                          # bytes/str -> dict (nhận)
```

Bên nhận luôn phải phòng payload sai: `json.JSONDecodeError` (không phải JSON), `KeyError` (thiếu trường), `ValueError`/`TypeError` (sai kiểu).

`json.dumps(..., separators=(",", ":"))` bỏ khoảng trắng, cho ra dạng gọn `{"device_id":"light01","status":"ON"}` như mẫu Bài 3.

## 9. Eclipse Mosquitto

- Broker mã nguồn mở, nhẹ, phổ biến nhất cho học tập và thử nghiệm.
- Từ bản 2.0, nếu **không có** file cấu hình thì broker chỉ nghe localhost và cho phép client ẩn danh từ máy local. Nếu **có** khai báo `listener` thì mặc định **từ chối** client ẩn danh, phải thêm `allow_anonymous true`.
- Công cụ đi kèm để kiểm tra không cần viết code:
  - `mosquitto_sub -h 127.0.0.1 -t "iot/lab/#" -v`: in mọi message (`-v` in kèm topic).
  - `mosquitto_pub -h 127.0.0.1 -t <topic> -m <payload>`: gửi một message.
  - `mosquitto -c mosquitto.conf -v`: chạy broker với log chi tiết.

## 10. Áp dụng trong 3 bài

| Bài | Kiến thức chính |
|---|---|
| 1 | Connect / subscribe / publish, callback, `loop_forever` vs `loop_start`, chờ PUBACK trước khi disconnect |
| 2 | Topic theo thiết bị, wildcard `+`, payload JSON, gửi định kỳ, bắt lỗi trong callback |
| 3 | Giao tiếp hai chiều bằng 2 topic, một client vừa pub vừa sub, hai thread + `threading.Event`, class lưu trạng thái thiết bị |
