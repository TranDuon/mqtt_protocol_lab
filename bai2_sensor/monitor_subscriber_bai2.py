"""Bai 2 - Monitoring Subscriber: nhan du lieu cam bien, in ra va canh bao khi vuot nguong."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # thu muc goc lab, de import common/
from common import config

TEMP_HIGH = 35.0      # nhiet do > 35 C  -> canh bao
HUMIDITY_LOW = 40.0   # do am   < 40 %  -> canh bao


def check_alerts(temperature, humidity):
    """Tra ve danh sach canh bao; hai dieu kien kiem tra doc lap nen co the co ca hai."""
    alerts = []
    if temperature > TEMP_HIGH:
        alerts.append("CANH BAO: Nhiet do cao")
    if humidity < HUMIDITY_LOW:
        alerts.append("CANH BAO: Do am thap")
    return alerts


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"LOI: Broker tu choi ket noi: {reason_code}")
        client.disconnect()
        return
    topics = userdata["topics"]
    client.subscribe([(topic, 1) for topic in topics])  # subscribe nhieu topic trong 1 goi SUBSCRIBE
    print(f"Da ket noi broker {config.BROKER_HOST}:{config.BROKER_PORT}")
    print(f"Dang giam sat: {', '.join(topics)} (Ctrl+C de thoat)\n")


def on_message(client, userdata, msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg.topic}")
    # Bat loi o day: neu exception lot ra ngoai callback, paho se dung loop_forever() va monitor bi tat.
    try:
        data = json.loads(msg.payload)  # chuoi JSON -> dict
        device_id = data["device_id"]
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(f"LOI: Payload khong phai JSON hop le: {msg.payload!r}\n")
        return
    except (KeyError, TypeError, ValueError):
        print(f"LOI: JSON thieu hoac sai truong device_id/temperature/humidity: {msg.payload!r}\n")
        return

    print(f"Device: {device_id}")
    print(f"Temperature: {temperature} C")
    print(f"Humidity: {humidity} %")
    for alert in check_alerts(temperature, humidity):
        print(alert)
    print()


def main():
    parser = argparse.ArgumentParser(description="Bai 2 - Monitoring subscriber")
    parser.add_argument("devices", nargs="*", default=["sensor01"],
                        help="device_id can giam sat (mac dinh: sensor01; dung + de nghe moi sensor)")
    args = parser.parse_args()

    client = config.create_client("monitor_bai2")
    client.user_data_set({"topics": [config.topic_data(d) for d in args.devices]})
    client.on_connect = on_connect
    client.on_message = on_message

    config.connect_or_exit(client)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Da dung monitor.")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
