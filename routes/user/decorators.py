from functools import wraps

from flask import session, redirect, url_for, flash


def user_required(function):

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
        # Check required session information
        # ------------------------------------------------

        if "username" not in session:

            flash(
                "Invalid user session.",
                "error"
            )

            session.clear()

            return redirect(
                url_for("auth.login")
            )


        # ------------------------------------------------
        # User is authenticated
        # ------------------------------------------------

        return function(*args, **kwargs)


    return decorated_function