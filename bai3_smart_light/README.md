# Bài 3 – Hệ thống điều khiển đèn thông minh

Mô hình IoT **hai chiều**: controller gửi lệnh xuống thiết bị, thiết bị thực hiện và báo trạng thái ngược lại.

| Topic | Chiều | Payload |
|---|---|---|
| `iot/lab/light01/cmd` | controller → device | `ON` hoặc `OFF` |
| `iot/lab/light01/status` | device → controller | `{"device_id":"light01","status":"ON"}` |

Tổng quát: `iot/lab/<device_id>/cmd` và `iot/lab/<device_id>/status`.

## Chương trình

| File | Vai trò | Làm gì |
|---|---|---|
| `device_bai3.py` | Subscriber `/cmd` + Publisher `/status` | Giữ trạng thái đèn (ban đầu OFF). Nhận `ON`/`OFF` thì đổi trạng thái và publish trạng thái mới. Lệnh khác bị bỏ qua và **không** publish status. |
| `controller_bai3.py` | Publisher `/cmd` + Subscriber `/status` | Đọc lệnh từ bàn phím, publish lên `/cmd`, chờ và in trạng thái thiết bị phản hồi. Lệnh khác ON/OFF/EXIT bị báo lỗi; `EXIT` để thoát. |

Mỗi thiết bị là một object của class `SmartDevice` (giữ `device_id`, `status`, 2 topic và logic xử lý lệnh), nên một tiến trình có thể mô phỏng nhiều thiết bị.

## Luồng chạy

```
controller (main thread)          broker                device (loop_forever)
  input "ON"
  publish("ON") ─────▶ iot/lab/light01/cmd ─────▶ on_message
  chờ status_received                                 handle_command("ON") → status = ON
                                                      publish(status JSON)
  on_message (thread nền) ◀── iot/lab/light01/status ◀──┘
  in "Trang thai nhan duoc", set status_received
  hỏi lệnh tiếp
```

Controller phải làm hai việc cùng lúc nên dùng **hai thread**:

- **Main thread**: vòng `input()` chờ người dùng gõ lệnh.
- **Thread nền của paho** (`loop_start()`): nhận `/status` và gọi `on_message`.

Hai thread báo hiệu cho nhau bằng `threading.Event`:

- `ready`: được set khi broker xác nhận đã subscribe `/status` (SUBACK). Chỉ sau đó mới cho gõ lệnh, để không lỡ phản hồi đầu tiên.
- `status_received`: được set trong `on_message`. Sau khi gửi lệnh, main thread chờ event này (tối đa 3 giây) rồi mới hỏi lệnh tiếp, nhờ đó dòng `Nhap lenh:` không bị in chen giữa phản hồi. Quá 3 giây thì báo thiết bị không phản hồi.

Trong `device_bai3.py`, `publish()` được gọi ngay trong `on_message` nhưng **không** chờ PUBACK: callback chạy trên chính thread mạng, chờ ở đó sẽ tự chặn mình (deadlock).

## Cách chạy

```powershell
python bai3_smart_light/device_bai3.py          # terminal 1 – chạy trước
python bai3_smart_light/controller_bai3.py      # terminal 2 – gõ ON, OFF, EXIT
```

Mở rộng nhiều thiết bị:

```powershell
python bai3_smart_light/device_bai3.py light01 fan01 pump01   # một tiến trình mô phỏng 3 thiết bị
python bai3_smart_light/controller_bai3.py fan01              # controller điều khiển fan01
```

## Output thực tế

Controller (lệnh gõ vào: `ON`, `OFF`, `BLINK`, `EXIT`):

```
Da ket noi broker 127.0.0.1:1883
Dieu khien light01: gui lenh toi iot/lab/light01/cmd, nhan trang thai tu iot/lab/light01/status
Lenh hop le: ON, OFF, EXIT

Nhap lenh: ON
Da gui lenh ON toi light01

Trang thai nhan duoc:
{"device_id":"light01","status":"ON"}

Nhap lenh: OFF
Da gui lenh OFF toi light01

Trang thai nhan duoc:
{"device_id":"light01","status":"OFF"}

Nhap lenh: BLINK
LOI: Lenh khong hop le. Chi chap nhan ON, OFF hoac EXIT.

Nhap lenh: EXIT
Da thoat controller.
```

Device:

```
Da ket noi broker 127.0.0.1:1883
[light01] Trang thai: OFF | nghe lenh tai iot/lab/light01/cmd
(Ctrl+C de tat thiet bi)

[light01] Nhan lenh ON -> trang thai ON, da gui {"device_id":"light01","status":"ON"}
[light01] Nhan lenh OFF -> trang thai OFF, da gui {"device_id":"light01","status":"OFF"}
Da tat thiet bi.
```

Khi thiết bị không chạy:

```
Nhap lenh: ON
Da gui lenh ON toi light01
Khong nhan duoc phan hoi tu light01 sau 3 giay (thiet bi co dang chay khong?)
```

## Đối chiếu tiêu chí đánh giá

- [x] Điều khiển được thiết bị qua MQTT
- [x] Thiết bị phản hồi đúng trạng thái sau mỗi lệnh hợp lệ
- [x] Có cơ chế giao tiếp hai chiều (`/cmd` xuống, `/status` lên)
- [x] Tổ chức topic hợp lý: `iot/lab/<device_id>/cmd|status`
- [x] Mở rộng: báo lỗi lệnh sai; lệnh EXIT; nhiều thiết bị light01, fan01, pump01
