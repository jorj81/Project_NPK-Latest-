
from flask import (
    Blueprint,
    render_template,
    session,
    request,
    redirect,
    url_for,
    flash
)


from esp32s_database import (
    create_esp32_device,
    get_farmer_esp32_devices,
    delete_esp32_device,
    get_farmer_current_readings,
    get_farmer_esp32_sensor_history
)


from users_database import (
    add_comment,
    edit_comment,
    delete_comment,
    get_user_comments
)

from routes.farmer.decorators import farmer_required



farmer_dashboard = Blueprint(
    "farmer_dashboard",
    __name__
)



@farmer_dashboard.route("/farmer/dashboard")
@farmer_required
def dashboard_page():

    return render_template(
        "farmer/farmer_dashboard.html"
    )


@farmer_dashboard.route(
    "/farmer/create-device",
    methods=["GET"]
)
@farmer_required
def create_device_page():

    return render_template(
        "farmer/create_mnpk_device.html"
    )



@farmer_dashboard.route(
    "/farmer/create-device",
    methods=["POST"]
)
@farmer_required
def create_device():

    farmer_id = session.get(
        "user_id"
    )


    # --------------------------------------------------------
    # Validate farmer ID
    # --------------------------------------------------------

    if not farmer_id:

        flash(
            "Farmer ID not found in session.",
            "error"
        )

        return redirect(
            url_for(
                "farmer_dashboard.dashboard_page"
            )
        )


    # --------------------------------------------------------
    # Create ESP32 device
    # --------------------------------------------------------

    success, result = create_esp32_device(

        esp32_code=request.form.get(
            "esp32_code"
        ),

        owner_id=farmer_id,

        barangay_id=request.form.get(
            "barangay_id"
        ),

        location=request.form.get(
            "location"
        ),

        ip_address=request.form.get(
            "ip_address"
        )
    )


    # --------------------------------------------------------
    # Handle result
    # --------------------------------------------------------

    if success:

        flash(
            result,
            "success"
        )

    else:

        flash(
            str(result),
            "error"
        )


    # --------------------------------------------------------
    # Return to device registration page
    # --------------------------------------------------------

    return redirect(
        url_for(
            "farmer_dashboard.create_device_page"
        )
    )


@farmer_dashboard.route(
    "/farmer/devices"
)
@farmer_required
def devices_page():

    # --------------------------------------------------------
    # Get logged-in farmer ID
    # --------------------------------------------------------

    farmer_id = session.get(
        "user_id"
    )


    # --------------------------------------------------------
    # Validate farmer ID
    # --------------------------------------------------------

    if not farmer_id:

        flash(
            "Farmer ID not found in session.",
            "error"
        )

        return redirect(
            url_for(
                "auth.login"
            )
        )


    # --------------------------------------------------------
    # Get only this farmer's devices
    # --------------------------------------------------------

    success, devices = get_farmer_esp32_devices(
        farmer_id
    )


    # --------------------------------------------------------
    # Handle database error
    # --------------------------------------------------------

    if not success:

        flash(
            str(devices),
            "error"
        )

        devices = []


    # --------------------------------------------------------
    # Display devices
    # --------------------------------------------------------

    return render_template(
        "farmer/my_devices.html",
        devices=devices
    )


@farmer_dashboard.route(
    "/farmer/delete-device/<int:device_id>",
    methods=["POST"]
)
@farmer_required
def delete_device_route(device_id):

    # --------------------------------------------------------
    # Check logged-in farmer
    # --------------------------------------------------------

    farmer_id = session.get(
        "user_id"
    )


    if not farmer_id:

        flash(
            "Farmer ID not found in session.",
            "error"
        )

        return redirect(
            url_for(
                "auth.login"
            )
        )


    # --------------------------------------------------------
    # Delete ESP32 device
    # --------------------------------------------------------

    success, message = delete_esp32_device(
        device_id
    )


    # --------------------------------------------------------
    # Show result
    # --------------------------------------------------------

    if success:

        flash(
            message,
            "success"
        )

    else:

        flash(
            message,
            "error"
        )


    # --------------------------------------------------------
    # Return to My Devices
    # --------------------------------------------------------

    return redirect(
        url_for(
            "farmer_dashboard.devices_page"
        )
    )


@farmer_dashboard.route(
    "/farmer/soil-data"
)
@farmer_required
def farmer_soil_data_page():


    farmer_id = session.get(
        "user_id"
    )


    # --------------------------------------------------------
    # Validate farmer ID
    # --------------------------------------------------------

    if not farmer_id:

        return render_template(
            "farmer/soil_current_data.html",
            devices=[],
            error="Farmer ID not found in session"
        )


    # --------------------------------------------------------
    # Get only this farmer's ESP32 devices
    # --------------------------------------------------------

    success, result = get_farmer_current_readings(
        farmer_id
    )


    # --------------------------------------------------------
    # Check database result
    # --------------------------------------------------------

    if not success:

        return render_template(
            "farmer/soil_current_data.html",
            devices=[],
            error=result
        )


    # --------------------------------------------------------
    # CHECK DEVICE STATUS
    # --------------------------------------------------------

    from datetime import datetime, timedelta

    current_time = datetime.now()


    for device in result:

        # ----------------------------------------------------
        # DEFAULT STATUS
        # ----------------------------------------------------

        device["active"] = False


        # ----------------------------------------------------
        # CHECK IF READING EXISTS
        # ----------------------------------------------------

        if device["recorded_at"]:

            time_difference = (
                current_time -
                device["recorded_at"]
            )


            # ------------------------------------------------
            # ACTIVE IF READING IS WITHIN 3 MINUTES
            # ------------------------------------------------

            if (
                time_difference >= timedelta(0)
                and
                time_difference <= timedelta(minutes=3)
            ):

                device["active"] = True


    # --------------------------------------------------------
    # Display farmer's ESP32 devices
    # --------------------------------------------------------

    return render_template(
        "farmer/soil_current_data.html",
        devices=result,
        error=None
    )



@farmer_dashboard.route(
    "/farmer/comment",
    methods=["GET", "POST"]
)
@farmer_required
def comment_page():

    # ========================================================
    # GET LOGGED-IN FARMER INFORMATION
    # ========================================================

    farmer_id = session.get(
        "user_id"
    )

    username = session.get(
        "username"
    )


    # ========================================================
    # CHECK FARMER SESSION
    # ========================================================

    if not farmer_id or not username:

        return redirect(
            url_for(
                "auth.login"
            )
        )


    # ========================================================
    # ADD COMMENT
    # ========================================================

    if request.method == "POST":

        comment = request.form.get(
            "comment",
            ""
        ).strip()


        # ====================================================
        # ADD COMMENT TO DATABASE
        # ====================================================

        success, message = add_comment(
            farmer_id,
            username,
            comment
        )


        # ====================================================
        # DISPLAY RESULT
        # ====================================================

        if success:

            flash(
                message,
                "success"
            )

        else:

            flash(
                message,
                "error"
            )


        # ====================================================
        # RETURN TO COMMENT PAGE
        # ====================================================

        return redirect(
            url_for(
                "farmer_dashboard.comment_page"
            )
        )


    # ========================================================
    # GET FARMER'S EXISTING COMMENTS
    # ========================================================

    success, comments = get_user_comments(
        farmer_id
    )


    # ========================================================
    # DATABASE ERROR
    # ========================================================

    if not success:

        return render_template(
            "farmer/comments.html",
            comments=[],
            error=comments
        )


    # ========================================================
    # DISPLAY COMMENTS
    # ========================================================

    return render_template(
        "farmer/comments.html",
        comments=comments,
        error=None
    )


@farmer_dashboard.route(
    "/farmer/comment/edit/<int:comment_id>",
    methods=["POST"]
)
@farmer_required
def edit_comment_page(comment_id):

    farmer_id = session.get(
        "user_id"
    )


    # ========================================================
    # CHECK FARMER SESSION
    # ========================================================

    if not farmer_id:

        return redirect(
            url_for(
                "auth.login"
            )
        )


    # ========================================================
    # GET NEW COMMENT
    # ========================================================

    comment = request.form.get(
        "comment",
        ""
    ).strip()


    # ========================================================
    # UPDATE COMMENT
    # ========================================================

    success, message = edit_comment(
        comment_id,
        farmer_id,
        comment
    )


    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    if success:

        flash(
            message,
            "success"
        )

    else:

        flash(
            message,
            "error"
        )


    # ========================================================
    # RETURN TO COMMENTS PAGE
    # ========================================================

    return redirect(
        url_for(
            "farmer_dashboard.comment_page"
        )
    )


@farmer_dashboard.route(
    "/farmer/comment/delete/<int:comment_id>",
    methods=["POST"]
)
@farmer_required
def delete_comment_page(comment_id):

    # ========================================================
    # GET LOGGED-IN FARMER ID
    # ========================================================

    farmer_id = session.get(
        "user_id"
    )


    # ========================================================
    # CHECK FARMER SESSION
    # ========================================================

    if not farmer_id:

        return redirect(
            url_for(
                "auth.login"
            )
        )


    # ========================================================
    # DELETE COMMENT
    # ========================================================

    success, message = delete_comment(
        comment_id,
        farmer_id
    )


    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    if success:

        flash(
            message,
            "success"
        )

    else:

        flash(
            message,
            "error"
        )


    # ========================================================
    # RETURN TO COMMENTS PAGE
    # ========================================================

    return redirect(
        url_for(
            "farmer_dashboard.comment_page"
        )
    )


@farmer_dashboard.route("/farmer/soil-history")
@farmer_required
def farmer_soil_history_page():

    # ========================================================
    # GET LOGGED-IN FARMER ID
    # ========================================================

    farmer_id = session.get(
        "user_id"
    )


    # ========================================================
    # CHECK FARMER SESSION
    # ========================================================

    if not farmer_id:

        return redirect(
            url_for("login.login_page")
        )


    # ========================================================
    # GET SELECTED TIME FILTER
    # ========================================================

    current_filter = request.args.get(
        "filter",
        "last_30_minutes"
    )


    # ========================================================
    # ALLOWED FILTERS
    # ========================================================

    allowed_filters = [

        "last_30_minutes",

        "last_1_hour",

        "last_12_hours",

        "last_24_hours",

        "last_7_days",

        "last_30_days",

        "all"

    ]


    # ========================================================
    # VALIDATE FILTER
    # ========================================================

    if current_filter not in allowed_filters:

        current_filter = "last_30_minutes"


    # ========================================================
    # GET FARMER'S SENSOR HISTORY
    # ========================================================

    success, result = get_farmer_esp32_sensor_history(
        farmer_id,
        current_filter
    )


    # ========================================================
    # DATABASE ERROR
    # ========================================================

    if not success:

        return render_template(
            "farmer/soil_history_data.html",

            devices=[],

            error=result,

            current_filter=current_filter
        )


    # ========================================================
    # DISPLAY FARMER'S SENSOR HISTORY
    # ========================================================

    return render_template(
        "farmer/soil_history_data.html",

        devices=result,

        error=None,

        current_filter=current_filter
    )
