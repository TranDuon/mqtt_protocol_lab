LAB MQTT - LAP TRINH PYTHON VOI GIAO THUC MQTT
Sinh vien: Tran Dang Duong - B23DCCN227
(Huong dan day du: README.md)

1. BROKER SU DUNG
   - Eclipse Mosquitto 2.1.2 chay tren may local: 127.0.0.1:1883, MQTT 3.1.1, khong TLS, cho phep ket noi an danh.
   - Cai dat: winget install --id EclipseFoundation.Mosquitto -e
   - Cau hinh: file mosquitto.conf (listener 1883 127.0.0.1, allow_anonymous true).
   - Chay: service "mosquitto" tu chay sau khi cai; hoac
     net stop mosquitto
     "C:\Program Files\mosquitto\mosquitto.exe" -c mosquitto.conf -v
   - Doi broker khong can sua code: dat bien moi truong MQTT_HOST / MQTT_PORT.

2. CHUAN BI
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt        (paho-mqtt 2.1.0)

3. CACH CHAY (moi chuong trinh mot terminal, chay ben nhan truoc)
   Bai 1 - topic iot/lab/message
     python bai1_messaging/subscriber_bai1.py
     python bai1_messaging/publisher_bai1.py          (tuy chon: -n so message, -i so giay)
   Bai 2 - topic iot/lab/sensor01/data
     python bai2_sensor/monitor_subscriber_bai2.py     (tuy chon: sensor01 sensor02, hoac + de nghe moi sensor)
     python bai2_sensor/sensor_publisher_bai2.py       (tuy chon: sensor01 sensor02)
   Bai 3 - topic iot/lab/light01/cmd va iot/lab/light01/status
     python bai3_smart_light/device_bai3.py            (tuy chon: light01 fan01 pump01)
     python bai3_smart_light/controller_bai3.py        (go ON / OFF / EXIT; tuy chon: fan01)

4. KET QUA DAT DUOC
   - Bai 1: subscriber nhan va in Topic, Payload, Time cua thong diep
     "Xin chao tu client Python MQTT - B23DCCN227 - Tran Dang Duong"; publisher gui nhieu message lien tiep.
   - Bai 2: sensor gui JSON {device_id, temperature, humidity} moi 3 giay; monitor in du lieu va
     canh bao "CANH BAO: Nhiet do cao" (> 35 C), "CANH BAO: Do am thap" (< 40 %); ho tro nhieu sensor.
   - Bai 3: controller gui lenh ON/OFF, thiet bi doi trang thai va phan hoi {"device_id":"light01","status":"ON"};
     bao loi lenh sai, co lenh EXIT, ho tro nhieu thiet bi.
   - Tat ca chuong trinh bao loi ro rang khi broker khong chay, tu ket noi lai, thoat gon khi Ctrl+C.
