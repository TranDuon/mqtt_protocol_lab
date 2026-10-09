"""Bai 1 - Subscriber: lang nghe topic iot/lab/message va in message nhan duoc."""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # thu muc goc lab, de import common/
from common import config


def on_connect(client, userdata, flags, reason_code, properties):
    """Duoc goi khi broker tra ve CONNACK."""
    if reason_code.is_failure:
        print(f"LOI: Broker tu choi ket noi: {reason_code}")
        client.disconnect()  # dung han thay vi de paho thu ket noi lai mai
        return
    # Subscribe trong on_connect de tu dang ky lai neu bi mat ket noi roi ket noi lai.
    client.subscribe(config.TOPIC_MESSAGE, qos=1)
    print(f"Da ket noi broker {config.BROKER_HOST}:{config.BROKER_PORT}")
    print(f"Dang lang nghe topic {config.TOPIC_MESSAGE} ... (Ctrl+C de thoat)\n")


def on_message(client, userdata, msg):
    """Duoc goi moi khi broker chuyen toi mot message thuoc topic da subscribe."""
    payload = msg.payload.decode("utf-8", errors="replace")  # payload la bytes
    received_at = datetime.now().strftime("%H:%M:%S")
    print("Nhan duoc message:")
    print(f"Topic: {msg.topic}")
    print(f"Payload: {payload}")
    print(f"Time: {received_at}\n")


def main():
    client = config.create_client("subscriber_bai1")
    client.on_connect = on_connect
    client.on_message = on_message

    config.connect_or_exit(client)
    try:
        client.loop_forever()  # chay vong lap mang tren main thread, cho den khi Ctrl+C
    except KeyboardInterrupt:
        print("Da dung subscriber.")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
