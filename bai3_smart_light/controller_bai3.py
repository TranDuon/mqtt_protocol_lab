"""Bai 3 - Controller App: nhap lenh ON/OFF tu ban phim, gui toi thiet bi va hien thi trang thai phan hoi."""
import argparse
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # thu muc goc lab, de import common/
from common import config

VALID_COMMANDS = ("ON", "OFF")
RESPONSE_TIMEOUT = 3  # giay cho thiet bi phan hoi trang thai

# Callback chay tren thread mang cua paho, main thread dang cho input().
# Dung Event de 2 thread bao hieu cho nhau.
ready = threading.Event()            # da subscribe xong topic status (nhan SUBACK)
status_received = threading.Event()  # vua nhan duoc trang thai tu thiet bi


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"LOI: Broker tu choi ket noi: {reason_code}")
        client.disconnect()
        return
    client.subscribe(config.topic_status(userdata["device_id"]), qos=1)


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    ready.set()


def on_message(client, userdata, msg):
    print("\nTrang thai nhan duoc:")
    print(msg.payload.decode("utf-8", errors="replace"))
    status_received.set()


def main():
    parser = argparse.ArgumentParser(description="Bai 3 - Controller")
    parser.add_argument("device", nargs="?", default="light01",
                        help="device_id can dieu khien (mac dinh: light01)")
    args = parser.parse_args()
    device_id = args.device
    cmd_topic = config.topic_cmd(device_id)

    client = config.create_client("controller_bai3")
    client.user_data_set({"device_id": device_id})
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    config.connect_or_exit(client)
    client.loop_start()  # thread nen nhan status; main thread doc ban phim

    try:
        if not ready.wait(timeout=5):
            print("LOI: Khong ket noi/subscribe duoc broker sau 5 giay.")
            return
        print(f"Da ket noi broker {config.BROKER_HOST}:{config.BROKER_PORT}")
        print(f"Dieu khien {device_id}: gui lenh toi {cmd_topic}, nhan trang thai tu {config.topic_status(device_id)}")
        print("Lenh hop le: ON, OFF, EXIT\n")

        while True:
            command = input("Nhap lenh: ").strip().upper()
            if command == "EXIT":
                break
            if command not in VALID_COMMANDS:
                print("LOI: Lenh khong hop le. Chi chap nhan ON, OFF hoac EXIT.\n")
                continue

            status_received.clear()
            if not config.publish_confirmed(client, cmd_topic, command):
                print("LOI: Khong gui duoc lenh (mat ket noi broker?)\n")
                continue
            print(f"Da gui lenh {command} toi {device_id}")

            # Cho phan hoi truoc khi hoi lenh tiep, de dong "Nhap lenh:" khong bi in chen.
            if status_received.wait(timeout=RESPONSE_TIMEOUT):
                print()
            else:
                print(f"Khong nhan duoc phan hoi tu {device_id} sau {RESPONSE_TIMEOUT} giay "
                      f"(thiet bi co dang chay khong?)\n")
    except (KeyboardInterrupt, EOFError):
        print()
    finally:
        client.disconnect()
        client.loop_stop()
        print("Da thoat controller.")


if __name__ == "__main__":
    main()
