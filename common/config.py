"""Cau hinh va ham tien ich MQTT dung chung cho ca 3 bai."""
import os
import sys
import uuid

import paho.mqtt.client as mqtt

STUDENT_NAME = "Tran Dang Duong"
STUDENT_ID = "B23DCCN227"

BROKER_HOST = os.environ.get("MQTT_HOST", "127.0.0.1")
BROKER_PORT = int(os.environ.get("MQTT_PORT", "1883"))
KEEPALIVE = 60  # giay; client im lang qua lau thi tu gui PINGREQ de bao "con song"
PUBLISH_TIMEOUT = 5  # giay cho broker tra PUBACK

TOPIC_MESSAGE = "iot/lab/message"


# Topic theo mo hinh thiet bi: iot/lab/<device_id>/<loai>
def topic_data(device_id):
    return f"iot/lab/{device_id}/data"


def topic_cmd(device_id):
    return f"iot/lab/{device_id}/cmd"


def topic_status(device_id):
    return f"iot/lab/{device_id}/status"


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    """Callback mac dinh: bao khi mat ket noi ngoai y muon (paho se tu ket noi lai)."""
    if reason_code.is_failure:
        print(f"CANH BAO: Mat ket noi broker ({reason_code}), dang thu ket noi lai...")


def create_client(role):
    """Tao MQTT client theo API cua paho-mqtt 2.x voi client ID duy nhat."""
    client_id = f"{role}-{uuid.uuid4().hex[:6]}"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    client.on_disconnect = on_disconnect
    return client


def connect_or_exit(client):
    """Gui goi CONNECT toi broker; neu khong ket noi duoc thi bao loi ro rang va thoat."""
    try:
        client.connect(BROKER_HOST, BROKER_PORT, KEEPALIVE)
    except OSError as err:
        print(f"LOI: Khong ket noi duoc MQTT broker tai {BROKER_HOST}:{BROKER_PORT} ({err})")
        print("Hay kiem tra Mosquitto da chay chua.")
        sys.exit(1)


def publish_confirmed(client, topic, payload):
    """Publish QoS 1 roi cho broker tra PUBACK. Tra ve True neu broker da nhan message.

    Chi goi tu main thread khi da loop_start(). Khong goi trong callback: callback chay
    tren chinh thread mang, cho PUBACK o do se tu chan minh (deadlock).
    """
    info = client.publish(topic, payload, qos=1)
    try:
        info.wait_for_publish(timeout=PUBLISH_TIMEOUT)
    except (RuntimeError, ValueError):  # dang mat ket noi, hoac hang doi gui bi day
        return False
    return info.is_published()
