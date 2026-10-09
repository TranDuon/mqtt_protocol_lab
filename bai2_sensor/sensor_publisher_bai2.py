"""Bai 2 - Sensor Publisher: mo phong cam bien gui nhiet do/do am dang JSON moi 3 giay."""
import argparse
import json
import random
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # thu muc goc lab, de import common/
from common import config

connected = threading.Event()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"LOI: Broker tu choi ket noi: {reason_code}")
        client.disconnect()
        return
    print(f"Da ket noi broker {config.BROKER_HOST}:{config.BROKER_PORT}")
    connected.set()


def read_sensor(device_id):
    """Sinh mot ban ghi gia lap. Khoang gia tri vuot qua nguong de thay duoc canh bao."""
    return {
        "device_id": device_id,
        "temperature": round(random.uniform(25.0, 40.0), 1),
        "humidity": round(random.uniform(30.0, 80.0), 1),
    }


def main():
    parser = argparse.ArgumentParser(description="Bai 2 - Sensor publisher")
    parser.add_argument("devices", nargs="*", default=["sensor01"],
                        help="danh sach device_id can mo phong (mac dinh: sensor01)")
    parser.add_argument("-i", "--interval", type=float, default=3.0, help="chu ky gui, giay (mac dinh 3)")
    args = parser.parse_args()

    client = config.create_client("sensor_bai2")
    client.on_connect = on_connect
    config.connect_or_exit(client)
    client.loop_start()

    try:
        if not connected.wait(timeout=5):
            print("LOI: Khong ket noi duoc broker sau 5 giay.")
            return
        print(f"Gui du lieu cua {', '.join(args.devices)} moi {args.interval:g} giay (Ctrl+C de dung)\n")
        while True:
            for device_id in args.devices:
                payload = json.dumps(read_sensor(device_id))  # dict -> chuoi JSON
                topic = config.topic_data(device_id)
                if config.publish_confirmed(client, topic, payload):
                    print(f"[{datetime.now():%H:%M:%S}] {topic} <- {payload}")
                else:
                    print(f"[{datetime.now():%H:%M:%S}] LOI: Khong gui duoc du lieu {device_id} (mat ket noi?)")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Da dung sensor publisher.")
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
