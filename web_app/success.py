import logging
import time
import uuid
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo

def send_success_alert():
    """
    Sends a "success" telemetry message to ThingsBoard.

    This function:
    - Generates a unique client ID using UUID.
    - Creates a timestamped telemetry payload with the message "Added".
    - Connects to the ThingsBoard server via MQTT.
    - Sends the telemetry data.
    - Logs whether the send was successful or not.
    - Ensures the client is disconnected after the attempt.

    Logging:
        - Success or failure of the telemetry send.
        - Any exceptions encountered during the process.

    Note:
        - Uses hardcoded ThingsBoard server URL and device access token.
        - Uses a new MQTT client instance for each call to avoid conflicts.
    """
    # Unique id is generated every time a connection is established.
    unique_id = str(uuid.uuid4())

    telemetry_with_ts = {
        "ts": int(round(time.time() * 1000)),
        "values": {"message": "Added"}
    }

    client = TBDeviceMqttClient(
        "thingsboard.cs.cf.ac.uk",
        username="FoodLinkAccess2025",
        client_id=f"client_{unique_id}"
    )

    try:
        # Connect to ThingsBoard.
        client.connect(timeout = 10)

        # Sends the success message to ThingsBoard.
        result = client.send_telemetry(telemetry_with_ts)

        if result.get() == TBPublishInfo.TB_ERR_SUCCESS:
            logging.info("Telemetry sent successfully.")
        else:
            logging.error("Failed to send telemetry.")

    except Exception as e:
         logging.error(f"[ThingsBoard Error] {e}")
    finally:
        try:
            # Disconnect to prevent connection conflicts when the next message is sent.
            client.disconnect()
        except Exception:
            # If connection was never made, disconnect might fail — ignore silently
            pass
