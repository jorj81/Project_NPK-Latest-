from users_database import connect_database


def create_esp32_device(
esp32_code,
    owner_id,
    barangay_id,
    location,
    ip_address=None
):

    connection = None
    cursor = None

    try:


        if not esp32_code:
            return False, "ESP32 code is required"

        if not owner_id:
            return False, "Owner ID is required"

        if not barangay_id:
            return False, "Barangay ID is required"

        if not location:
            return False, "Location is required"

        if ip_address:
            ip_address = ip_address.strip()

            if ip_address == "":
                ip_address = None


        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Check if ESP32 code already exists
        # ----------------------------------------------------

        check_query = """
            SELECT id
            FROM esp32_device
            WHERE esp32_code = %s
            LIMIT 1
        """

        cursor.execute(
            check_query,
            (esp32_code,)
        )

        existing_device = cursor.fetchone()

        if existing_device:

            return False, "ESP32 code already exists"

        # ----------------------------------------------------
        # Insert ESP32 device
        # ----------------------------------------------------

        insert_query = """
            INSERT INTO esp32_device (
                esp32_code,
                owner_id,
                barangay_id,
                location,
                ip_address
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """

        cursor.execute(
            insert_query,
            (
                esp32_code,
                owner_id,
                barangay_id,
                location,
                ip_address
            )
        )

        # ----------------------------------------------------
        # Save changes
        # ----------------------------------------------------

        connection.commit()

        # ----------------------------------------------------
        # Get newly created device ID
        # ----------------------------------------------------

        device_id = cursor.lastrowid

        return True, {
            "message": "ESP32 device created successfully",
            "device_id": device_id,
            "esp32_code": esp32_code,
            "owner_id": owner_id,
            "barangay_id": barangay_id,
            "location": location,
            "ip_address": ip_address
        }

    except Error as e:

        if connection:
            connection.rollback()

        print(f"Create ESP32 device error: {e}")

        return False, f"Database error: {e}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

def get_all_esp32_devices():

    connection = None
    cursor = None

    try:

        # ----------------------------------------------------
        # Connect to database
        # ----------------------------------------------------

        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        # ----------------------------------------------------
        # Create dictionary cursor
        # ----------------------------------------------------

        cursor = connection.cursor(dictionary=True)

        # ----------------------------------------------------
        # Get all ESP32 devices
        # ----------------------------------------------------

        query = """
            SELECT
                e.id AS device_id,
                e.esp32_code,

                e.owner_id,
                u.username AS owner_name,
                ur.role_name AS owner_role,

                e.barangay_id,
                b.barangay_name,

                e.location,
                e.ip_address

            FROM esp32_device e

            LEFT JOIN users u
                ON e.owner_id = u.id

            LEFT JOIN user_roles ur
                ON u.user_role_id = ur.id

            LEFT JOIN barangays b
                ON e.barangay_id = b.id

            ORDER BY e.id ASC
        """

        cursor.execute(query)

        devices = cursor.fetchall()

        # ----------------------------------------------------
        # Return devices
        # ----------------------------------------------------

        return True, devices

    except Error as e:

        print(f"Get all ESP32 devices error: {e}")

        return False, f"Database error: {e}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

def delete_esp32_device(device_id):

    connection = None
    cursor = None

    try:

        # ----------------------------------------------------
        # Validate device ID
        # ----------------------------------------------------

        if not device_id:
            return False, "Device ID is required"

        # ----------------------------------------------------
        # Connect to database
        # ----------------------------------------------------

        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Check if device exists
        # ----------------------------------------------------

        check_query = """
            SELECT id
            FROM esp32_device
            WHERE id = %s
            LIMIT 1
        """

        cursor.execute(
            check_query,
            (device_id,)
        )

        device = cursor.fetchone()

        if not device:
            return False, "ESP32 device not found"

        # ----------------------------------------------------
        # Delete ESP32 device
        # ----------------------------------------------------

        delete_query = """
            DELETE FROM esp32_device
            WHERE id = %s
        """

        cursor.execute(
            delete_query,
            (device_id,)
        )

        # ----------------------------------------------------
        # Save changes
        # ----------------------------------------------------

        connection.commit()

        # ----------------------------------------------------
        # Check if deletion happened
        # ----------------------------------------------------

        if cursor.rowcount == 0:

            return False, "ESP32 device could not be deleted"

        return True, "ESP32 device deleted successfully"

    except Error as e:

        if connection:
            connection.rollback()

        print(f"Delete ESP32 device error: {e}")

        return False, f"Database error: {e}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()



def save_esp32_current_reading(
    esp32_device_id,
    soil_moisture,
    nitrogen,
    phosphorus,
    potassium
):

    connection = None
    cursor = None

    try:

        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor()

        query = """
            INSERT INTO esp32_current_reading
            (
                esp32_device_id,
                soil_moisture,
                nitrogen,
                phosphorus,
                potassium,
                recorded_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP
            )

            ON DUPLICATE KEY UPDATE

                soil_moisture = VALUES(soil_moisture),
                nitrogen = VALUES(nitrogen),
                phosphorus = VALUES(phosphorus),
                potassium = VALUES(potassium),
                recorded_at = CURRENT_TIMESTAMP
        """

        values = (
            esp32_device_id,
            soil_moisture,
            nitrogen,
            phosphorus,
            potassium
        )

        cursor.execute(query, values)

        connection.commit()

        return True, "Current reading saved successfully"

    except Error as e:

        if connection:
            connection.rollback()

        print(f"Save current ESP32 reading error: {e}")

        return False, f"Database error: {e}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

def save_esp32_sensor_history(
    esp32_device_id,
    soil_moisture,
    nitrogen,
    phosphorus,
    potassium
):

    connection = None
    cursor = None

    try:

        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor()

        query = """
            INSERT INTO esp32_sensor_history
            (
                esp32_device_id,
                soil_moisture,
                nitrogen,
                phosphorus,
                potassium,
                recorded_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP
            )
        """

        values = (
            esp32_device_id,
            soil_moisture,
            nitrogen,
            phosphorus,
            potassium
        )

        cursor.execute(query, values)

        connection.commit()

        return True, "Sensor history saved successfully"

    except Error as e:

        if connection:
            connection.rollback()

        print(f"Save ESP32 sensor history error: {e}")

        return False, f"Database error: {e}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


def save_esp32_reading(
    esp32_device_id,
    soil_moisture,
    nitrogen,
    phosphorus,
    potassium
):

    connection = None
    cursor = None

    try:

        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor()

        # ------------------------------------------------
        # Save history
        # ------------------------------------------------

        history_query = """
            INSERT INTO esp32_sensor_history
            (
                esp32_device_id,
                soil_moisture,
                nitrogen,
                phosphorus,
                potassium,
                recorded_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP
            )
        """

        history_values = (
            esp32_device_id,
            soil_moisture,
            nitrogen,
            phosphorus,
            potassium
        )

        cursor.execute(
            history_query,
            history_values
        )

        # ------------------------------------------------
        # Save/update current reading
        # ------------------------------------------------

        current_query = """
            INSERT INTO esp32_current_reading
            (
                esp32_device_id,
                soil_moisture,
                nitrogen,
                phosphorus,
                potassium,
                recorded_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP
            )

            ON DUPLICATE KEY UPDATE

                soil_moisture = VALUES(soil_moisture),
                nitrogen = VALUES(nitrogen),
                phosphorus = VALUES(phosphorus),
                potassium = VALUES(potassium),
                recorded_at = CURRENT_TIMESTAMP
        """

        current_values = (
            esp32_device_id,
            soil_moisture,
            nitrogen,
            phosphorus,
            potassium
        )

        cursor.execute(
            current_query,
            current_values
        )

        # ------------------------------------------------
        # Commit both operations
        # ------------------------------------------------

        connection.commit()

        return True, "ESP32 reading saved successfully"

    except Error as e:

        if connection:
            connection.rollback()

        print(f"Save ESP32 reading error: {e}")

        return False, f"Database error: {e}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

def get_all_current_readings():

    connection = None
    cursor = None

    try:

        connection = connect_database()

        if connection is None:

            return False, "Database connection failed"

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT

                esp32_device.id AS device_id,

                esp32_device.location,

                barangays.barangay_name,

                esp32_current_reading.id AS reading_id,

                esp32_current_reading.soil_moisture,

                esp32_current_reading.nitrogen,

                esp32_current_reading.phosphorus,

                esp32_current_reading.potassium,

                esp32_current_reading.recorded_at

            FROM esp32_device

            LEFT JOIN barangays

                ON esp32_device.barangay_id =
                   barangays.id

            LEFT JOIN esp32_current_reading

                ON esp32_device.id =
                   esp32_current_reading.esp32_device_id

            ORDER BY
                esp32_device.id ASC
        """

        cursor.execute(query)

        readings = cursor.fetchall()

        return True, readings

    except Exception as e:

        print(
            "Error getting all current readings:",
            e
        )

        return False, str(e)

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

def get_all_esp32_sensor_history(
    filter_type="last_30_minutes"
):

    connection = None
    cursor = None

    try:

        # ----------------------------------------------------
        # Connect to database
        # ----------------------------------------------------

        connection = connect_database()

        if connection is None:

            return False, "Database connection failed"


        # ----------------------------------------------------
        # Create dictionary cursor
        # ----------------------------------------------------

        cursor = connection.cursor(
            dictionary=True
        )


        # ----------------------------------------------------
        # Validate filter
        # ----------------------------------------------------

        allowed_filters = [

            "last_30_minutes",

            "last_1_hour",

            "last_12_hours",

            "last_24_hours",

            "last_7_days",

            "last_30_days",

            "all"

        ]


        if filter_type not in allowed_filters:

            filter_type = "last_30_minutes"


        # ----------------------------------------------------
        # Determine SQL time condition
        # ----------------------------------------------------

        time_condition = ""


        if filter_type == "last_30_minutes":

            time_condition = """
                AND esp32_sensor_history.recorded_at
                    >= NOW() - INTERVAL 30 MINUTE
            """


        elif filter_type == "last_1_hour":

            time_condition = """
                AND esp32_sensor_history.recorded_at
                    >= NOW() - INTERVAL 1 HOUR
            """


        elif filter_type == "last_12_hours":

            time_condition = """
                AND esp32_sensor_history.recorded_at
                    >= NOW() - INTERVAL 12 HOUR
            """


        elif filter_type == "last_24_hours":

            time_condition = """
                AND esp32_sensor_history.recorded_at
                    >= NOW() - INTERVAL 24 HOUR
            """


        elif filter_type == "last_7_days":

            time_condition = """
                AND esp32_sensor_history.recorded_at
                    >= NOW() - INTERVAL 7 DAY
            """


        elif filter_type == "last_30_days":

            time_condition = """
                AND esp32_sensor_history.recorded_at
                    >= NOW() - INTERVAL 30 DAY
            """


        elif filter_type == "all":

            time_condition = ""


        # ----------------------------------------------------
        # Get devices and filtered history
        # ----------------------------------------------------

        query = f"""
            SELECT

                esp32_device.id AS device_id,

                esp32_device.location,

                barangays.barangay_name,

                esp32_sensor_history.id AS history_id,

                esp32_sensor_history.soil_moisture,

                esp32_sensor_history.nitrogen,

                esp32_sensor_history.phosphorus,

                esp32_sensor_history.potassium,

                esp32_sensor_history.recorded_at

            FROM esp32_device

            LEFT JOIN barangays

                ON esp32_device.barangay_id =
                   barangays.id

            LEFT JOIN esp32_sensor_history

                ON esp32_device.id =
                   esp32_sensor_history.esp32_device_id

                {time_condition}

            ORDER BY

                esp32_device.id ASC,

                esp32_sensor_history.recorded_at DESC
        """


        # ----------------------------------------------------
        # Execute query
        # ----------------------------------------------------

        cursor.execute(query)


        rows = cursor.fetchall()


        # ----------------------------------------------------
        # Group history by device
        # ----------------------------------------------------

        devices = {}


        for row in rows:

            device_id = row["device_id"]


            # ------------------------------------------------
            # Create device if it does not exist
            # ------------------------------------------------

            if device_id not in devices:

                devices[device_id] = {

                    "device_id":
                        device_id,

                    "location":
                        row["location"],

                    "barangay_name":
                        row["barangay_name"],

                    "history": []

                }


            # ------------------------------------------------
            # Add history record
            # ------------------------------------------------

            if row["history_id"] is not None:

                devices[device_id]["history"].append({

                    "history_id":
                        row["history_id"],

                    "soil_moisture":
                        row["soil_moisture"],

                    "nitrogen":
                        row["nitrogen"],

                    "phosphorus":
                        row["phosphorus"],

                    "potassium":
                        row["potassium"],

                    "recorded_at":
                        row["recorded_at"]

                })


        # ----------------------------------------------------
        # Convert dictionary to list
        # ----------------------------------------------------

        devices = list(
            devices.values()
        )


        # ----------------------------------------------------
        # Return grouped devices
        # ----------------------------------------------------

        return True, devices


    except Error as e:

        print(
            f"Get all ESP32 sensor history error: {e}"
        )

        return False, f"Database error: {e}"


    finally:

        if cursor is not None:

            cursor.close()


        if connection is not None:

            if connection.is_connected():

                connection.close()



def get_farmer_esp32_devices(owner_id):

    connection = None
    cursor = None

    try:

        # ----------------------------------------------------
        # Validate owner ID
        # ----------------------------------------------------

        if not owner_id:
            return False, "Owner ID is required"

        # ----------------------------------------------------
        # Connect to database
        # ----------------------------------------------------

        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor(dictionary=True)

        # ----------------------------------------------------
        # Get only devices belonging to this farmer
        # ----------------------------------------------------

        query = """
            SELECT
                e.id AS device_id,
                e.esp32_code,

                e.owner_id,
                u.username AS owner_name,
                ur.role_name AS owner_role,

                e.barangay_id,
                b.barangay_name,

                e.location,
                e.ip_address

            FROM esp32_device e

            LEFT JOIN users u
                ON e.owner_id = u.id

            LEFT JOIN user_roles ur
                ON u.user_role_id = ur.id

            LEFT JOIN barangays b
                ON e.barangay_id = b.id

            WHERE e.owner_id = %s

            ORDER BY e.id ASC
        """

        cursor.execute(
            query,
            (owner_id,)
        )

        devices = cursor.fetchall()

        return True, devices

    except Error as e:

        print(f"Get farmer ESP32 devices error: {e}")

        return False, f"Database error: {e}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

def get_farmer_current_readings(farmer_id):

    connection = None
    cursor = None

    try:

        # ----------------------------------------------------
        # Validate farmer ID
        # ----------------------------------------------------

        if not farmer_id:

            return False, "Farmer ID is required"


        # ----------------------------------------------------
        # Connect to database
        # ----------------------------------------------------

        connection = connect_database()

        if connection is None:

            return False, "Database connection failed"


        # ----------------------------------------------------
        # Create dictionary cursor
        # ----------------------------------------------------

        cursor = connection.cursor(
            dictionary=True
        )


        # ----------------------------------------------------
        # Get farmer's ESP32 devices
        # and their current readings
        # ----------------------------------------------------

        query = """
            SELECT

                esp32_device.id AS device_id,

                esp32_device.esp32_code,

                esp32_device.owner_id,

                esp32_device.location,

                esp32_device.ip_address,

                barangays.barangay_name,

                esp32_current_reading.soil_moisture,

                esp32_current_reading.nitrogen,

                esp32_current_reading.phosphorus,

                esp32_current_reading.potassium,

                esp32_current_reading.recorded_at

            FROM esp32_device

            LEFT JOIN barangays

                ON esp32_device.barangay_id =
                   barangays.id

            LEFT JOIN esp32_current_reading

                ON esp32_device.id =
                   esp32_current_reading.esp32_device_id

            WHERE esp32_device.owner_id = %s

            ORDER BY

                esp32_device.id ASC
        """


        # ----------------------------------------------------
        # Execute query
        # ----------------------------------------------------

        cursor.execute(
            query,
            (farmer_id,)
        )


        # ----------------------------------------------------
        # Get all devices
        # ----------------------------------------------------

        devices = cursor.fetchall()


        # ----------------------------------------------------
        # Return devices
        # ----------------------------------------------------

        return True, devices


    except Error as e:

        print(
            f"Get farmer current readings error: {e}"
        )

        return False, f"Database error: {e}"


    finally:

        # ----------------------------------------------------
        # Close cursor
        # ----------------------------------------------------

        if cursor is not None:

            cursor.close()


        # ----------------------------------------------------
        # Close connection
        # ----------------------------------------------------

        if connection is not None:

            if connection.is_connected():

                connection.close()

def get_farmer_esp32_sensor_history(
    farmer_id,
    current_filter="last_30_minutes"
):

    connection = None
    cursor = None

    try:

        # ----------------------------------------------------
        # Validate farmer ID
        # ----------------------------------------------------

        if not farmer_id:

            return False, "Farmer ID is required"


        # ----------------------------------------------------
        # Connect to database
        # ----------------------------------------------------

        connection = connect_database()

        if connection is None:

            return False, "Database connection failed"


        # ----------------------------------------------------
        # Create dictionary cursor
        # ----------------------------------------------------

        cursor = connection.cursor(
            dictionary=True
        )


        # ----------------------------------------------------
        # Determine history time condition
        # ----------------------------------------------------

        history_time_condition = ""


        if current_filter == "last_30_minutes":

            history_time_condition = """
                AND esp32_sensor_history.recorded_at >=
                    DATE_SUB(NOW(), INTERVAL 30 MINUTE)
            """


        elif current_filter == "last_1_hour":

            history_time_condition = """
                AND esp32_sensor_history.recorded_at >=
                    DATE_SUB(NOW(), INTERVAL 1 HOUR)
            """


        elif current_filter == "last_12_hours":

            history_time_condition = """
                AND esp32_sensor_history.recorded_at >=
                    DATE_SUB(NOW(), INTERVAL 12 HOUR)
            """


        elif current_filter == "last_24_hours":

            history_time_condition = """
                AND esp32_sensor_history.recorded_at >=
                    DATE_SUB(NOW(), INTERVAL 24 HOUR)
            """


        elif current_filter == "last_7_days":

            history_time_condition = """
                AND esp32_sensor_history.recorded_at >=
                    DATE_SUB(NOW(), INTERVAL 7 DAY)
            """


        elif current_filter == "last_30_days":

            history_time_condition = """
                AND esp32_sensor_history.recorded_at >=
                    DATE_SUB(NOW(), INTERVAL 30 DAY)
            """


        elif current_filter == "all":

            history_time_condition = ""


        else:

            current_filter = "last_30_minutes"

            history_time_condition = """
                AND esp32_sensor_history.recorded_at >=
                    DATE_SUB(NOW(), INTERVAL 30 MINUTE)
            """


        # ----------------------------------------------------
        # Get farmer's registered devices
        #
        # IMPORTANT:
        # The time condition is inside the LEFT JOIN.
        # This means the device is still returned even
        # when it has no history for the selected period.
        # ----------------------------------------------------

        query = f"""
            SELECT

                esp32_device.id AS device_id,

                esp32_device.owner_id,

                esp32_device.location,

                barangays.barangay_name,

                esp32_sensor_history.id AS history_id,

                esp32_sensor_history.soil_moisture,

                esp32_sensor_history.nitrogen,

                esp32_sensor_history.phosphorus,

                esp32_sensor_history.potassium,

                esp32_sensor_history.recorded_at

            FROM esp32_device

            LEFT JOIN barangays

                ON esp32_device.barangay_id =
                   barangays.id

            LEFT JOIN esp32_sensor_history

                ON esp32_device.id =
                   esp32_sensor_history.esp32_device_id

                {history_time_condition}

            WHERE

                esp32_device.owner_id = %s

            ORDER BY

                esp32_device.id ASC,

                esp32_sensor_history.recorded_at DESC
        """


        # ----------------------------------------------------
        # Execute query
        # ----------------------------------------------------

        cursor.execute(
            query,
            (farmer_id,)
        )


        # ----------------------------------------------------
        # Get records
        # ----------------------------------------------------

        records = cursor.fetchall()


        # ----------------------------------------------------
        # Organize devices
        # ----------------------------------------------------

        devices = {}


        for record in records:

            device_id = record["device_id"]


            # ------------------------------------------------
            # Create device entry
            # ------------------------------------------------

            if device_id not in devices:

                devices[device_id] = {

                    "device_id":
                        device_id,

                    "owner_id":
                        record["owner_id"],

                    "location":
                        record["location"],

                    "barangay_name":
                        record["barangay_name"],

                    "history": []

                }


            # ------------------------------------------------
            # Add history only when it exists
            # ------------------------------------------------

            if record["history_id"] is not None:

                devices[device_id]["history"].append({

                    "history_id":
                        record["history_id"],

                    "soil_moisture":
                        record["soil_moisture"],

                    "nitrogen":
                        record["nitrogen"],

                    "phosphorus":
                        record["phosphorus"],

                    "potassium":
                        record["potassium"],

                    "recorded_at":
                        record["recorded_at"]

                })


        # ----------------------------------------------------
        # Convert dictionary to list
        # ----------------------------------------------------

        devices = list(
            devices.values()
        )


        # ----------------------------------------------------
        # Return devices
        # ----------------------------------------------------

        return True, devices


    except Error as e:

        print(
            f"Get farmer ESP32 sensor history error: {e}"
        )

        return False, f"Database error: {e}"


    finally:

        # ----------------------------------------------------
        # Close cursor
        # ----------------------------------------------------

        if cursor is not None:

            cursor.close()


        # ----------------------------------------------------
        # Close connection
        # ----------------------------------------------------

        if connection is not None:

            if connection.is_connected():

                connection.close()