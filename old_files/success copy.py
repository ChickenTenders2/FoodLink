import logging
import time
import uuid
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo


class Success():
    def __init__(self):
        # Unique id is generated every time a connection is established.
        unique_id = str(uuid.uuid4())

        self.telemetry_with_ts = {
            "ts": int(round(time.time() * 1000)),
            "values": {"message": "Added"}
        }

        self.client = TBDeviceMqttClient(
            "thingsboard.cs.cf.ac.uk",
            username="FoodLinkAccess2025",
            client_id=f"client_{unique_id}"
        )

        # Connect to ThingsBoard.
        self.client.connect()

    # Sends the success message to ThingsBoard.  
    def alert(self):

        result = self.client.send_telemetry(self.telemetry_with_ts)

        if result.get() == TBPublishInfo.TB_ERR_SUCCESS:
            logging.info("Telemetry sent successfully.")
        else:
            logging.error("Failed to send telemetry.")

        # Disconnect to prevent connection conflicts when the next message is sent.
        self.client.disconnect()
