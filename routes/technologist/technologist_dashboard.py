from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    session,
    redirect,
    url_for
)

from datetime import datetime, timedelta
from routes.technologist.decorators import (
    technologist_required
)


from esp32s_database import (
    get_all_current_readings,
    get_all_esp32_sensor_history,
    get_all_esp32_devices
)


from users_database import (
    add_comment,
    edit_comment,
    delete_comment,
    get_user_comments
)


# ============================================================
# TECHNOLOGIST DASHBOARD BLUEPRINT
# ============================================================

technologist_dashboard = Blueprint(
    "technologist_dashboard",
    __name__
)


# ============================================================
# TECHNOLOGIST DASHBOARD
# ============================================================

@technologist_dashboard.route(
    "/technologist/dashboard"
)
@technologist_required
def dashboard_page():

    return render_template(
        "technologist/dashboard.html"
    )


# ============================================================
# CURRENT ESP32 SOIL DATA
# ============================================================




@technologist_dashboard.route(
    "/technologist/soil-data"
)
@technologist_required
def soil_data_page():

    # ========================================================
    # GET CURRENT ESP32 SOIL READINGS
    # ========================================================

    success, result = get_all_current_readings()


    # ========================================================
    # DATABASE ERROR
    # ========================================================

    if not success:

        return render_template(
            "technologist/current_soil_data.html",
            devices=[],
            error=result
        )


    # ========================================================
    # CHECK DEVICE STATUS
    # ========================================================

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


    # ========================================================
    # DISPLAY CURRENT SOIL DATA
    # ========================================================

    return render_template(
        "technologist/current_soil_data.html",
        devices=result,
        error=None
    )


# ============================================================
# ALL ESP32 SOIL HISTORY
# ============================================================

@technologist_dashboard.route(
    "/technologist/soil-history"
)
@technologist_required
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
            "technologist/soil_history_data.html",

            devices=[],

            error=result,

            current_filter=current_filter
        )


    # ========================================================
    # DISPLAY SENSOR HISTORY
    # ========================================================

    return render_template(
        "technologist/soil_history_data.html",

        devices=result,

        error=None,

        current_filter=current_filter
    )


# ============================================================
# TECHNOLOGIST ESP32 DEVICES
# ============================================================

@technologist_dashboard.route(
    "/technologist/devices"
)
@technologist_required
def technologist_devices_page():

    success, devices = get_all_esp32_devices()


    if not success:

        flash(
            devices,
            "error"
        )

        return render_template(
            "technologist/technologist_devices.html",
            devices=[]
        )


    return render_template(
        "technologist/technologist_devices.html",
        devices=devices
    )


# ============================================================
# TECHNOLOGIST COMMENTS
# ============================================================

@technologist_dashboard.route(
    "/technologist/comment",
    methods=["GET", "POST"]
)
@technologist_required
def comment_page():

    # ========================================================
    # GET LOGGED-IN TECHNOLOGIST INFORMATION
    # ========================================================

    technologist_id = session.get(
        "user_id"
    )

    username = session.get(
        "username"
    )


    # ========================================================
    # CHECK TECHNOLOGIST SESSION
    # ========================================================

    if not technologist_id or not username:

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
            technologist_id,
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
                "technologist_dashboard.comment_page"
            )
        )


    # ========================================================
    # GET TECHNOLOGIST'S EXISTING COMMENTS
    # ========================================================

    success, comments = get_user_comments(
        technologist_id
    )


    # ========================================================
    # DATABASE ERROR
    # ========================================================

    if not success:

        return render_template(
            "technologist/comments.html",
            comments=[],
            error=comments
        )


    # ========================================================
    # DISPLAY COMMENTS
    # ========================================================

    return render_template(
        "technologist/comments.html",
        comments=comments,
        error=None
    )


# ============================================================
# EDIT TECHNOLOGIST COMMENT
# ============================================================

@technologist_dashboard.route(
    "/technologist/comment/edit/<int:comment_id>",
    methods=["POST"]
)
@technologist_required
def edit_comment_page(comment_id):

    # ========================================================
    # GET LOGGED-IN TECHNOLOGIST ID
    # ========================================================

    technologist_id = session.get(
        "user_id"
    )


    # ========================================================
    # CHECK TECHNOLOGIST SESSION
    # ========================================================

    if not technologist_id:

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
        technologist_id,
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
            "technologist_dashboard.comment_page"
        )
    )


# ============================================================
# DELETE TECHNOLOGIST COMMENT
# ============================================================

@technologist_dashboard.route(
    "/technologist/comment/delete/<int:comment_id>",
    methods=["POST"]
)
@technologist_required
def delete_comment_page(comment_id):

    # ========================================================
    # GET LOGGED-IN TECHNOLOGIST ID
    # ========================================================

    technologist_id = session.get(
        "user_id"
    )


    # ========================================================
    # CHECK TECHNOLOGIST SESSION
    # ========================================================

    if not technologist_id:

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
        technologist_id
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
            "technologist_dashboard.comment_page"
        )
    )
