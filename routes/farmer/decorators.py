from functools import wraps

from flask import session, redirect, url_for, flash


def farmer_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        # ------------------------------------------------
        # Check if user is logged in
        # ------------------------------------------------

        if "user_id" not in session:

            flash(
                "Please log in to access this page.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )


        # ------------------------------------------------
        # Check user role
        # ------------------------------------------------

        role = session.get("role", "").lower()

        if role != "farmer":

            flash(
                "You do not have permission to access this page.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )


        # ------------------------------------------------
        # Farmer is authenticated and authorized
        # ------------------------------------------------

        return function(*args, **kwargs)


    return decorated_function