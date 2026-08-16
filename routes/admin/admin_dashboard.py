from flask import Blueprint, render_template, session, flash, redirect, url_for, request

from routes.admin.decorators import admin_required

from esp32s_database import (
    get_all_esp32_devices,
    delete_esp32_device,
    get_all_current_readings,
    get_all_esp32_sensor_history   
)

from users_database import (
    dashboard_users_data,
    delete_user,
    get_all_comments,
    delete_comment,
    get_user_count,
    get_active_user_count,
    get_active_users
)


admin_dashboard = Blueprint(
    "admin_dashboard",
    __name__
)


# ============================================================
# ADMIN DASHBOARD
# ============================================================


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@admin_dashboard.route("/dashboard")
@admin_required
def dashboard_page():

    username = session.get(
        "username",
        "Administrator"
    )


    # ========================================================
    # GET TOTAL USERS
    # ========================================================

    success, total_users = get_user_count()

    if not success:

        flash(
            total_users,
            "error"
        )

        total_users = 0


    # ========================================================
    # GET ACTIVE USERS
    # ========================================================

    success, active_users = get_active_user_count()

    if not success:

        flash(
            active_users,
            "error"
        )

        active_users = 0


    # ========================================================
    # DISPLAY DASHBOARD
    # ========================================================

    return render_template(
        "admin/dashboard.html",

        username=username,

        total_users=total_users,

        active_users=active_users
    )




# ============================================================
# USERS
# ============================================================

@admin_dashboard.route("/users-data")
@admin_required
def users_data():

    success, users = dashboard_users_data()

    if not success:

        flash(
            users,
            "error"
        )

        return render_template(
            "admin/users_data.html",
            users=[]
        )

    return render_template(
        "admin/users_data.html",
        users=users
    )


# ============================================================
# DELETE USER
# ============================================================

@admin_dashboard.route(
    "/users/delete/<int:user_id>",
    methods=["POST"]
)
@admin_required
def delete_user_route(user_id):

    success, message = delete_user(user_id)

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

    return redirect(
        url_for(
            "admin_dashboard.users_data"
        )
    )


# ============================================================
# COMMENTS
# ============================================================

@admin_dashboard.route("/comments")
@admin_required
def comments_data():

    comments = get_all_comments()

    return render_template(
        "admin/comments.html",
        comments=comments
    )


# ============================================================
# DELETE COMMENT
# ============================================================

@admin_dashboard.route(
    "/comments/delete/<int:comment_id>/<int:user_id>",
    methods=["POST"]
)
@admin_required
def delete_comment_route(comment_id, user_id):

    success, message = delete_comment(
        comment_id,
        user_id
    )

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

    return redirect(
        url_for(
            "admin_dashboard.comments_data"
        )
    )


# ============================================================
# ESP32 DEVICES
# ============================================================

@admin_dashboard.route("/devices")
@admin_required
def devices_page():

    success, devices = get_all_esp32_devices()

    if not success:

        flash(
            devices,
            "error"
        )

        return render_template(
            "admin/devices.html",
            devices=[]
        )

    return render_template(
        "admin/devices.html",
        devices=devices
    )


# ============================================================
# DELETE ESP32 DEVICE
# ============================================================

@admin_dashboard.route(
    "/devices/delete/<int:device_id>",
    methods=["POST"]
)
@admin_required
def delete_device_route(device_id):

    success, message = delete_esp32_device(device_id)

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

    return redirect(
        url_for(
            "admin_dashboard.devices_page"
        )
    )


# ============================================================
# CURRENT SOIL DATA
# ============================================================

@admin_dashboard.route("/soil-data")
@admin_required
def soil_data_page():

    # ========================================================
    # GET CURRENT SOIL READINGS
    # ========================================================

    success, result = get_all_current_readings()


    # ========================================================
    # DATABASE ERROR
    # ========================================================

    if not success:

        return render_template(
            "admin/current_soil_data.html",
            devices=[],
            error=result
        )


    # ========================================================
    # CHECK DEVICE STATUS
    # ========================================================

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

            if time_difference <= timedelta(minutes=3):

                device["active"] = True


    # ========================================================
    # DISPLAY CURRENT SOIL DATA
    # ========================================================

    return render_template(
        "admin/current_soil_data.html",
        devices=result,
        error=None
    )


# ============================================================
# ALL ESP32 SOIL HISTORY
# ============================================================

@admin_dashboard.route("/soil-history")
@admin_required
def soil_history_page():

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
    # GET SENSOR HISTORY
    # ========================================================

    success, result = get_all_esp32_sensor_history(
        current_filter
    )

    # ========================================================
    # DATABASE ERROR
    # ========================================================

    if not success:

        return render_template(
            "admin/soil_history_data.html",
            devices=[],
            error=result,
            current_filter=current_filter
        )

    # ========================================================
    # DISPLAY SENSOR HISTORY
    # ========================================================

    return render_template(
        "admin/soil_history_data.html",
        devices=result,
        error=None,
        current_filter=current_filter
    )



# ============================================================
# ACTIVE USERS
# ============================================================

@admin_dashboard.route("/active-users")
@admin_required
def active_users_page():

    success, users = get_active_users()

    if not success:

        flash(
            users,
            "error"
        )

        return render_template(
            "admin/active_users.html",
            users=[]
        )

    return render_template(
        "admin/active_users.html",
        users=users
    )

