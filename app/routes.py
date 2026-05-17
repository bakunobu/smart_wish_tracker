from flask import Blueprint, render_template, request, redirect, url_for
from . import db
from .models import TimeEntry
from datetime import datetime

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    entries = TimeEntry.query.order_by(TimeEntry.start_time.desc()).all()
    return render_template("index.html", entries=entries)


@bp.route("/start", methods=["POST"])
def start_timer():
    description = request.form["description"]
    project = request.form.get("project", "")

    new_entry = TimeEntry(
        description=description, project=project, start_time=datetime.utcnow()
    )

    db.session.add(new_entry)
    db.session.commit()
    return redirect(url_for("main.index"))


@bp.route("/stop/<int:entry_id>")
def stop_timer(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    entry.end_time = datetime.utcnow()
    db.session.commit()
    return redirect(url_for("main.index"))


@bp.app_template_filter("duration")
def format_duration(delta):
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"
