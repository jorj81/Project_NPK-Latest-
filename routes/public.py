from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import os
import socket
from contextlib import closing


public = Blueprint("public", __name__)


# ============================================================
# GET LOCAL IP ADDRESS
# ============================================================

def get_local_ip():
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
            s.connect(("8.8.8.8", 80))

            local_ip = s.getsockname()[0]

            if local_ip and local_ip != "0.0.0.0":
                return local_ip

    except Exception:
        pass

    return "127.0.0.1"


# ============================================================
# REDIRECT LOGGED-IN USER TO DASHBOARD
# ============================================================

def redirect_logged_in_user():

    if "user_id" in session and "role" in session:

        role = session["role"].lower()

        # ----------------------------------------------------
        # ADMIN
        # ----------------------------------------------------

        if role == "admin":
            return redirect(
                url_for("admin_dashboard.dashboard_page")
            )

        # ----------------------------------------------------
        # FARMER
        # ----------------------------------------------------

        elif role == "farmer":
            return redirect(
                url_for("farmer_dashboard.dashboard_page")
            )

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

        elif role == "user":
            return redirect(
                url_for("user_dashboard.dashboard_page")
            )

        # ----------------------------------------------------
        # TECHNOLOGIST
        # ----------------------------------------------------

        elif role == "technologist":
            return redirect(
                url_for("technologist_dashboard.dashboard_page")
            )

        # ----------------------------------------------------
        # INVALID ROLE
        # ----------------------------------------------------

        else:
            session.clear()

            flash(
                "Invalid user role.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

    return None


# ============================================================
# PUBLIC INDEX
# ============================================================

@public.route("/")
def index():

    # Check if already logged in
    dashboard_redirect = redirect_logged_in_user()

    if dashboard_redirect:
        return dashboard_redirect

    # --------------------------------------------------------
    # LOAD TERMS AND CONDITIONS
    # --------------------------------------------------------

    terms_path = os.path.join(
        os.path.dirname(__file__),
        "terms.txt"
    )

    try:
        with open(
            terms_path,
            "r",
            encoding="utf-8"
        ) as file:

            terms_text = file.read()

    except FileNotFoundError:

        terms_text = "Terms file not found."

    return render_template(
        "public/index.html",
        terms_text=terms_text
    )


# ============================================================
# ACCEPT TERMS
# ============================================================

@public.route("/accept-terms", methods=["POST"])
def accept_terms():

    if request.form.get("agree"):

        return redirect(
            url_for("public.home")
        )

    flash(
        "You must accept the Terms and Conditions.",
        "error"
    )

    return redirect(
        url_for("public.index")
    )


# ============================================================
# PUBLIC HOME
# ============================================================

@public.route("/home")
def home():

    # --------------------------------------------------------
    # CHECK IF USER IS ALREADY LOGGED IN
    # --------------------------------------------------------

    dashboard_redirect = redirect_logged_in_user()

    if dashboard_redirect:
        return dashboard_redirect

    # --------------------------------------------------------
    # GET SERVER INFORMATION
    # --------------------------------------------------------

    local_ip = get_local_ip()

    port = (
        request.host.split(":")[-1]
        if ":" in request.host
        else "5000"
    )

    server_url = f"http://{local_ip}:{port}"

    return render_template(
        "public/home.html",
        local_ip=local_ip,
        server_url=server_url
    )