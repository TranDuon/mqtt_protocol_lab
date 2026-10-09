"""Bai 1 - Publisher: gui thong diep chao mung len topic iot/lab/message."""
import argparse
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # thu muc goc lab, de import common/
from common import config

# on_connect chay tren thread mang cua paho; Event dung de bao cho main thread biet da ket noi.
connected = threading.Event()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"LOI: Broker tu choi ket noi: {reason_code}")
        client.disconnect()
        return
    print(f"Da ket noi broker {config.BROKER_HOST}:{config.BROKER_PORT}")
    connected.set()


def main():
    parser = argparse.ArgumentParser(description="Bai 1 - MQTT publisher")
    parser.add_argument("-n", "--count", type=int, default=5, help="so message can gui (mac dinh 5)")
    parser.add_argument("-i", "--interval", type=float, default=1.0, help="so giay giua 2 message (mac dinh 1)")
    args = parser.parse_args()

    payload = f"Xin chao tu client Python MQTT - {config.STUDENT_ID} - {config.STUDENT_NAME}"

    client = config.create_client("publisher_bai1")
    client.on_connect = on_connect
    config.connect_or_exit(client)
    client.loop_start()  # chay vong lap mang tren thread nen; main thread tiep tuc ben duoi

    try:
        if not connected.wait(timeout=5):
            print("LOI: Khong ket noi duoc broker sau 5 giay.")
            return
        for i in range(1, args.count + 1):
            if config.publish_confirmed(client, config.TOPIC_MESSAGE, payload):
                print(f"Da gui message [{i}/{args.count}] len {config.TOPIC_MESSAGE}: {payload}")
            else:
                print(f"LOI: Message [{i}/{args.count}] chua duoc broker xac nhan (mat ket noi?)")
            if i < args.count:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Da dung publisher.")
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
