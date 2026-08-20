from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
)

import bcrypt

from users_database import (
    connect_database,
    create_user,
    update_user_last_seen,
    clear_user_last_seen
)


auth = Blueprint("auth", __name__)


# ============================================================
# LOGIN
# ============================================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    # --------------------------------------------------------
    # If already logged in, redirect based on role
    # --------------------------------------------------------

    if request.method == "GET":

        if "user_id" in session and "role" in session:

            role = session["role"].lower()

            if role == "admin":
                return redirect(
                    url_for("admin_dashboard.dashboard_page")
                )

            elif role == "farmer":
                return redirect(
                    url_for("farmer_dashboard.dashboard_page")
                )

            elif role == "user":
                return redirect(
                    url_for("user_dashboard.dashboard_page")
                )

            elif role == "technologist":
                return redirect(
                    url_for("technologist_dashboard.dashboard_page")
                )

            else:
                session.clear()

                flash(
                    "Invalid user role.",
                    "error"
                )

                return redirect(
                    url_for("auth.login")
                )

        return render_template(
            "auth/login.html"
        )


    # --------------------------------------------------------
    # Get login form data
    # --------------------------------------------------------

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    ).strip()


    if not username or not password:

        flash(
            "Username and password are required.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    connection = None
    cursor = None


    try:

        connection = connect_database()

        if connection is None:

            flash(
                "Database connection failed.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )


        cursor = connection.cursor(
            dictionary=True
        )


        # ----------------------------------------------------
        # Find user
        # ----------------------------------------------------

        query = """
            SELECT
                users.id,
                users.username,
                users.password_hash,
                users.user_role_id,
                user_roles.role_name
            FROM users
            INNER JOIN user_roles
                ON users.user_role_id = user_roles.id
            WHERE users.username = %s
        """


        cursor.execute(
            query,
            (username,)
        )


        user = cursor.fetchone()


        # ----------------------------------------------------
        # User does not exist
        # ----------------------------------------------------

        if user is None:

            flash(
                "User not found.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )


        # ----------------------------------------------------
        # Check password
        # ----------------------------------------------------

        stored_hash = user["password_hash"]


        if isinstance(
            stored_hash,
            str
        ):

            stored_hash = stored_hash.encode(
                "utf-8"
            )


        input_password = password.encode(
            "utf-8"
        )


        if bcrypt.checkpw(
            input_password,
            stored_hash
        ):

            # ------------------------------------------------
            # Save user information in session
            # ------------------------------------------------

            session["user_id"] = user["id"]

            session["username"] = user["username"]


            # ------------------------------------------------
            # Save role information
            # ------------------------------------------------

            session["user_role_id"] = user["user_role_id"]

            session["role"] = user["role_name"]


            # ------------------------------------------------
            # Mark user as active immediately
            # ------------------------------------------------

            success, message = update_user_last_seen(
                user["id"]
            )


            if not success:

                print(
                    f"Login activity update error: {message}"
                )


            flash(
                "Login successful.",
                "success"
            )


            # ------------------------------------------------
            # Redirect user based on role
            # ------------------------------------------------

            role = user["role_name"].lower()


            # ADMIN
            if role == "admin":

                return redirect(
                    url_for(
                        "admin_dashboard.dashboard_page"
                    )
                )


            # FARMER
            elif role == "farmer":

                return redirect(
                    url_for(
                        "farmer_dashboard.dashboard_page"
                    )
                )


            # USER
            elif role == "user":

                return redirect(
                    url_for(
                        "user_dashboard.dashboard_page"
                    )
                )


            # TECHNOLOGIST
            elif role == "technologist":

                return redirect(
                    url_for(
                        "technologist_dashboard.dashboard_page"
                    )
                )


            # UNKNOWN ROLE
            else:

                session.clear()

                flash(
                    "Your account has an invalid user role.",
                    "error"
                )

                return redirect(
                    url_for("auth.login")
                )


        # ----------------------------------------------------
        # Incorrect password
        # ----------------------------------------------------

        flash(
            "Invalid username or password.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    except Exception as e:

        flash(
            f"Login error: {e}",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    finally:

        if cursor is not None:
            cursor.close()

        if (
            connection is not None
            and connection.is_connected()
        ):
            connection.close()


# ============================================================
# ADD USER FORM
# ============================================================

# ============================================================
# ADD USER FORM
# ============================================================

@auth.route("/add-user")
def add_user_form():

    # --------------------------------------------------------
    # If already logged in, redirect based on role
    # --------------------------------------------------------

    if "user_id" in session and "role" in session:

        role = session["role"].lower()


        if role == "admin":

            return redirect(
                url_for(
                    "admin_dashboard.dashboard_page"
                )
            )


        elif role == "farmer":

            return redirect(
                url_for(
                    "farmer_dashboard.dashboard_page"
                )
            )


        elif role == "user":

            return redirect(
                url_for(
                    "user_dashboard.dashboard_page"
                )
            )


        elif role == "technologist":

            return redirect(
                url_for(
                    "technologist_dashboard.dashboard_page"
                )
            )


        else:

            session.clear()

            flash(
                "Invalid user role.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )


    connection = None
    cursor = None


    try:

        connection = connect_database()


        if connection is None:

            flash(
                "Database connection failed.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )


        cursor = connection.cursor(
            dictionary=True
        )


        query = """
            SELECT id, role_name
            FROM user_roles
            ORDER BY id
        """


        cursor.execute(query)


        roles = cursor.fetchall()


        return render_template(
            "auth/add_user.html",
            roles=roles
        )


    except Exception as e:

        flash(
            f"Error loading user roles: {e}",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    finally:

        if cursor is not None:

            cursor.close()


        if (
            connection is not None
            and connection.is_connected()
        ):

            connection.close()


# ============================================================
# CREATE USER
# ============================================================

@auth.route(
    "/create-user",
    methods=["POST"]
)
def create_user_route():

    username = request.form.get(
        "username",
        ""
    ).strip()


    password = request.form.get(
        "password",
        ""
    ).strip()


    contact_number = request.form.get(
        "contact_number",
        ""
    ).strip()


    barangay_id = request.form.get(
        "barangay_id",
        ""
    ).strip()


    user_role_id = request.form.get(
        "user_role_id",
        ""
    ).strip()


    # Since barangay_id is removed from the form, give it a default valid ID to satisfy the database
    if not barangay_id:
        barangay_id = "13"

    if (
        not username
        or not password
        or not contact_number
        or not user_role_id
    ):

        flash(
            "All fields are required.",
            "error"
        )

        return redirect(
            url_for("auth.add_user_form")
        )


    success, message = create_user(
        username,
        password,
        contact_number,
        barangay_id,
        user_role_id
    )


    if success:

        flash(
            message,
            "success"
        )

        return redirect(
            url_for("auth.login")
        )


    flash(
        message,
        "error"
    )

    return redirect(
        url_for("auth.add_user_form")
    )


# ============================================================
# GET REGIONS
# ============================================================

@auth.route("/regions")
def get_regions():

    connection = None
    cursor = None


    try:

        connection = connect_database()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute("""
            SELECT id, region_name
            FROM regions
            ORDER BY region_name
        """)


        regions = cursor.fetchall()


        return jsonify(regions)


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


    finally:

        if cursor is not None:
            cursor.close()

        if (
            connection is not None
            and connection.is_connected()
        ):
            connection.close()


# ============================================================
# GET PROVINCES
# ============================================================

@auth.route(
    "/provinces/<int:region_id>"
)
def get_provinces(region_id):

    connection = None
    cursor = None


    try:

        connection = connect_database()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute("""
            SELECT id, province_name
            FROM provinces
            WHERE region_id = %s
            ORDER BY province_name
        """, (region_id,))


        provinces = cursor.fetchall()


        return jsonify(provinces)


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


    finally:

        if cursor is not None:
            cursor.close()

        if (
            connection is not None
            and connection.is_connected()
        ):
            connection.close()


# ============================================================
# GET CITIES / MUNICIPALITIES
# ============================================================

@auth.route(
    "/cities/<int:province_id>"
)
def get_cities(province_id):

    connection = None
    cursor = None


    try:

        connection = connect_database()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute("""
            SELECT id, city_name, type
            FROM cities_municipalities
            WHERE province_id = %s
            ORDER BY city_name
        """, (province_id,))


        cities = cursor.fetchall()


        return jsonify(cities)


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


    finally:

        if cursor is not None:
            cursor.close()

        if (
            connection is not None
            and connection.is_connected()
        ):
            connection.close()


# ============================================================
# GET BARANGAYS
# ============================================================

@auth.route(
    "/barangays/<int:city_id>"
)
def get_barangays(city_id):

    connection = None
    cursor = None


    try:

        connection = connect_database()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute("""
            SELECT id, barangay_name
            FROM barangays
            WHERE city_id = %s
            ORDER BY barangay_name
        """, (city_id,))


        barangays = cursor.fetchall()


        return jsonify(barangays)


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


    finally:

        if cursor is not None:
            cursor.close()

        if (
            connection is not None
            and connection.is_connected()
        ):
            connection.close()


# ============================================================
# HEARTBEAT
# ============================================================

@auth.route(
    "/heartbeat",
    methods=["POST"]
)
def heartbeat():

    # --------------------------------------------------------
    # Get logged-in user from session
    # --------------------------------------------------------

    user_id = session.get(
        "user_id"
    )


    # --------------------------------------------------------
    # User is not logged in
    # --------------------------------------------------------

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User is not logged in"
        }), 401


    # --------------------------------------------------------
    # Update last_seen
    # --------------------------------------------------------

    success, message = update_user_last_seen(
        user_id
    )


    if not success:

        return jsonify({
            "success": False,
            "message": message
        }), 500


    # --------------------------------------------------------
    # Heartbeat successful
    # --------------------------------------------------------

    return jsonify({
        "success": True
    })


# ============================================================
# LOGOUT
# ============================================================

@auth.route("/logout")
def logout():

    # --------------------------------------------------------
    # Get user ID before clearing session
    # --------------------------------------------------------

    user_id = session.get(
        "user_id"
    )


    # --------------------------------------------------------
    # Clear user's last_seen
    # --------------------------------------------------------

    if user_id:

        success, message = clear_user_last_seen(
            user_id
        )


        if not success:

            print(
                f"Logout activity error: {message}"
            )


    # --------------------------------------------------------
    # Clear Flask session
    # --------------------------------------------------------

    session.clear()


    # --------------------------------------------------------
    # Redirect to login
    # --------------------------------------------------------

    flash(
        "You have been logged out.",
        "success"
    )


    return redirect(
        url_for("auth.login")
    )