

import requests


from esp32s_database import (
    get_all_esp32_devices,
    save_esp32_reading
)


class ESP32Client:



    def __init__(
        self,
        ip_address,
        timeout=1
    ):

        if not ip_address:

            raise ValueError(
                "ESP32 IP address is required"
            )

        self.ip_address = str(
            ip_address
        ).strip()

        self.base_url = (
            f"http://{self.ip_address}"
        )

        self.timeout = timeout

        self.session = requests.Session()


    # ========================================================
    # GET SENSOR DATA
    # ========================================================

    def get_sensor_data(self):

        url = f"{self.base_url}/data"

        try:

            response = self.session.get(
                url,
                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            return {
                "success": True,
                "data": data,
                "error": None
            }


        # ----------------------------------------------------
        # TIMEOUT
        # ----------------------------------------------------

        except requests.exceptions.Timeout:

            return {
                "success": False,
                "data": None,
                "error": "Request timed out"
            }


        # ----------------------------------------------------
        # CONNECTION ERROR
        # ----------------------------------------------------

        except requests.exceptions.ConnectionError:

            return {
                "success": False,
                "data": None,
                "error": "Could not connect to ESP32"
            }


        # ----------------------------------------------------
        # HTTP ERROR
        # ----------------------------------------------------

        except requests.exceptions.HTTPError as e:

            return {
                "success": False,
                "data": None,
                "error": f"HTTP error: {e}"
            }


        # ----------------------------------------------------
        # INVALID JSON
        # ----------------------------------------------------

        except ValueError:

            return {
                "success": False,
                "data": None,
                "error": "Invalid JSON received"
            }


        # ----------------------------------------------------
        # OTHER REQUEST ERROR
        # ----------------------------------------------------

        except requests.exceptions.RequestException as e:

            return {
                "success": False,
                "data": None,
                "error": f"Request failed: {e}"
            }



def get_all_esp32_device_connections():

    result = get_all_esp32_devices()


    if not result:

        return []



    if isinstance(result, tuple):

        success, devices = result

        if not success:

            print()
            print("Database error:")
            print(devices)

            return []

    else:

        devices = result


    if not devices:

        return []


    device_connections = []


    for device in devices:

        # ----------------------------------------------------
        # Get database device ID
        # ----------------------------------------------------

        device_id = device.get(
            "device_id"
        )


        # ----------------------------------------------------
        # Get ESP32 IP address
        # ----------------------------------------------------

        ip_address = device.get(
            "ip_address"
        )


        # ----------------------------------------------------
        # Skip devices without IP
        # ----------------------------------------------------

        if not ip_address:

            continue


        # ----------------------------------------------------
        # Clean IP address
        # ----------------------------------------------------

        ip_address = str(
            ip_address
        ).strip()


        # ----------------------------------------------------
        # Avoid duplicate IP addresses
        # ----------------------------------------------------

        duplicate = False


        for existing_device in device_connections:

            if (
                existing_device["ip_address"]
                == ip_address
            ):

                duplicate = True

                break


        if duplicate:

            continue


        # ----------------------------------------------------
        # Store device ID and IP together
        # ----------------------------------------------------

        device_connections.append(
            {
                "device_id": device_id,
                "ip_address": ip_address
            }
        )


    return device_connections


# ============================================================
# CONNECT TO ALL ESP32 DEVICES
# ============================================================

def test_all_esp32_devices():

    print()
    print("========================================")
    print("        ESP32 SENSOR TEST")
    print("========================================")


    # ========================================================
    # GET DEVICE CONNECTIONS
    # ========================================================

    print()
    print("Retrieving ESP32 devices...")
    print("----------------------------------------")


    devices = get_all_esp32_device_connections()


    # ========================================================
    # NO DEVICES
    # ========================================================

    if not devices:

        print()
        print("No ESP32 devices found.")

        print()
        print("========================================")
        print("             TEST FINISHED")
        print("========================================")

        return


    # ========================================================
    # DISPLAY DEVICES
    # ========================================================

    print()

    print(
        f"Found {len(devices)} ESP32 device(s)."
    )

    print()


    for index, device in enumerate(
        devices,
        start=1
    ):

        print(
            f"{index}. "
            f"Device ID: {device['device_id']} "
            f"| IP: {device['ip_address']}"
        )


    # ========================================================
    # CONNECT TO EACH ESP32
    # ========================================================

    print()
    print("========================================")
    print("     CONNECTING TO ESP32 DEVICES")
    print("========================================")


    for index, device in enumerate(
        devices,
        start=1
    ):

        # ----------------------------------------------------
        # Get database device ID
        # ----------------------------------------------------

        device_id = device["device_id"]


        # ----------------------------------------------------
        # Get IP address
        #
        # THIS IS THE ONLY VALUE USED FOR CONNECTION
        # ----------------------------------------------------

        ip_address = device["ip_address"]


        print()
        print("----------------------------------------")

        print(
            f"ESP32 #{index}"
        )

        print(
            f"Device ID  : {device_id}"
        )

        print(
            f"IP Address : {ip_address}"
        )

        print(
            "Connecting..."
        )

        print("----------------------------------------")


        # ====================================================
        # CREATE ESP32 CLIENT
        # ====================================================

        try:

            client = ESP32Client(
                ip_address=ip_address
            )


        except ValueError as e:

            print()
            print(
                f"Error creating client: {e}"
            )

            continue


        # ====================================================
        # GET SENSOR DATA
        # ====================================================

        result = client.get_sensor_data()


        # ====================================================
        # SUCCESS
        # ====================================================

        if result["success"]:

            data = result["data"]


            print()
            print("Connection successful!")


            # =================================================
            # GET SENSOR VALUES
            # =================================================

            soil_moisture = data.get(
                "soil_moisture"
            )

            nitrogen = data.get(
                "nitrogen"
            )

            phosphorus = data.get(
                "phosphorus"
            )

            potassium = data.get(
                "potassium"
            )


            # =================================================
            # DISPLAY SENSOR DATA
            # =================================================

            print()
            print("ESP32 DATA")
            print("----------------------------------------")


            print(
                f"Device ID     : "
                f"{device_id}"
            )


            print(
                f"IP Address    : "
                f"{ip_address}"
            )


            print(
                f"Device Code   : "
                f"{data.get('device_code', 'N/A')}"
            )


            print(
                f"Soil Moisture : "
                f"{soil_moisture}"
            )


            print(
                f"Nitrogen      : "
                f"{nitrogen}"
            )


            print(
                f"Phosphorus    : "
                f"{phosphorus}"
            )


            print(
                f"Potassium     : "
                f"{potassium}"
            )


            print("----------------------------------------")


            # =================================================
            # SAVE READING TO DATABASE
            # =================================================

            print()
            print("Saving sensor reading...")
            print("----------------------------------------")


            save_success, save_message = (
                save_esp32_reading(
                    esp32_device_id=device_id,
                    soil_moisture=soil_moisture,
                    nitrogen=nitrogen,
                    phosphorus=phosphorus,
                    potassium=potassium
                )
            )


            # =================================================
            # SAVE SUCCESS
            # =================================================

            if save_success:

                print(
                    "Sensor reading saved successfully."
                )

                print(
                    f"Saved under device ID: "
                    f"{device_id}"
                )


            # =================================================
            # SAVE ERROR
            # =================================================

            else:

                print(
                    "Failed to save sensor reading."
                )

                print(
                    f"Database error: "
                    f"{save_message}"
                )


            # =================================================
            # RAW JSON
            # =================================================

            print()
            print("Raw JSON:")

            print(data)


        # ====================================================
        # CONNECTION ERROR
        # ====================================================

        else:

            print()
            print("Connection failed!")


            print()
            print(
                f"Device ID : "
                f"{device_id}"
            )


            print(
                f"IP Address: "
                f"{ip_address}"
            )


            print(
                f"Error: "
                f"{result['error']}"
            )


    # ========================================================
    # FINISHED
    # ========================================================

    print()
    print("========================================")
    print("             TEST FINISHED")
    print("========================================")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    test_all_esp32_devices()

