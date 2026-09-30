# routes/login.py
# Login e logout.
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from auth import get_user

bp = Blueprint("login", __name__)

@bp.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        user = get_user(request.form.get("email", "").strip())
        if user and user.check_password(request.form.get("password", "")):
            login_user(user, remember="remember" in request.form)
            next_page = request.args.get("next")
            # accetta solo percorsi interni, per evitare redirect verso altri siti
            if not next_page or not next_page.startswith("/") or next_page.startswith("//"):
                next_page = url_for("dashboard.dashboard")
            return redirect(next_page)
        return render_template("index.html", error="Credenziali errate")
    return render_template("index.html")


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Logout effettuato")
    return redirect(url_for("login.index"))
