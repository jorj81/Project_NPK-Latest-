from functools import wraps

from flask import session, redirect, url_for, flash


# ============================================================
# TECHNOLOGIST REQUIRED DECORATOR
# ============================================================

def technologist_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        # ====================================================
        # CHECK IF TECHNOLOGIST IS LOGGED IN
        # ====================================================

        if "user_id" not in session:

            flash(
                "Please log in to access this page.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )


        # ====================================================
        # CHECK TECHNOLOGIST ROLE
        # ====================================================

        role = session.get(
            "role",
            ""
        ).lower()


        if role != "technologist":

            flash(
                "You do not have permission to access this page.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )


        # ====================================================
        # TECHNOLOGIST IS AUTHENTICATED AND AUTHORIZED
        # ====================================================

        return function(
            *args,
            **kwargs
        )


    return decorated_function

