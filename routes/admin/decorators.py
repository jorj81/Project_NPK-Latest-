from functools import wraps

from flask import session, redirect, url_for, flash


def admin_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        # Check if user is logged in
        if "user_id" not in session:

            flash("Please login first.", "error")

            return redirect(
                url_for("auth.login")
            )

        # Check if user is an administrator
        if session.get("role") != "admin":

            flash("Access denied. Administrator privileges required.", "error")

            return redirect(
                url_for("auth.logout")
            )

        return view_function(*args, **kwargs)

    return wrapped_view

