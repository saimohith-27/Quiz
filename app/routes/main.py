from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..services.roll_number_service import parse_roll_number

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    return render_template("home.html")


@main_bp.route("/candidate", methods=["GET", "POST"])
def candidate():
    decoded_info = None
    form_data = {}

    if request.method == "POST":
        action = request.form.get("action", "decode")
        name = request.form.get("name", "").strip()
        roll_number = request.form.get("roll_number", "").strip().upper()
        section = request.form.get("section", "").strip().upper()
        form_data = {"name": name, "roll_number": roll_number, "section": section}

        if not name or not roll_number or not section:
            flash("Name, roll number, and section are required.", "danger")
            return render_template("candidate.html", decoded_info=decoded_info, form_data=form_data)

        if len(name) > 120 or len(roll_number) > 20 or len(section) > 8:
            flash("One or more fields exceed allowed length.", "danger")
            return render_template("candidate.html", decoded_info=decoded_info, form_data=form_data)

        parsed = parse_roll_number(roll_number)
        decoded_info = parsed.to_dict()
        if not parsed.valid:
            flash(parsed.error, "danger")
            return render_template("candidate.html", decoded_info=None, form_data=form_data)

        if action == "confirm":
            session["candidate"] = {
                "name": name,
                "roll_number": roll_number,
                "section": section,
                "decoded": decoded_info,
            }
            session.pop("active_attempt_id", None)
            session.pop("last_result", None)
            return redirect(url_for("exam.configure_exam"))

    return render_template("candidate.html", decoded_info=decoded_info, form_data=form_data)
