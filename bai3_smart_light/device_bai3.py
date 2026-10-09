"""Bai 3 - Smart Light Device: nhan lenh ON/OFF qua MQTT va phan hoi trang thai moi."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # thu muc goc lab, de import common/
from common import config

VALID_COMMANDS = ("ON", "OFF")


class SmartDevice:
    """Mot thiet bi thong minh (den, quat, bom...) duoc dieu khien qua MQTT."""

    def __init__(self, device_id):
        self.device_id = device_id
        self.status = "OFF"
        self.cmd_topic = config.topic_cmd(device_id)
        self.status_topic = config.topic_status(device_id)

    def handle_command(self, command):
        """Ap dung lenh. Tra ve True neu lenh hop le (trang thai da cap nhat)."""
        if command not in VALID_COMMANDS:
            return False
        self.status = command
        return True

    def status_payload(self):
        # separators bo khoang trang -> {"device_id":"light01","status":"ON"} giong mau de bai
        return json.dumps({"device_id": self.device_id, "status": self.status}, separators=(",", ":"))


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"LOI: Broker tu choi ket noi: {reason_code}")
        client.disconnect()
        return
    devices = userdata  # dict: cmd_topic -> SmartDevice
    client.subscribe([(topic, 1) for topic in devices])
    print(f"Da ket noi broker {config.BROKER_HOST}:{config.BROKER_PORT}")
    for device in devices.values():
        print(f"[{device.device_id}] Trang thai: {device.status} | nghe lenh tai {device.cmd_topic}")
    print("(Ctrl+C de tat thiet bi)\n")


def on_message(client, userdata, msg):
    device = userdata.get(msg.topic)
    if device is None:
        return
    command = msg.payload.decode("utf-8", errors="replace").strip().upper()

    if not device.handle_command(command):
        print(f"[{device.device_id}] Bo qua lenh khong hop le: {command!r} (chi nhan ON/OFF)")
        return

    payload = device.status_payload()
    # Chi publish, KHONG cho PUBACK o day: callback dang chay tren thread mang,
    # cho tai day se tu chan chinh no (deadlock).
    client.publish(device.status_topic, payload, qos=1)
    print(f"[{device.device_id}] Nhan lenh {command} -> trang thai {device.status}, da gui {payload}")


def main():
    parser = argparse.ArgumentParser(description="Bai 3 - Smart device")
    parser.add_argument("devices", nargs="*", default=["light01"],
                        help="device_id can mo phong (mac dinh: light01), vd: light01 fan01 pump01")
    args = parser.parse_args()

    devices = {}
    for device_id in args.devices:
        device = SmartDevice(device_id)
        devices[device.cmd_topic] = device  # tra cuu thiet bi theo topic cua message den

    client = config.create_client("device_bai3")
    client.user_data_set(devices)
    client.on_connect = on_connect
    client.on_message = on_message

    config.connect_or_exit(client)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Da tat thiet bi.")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
