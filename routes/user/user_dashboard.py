from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from routes.user.decorators import user_required

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
# USER DASHBOARD BLUEPRINT
# ============================================================

user_dashboard = Blueprint(
    "user_dashboard",
    __name__
)


# ============================================================
# USER DASHBOARD
# ============================================================

@user_dashboard.route("/user/dashboard")
@user_required
def dashboard_page():

    return render_template(
        "user/dashboard.html"
    )


# ============================================================
# CURRENT ESP32 SOIL DATA
# ============================================================

@user_dashboard.route("/user/soil-data")
@user_required
def soil_data_page():

    # --------------------------------------------------------
    # GET CURRENT ESP32 SOIL READINGS
    # --------------------------------------------------------

    success, result = get_all_current_readings()


    # --------------------------------------------------------
    # DATABASE ERROR
    # --------------------------------------------------------

    if not success:

        return render_template(
            "user/current_soil_data.html",
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
    # DISPLAY CURRENT SOIL DATA
    # --------------------------------------------------------

    return render_template(
        "user/current_soil_data.html",
        devices=result,
        error=None
    )

# ============================================================
# ALL ESP32 SOIL HISTORY
# ============================================================

@user_dashboard.route("/user/soil-history")
@user_required
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
            "user/soil_history_data.html",

            devices=[],

            error=result,

            current_filter=current_filter
        )


    # ========================================================
    # DISPLAY SENSOR HISTORY
    # ========================================================

    return render_template(
        "user/soil_history_data.html",

        devices=result,

        error=None,

        current_filter=current_filter
    )


# ============================================================
# USER ESP32 DEVICES
# ============================================================

@user_dashboard.route("/user-devices")
@user_required
def user_devices_page():

    success, devices = get_all_esp32_devices()

    if not success:

        flash(
            devices,
            "error"
        )

        return render_template(
            "user/user_devices.html",
            devices=[]
        )

    return render_template(
        "user/user_devices.html",
        devices=devices
    )


# ============================================================
# USER COMMENTS
# ============================================================

@user_dashboard.route("/user/comment", methods=["GET", "POST"])
@user_required
def comment_page():

    # ========================================================
    # GET LOGGED-IN USER INFORMATION
    # ========================================================

    user_id = session.get("user_id")

    username = session.get("username")


    # ========================================================
    # CHECK USER SESSION
    # ========================================================

    if not user_id or not username:

        return redirect(
            url_for("login.login_page")
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
            user_id,
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
        # REDIRECT BACK TO COMMENT PAGE
        # ====================================================

        return redirect(
            url_for(
                "user_dashboard.comment_page"
            )
        )


    # ========================================================
    # GET USER'S EXISTING COMMENTS
    # ========================================================

    success, comments = get_user_comments(
        user_id
    )


    # ========================================================
    # DATABASE ERROR
    # ========================================================

    if not success:

        return render_template(
            "user/comments.html",
            comments=[],
            error=comments
        )


    # ========================================================
    # DISPLAY COMMENTS
    # ========================================================

    return render_template(
        "user/comments.html",
        comments=comments,
        error=None
    )


# ============================================================
# EDIT USER COMMENT
# ============================================================

@user_dashboard.route(
    "/user/comment/edit/<int:comment_id>",
    methods=["POST"]
)
@user_required
def edit_comment_page(comment_id):

    # ========================================================
    # GET LOGGED-IN USER ID
    # ========================================================

    user_id = session.get(
        "user_id"
    )


    # ========================================================
    # CHECK USER SESSION
    # ========================================================

    if not user_id:

        return redirect(
            url_for("login.login_page")
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
        user_id,
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
            "user_dashboard.comment_page"
        )
    )


# ============================================================
# DELETE USER COMMENT
# ============================================================

@user_dashboard.route(
    "/user/comment/delete/<int:comment_id>",
    methods=["POST"]
)
@user_required
def delete_comment_page(comment_id):

    # ========================================================
    # GET LOGGED-IN USER ID
    # ========================================================

    user_id = session.get(
        "user_id"
    )


    # ========================================================
    # CHECK USER SESSION
    # ========================================================

    if not user_id:

        return redirect(
            url_for("login.login_page")
        )


    # ========================================================
    # DELETE COMMENT
    # ========================================================

    success, message = delete_comment(
        comment_id,
        user_id
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
            "user_dashboard.comment_page"
        )
    )



