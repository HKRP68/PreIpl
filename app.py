"""Flask API server for IPL Prediction Bot Mini App."""
import os
import json
import hmac
import hashlib
from urllib.parse import unquote, parse_qs
from functools import wraps
from datetime import datetime

from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, session

import database as db

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me-in-production")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


# ── Telegram WebApp Auth Validation ──
def validate_telegram_data(init_data_raw):
    """Validate Telegram Mini App initData."""
    if not BOT_TOKEN:
        return None  # Skip validation in dev
    try:
        parsed = parse_qs(unquote(init_data_raw))
        check_hash = parsed.get("hash", [None])[0]
        if not check_hash:
            return None

        data_pairs = []
        for key, val in sorted(parsed.items()):
            if key != "hash":
                data_pairs.append(f"{key}={val[0]}")
        data_check_string = "\n".join(data_pairs)

        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if computed == check_hash:
            user_json = parsed.get("user", [None])[0]
            if user_json:
                return json.loads(user_json)
        return None
    except Exception:
        return None


def get_user_from_request():
    """Extract Telegram user from request headers or params."""
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    if init_data:
        user_data = validate_telegram_data(init_data)
        if user_data:
            return db.get_or_create_user(
                telegram_id=user_data["id"],
                username=user_data.get("username"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
            )

    # Dev mode: allow telegram_id param
    tid = request.args.get("telegram_id") or request.json.get("telegram_id") if request.is_json else request.args.get("telegram_id")
    if tid:
        return db.get_or_create_user(
            telegram_id=int(tid),
            username=request.args.get("username", "dev_user"),
            first_name=request.args.get("first_name", "Dev"),
        )
    return None


# ── Admin Auth ──
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect("/admin/login")
        return f(*args, **kwargs)
    return decorated


# ────────────────────────────────────────
#  MINI APP FRONTEND
# ────────────────────────────────────────

@app.route("/")
def index():
    return render_template("miniapp.html")


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


# ────────────────────────────────────────
#  API ENDPOINTS
# ────────────────────────────────────────

@app.route("/api/matches/upcoming")
def api_upcoming_matches():
    matches = db.get_upcoming_matches()
    return jsonify(matches)


@app.route("/api/matches/all")
def api_all_matches():
    matches = db.get_all_matches()
    return jsonify(matches)


@app.route("/api/match/<int:match_id>")
def api_match(match_id):
    match = db.get_match(match_id)
    if not match:
        return jsonify({"error": "Not found"}), 404
    return jsonify(match)


@app.route("/api/match/<int:match_id>/players")
def api_match_players(match_id):
    players = db.get_players_for_match(match_id)
    return jsonify(players)


@app.route("/api/teams")
def api_teams():
    teams = db.get_all_teams()
    return jsonify(teams)


@app.route("/api/predict", methods=["POST"])
def api_predict():
    user = get_user_from_request()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    result = db.save_prediction(
        user_id=user["id"],
        match_id=data["match_id"],
        toss_winner_id=data.get("toss_winner_id"),
        match_winner_id=data.get("match_winner_id"),
        top_scorer_id=data.get("top_scorer_id"),
        top_wicket_taker_id=data.get("top_wicket_taker_id"),
        player_of_match_id=data.get("player_of_match_id"),
    )
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/api/my-predictions")
def api_my_predictions():
    user = get_user_from_request()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    preds = db.get_user_predictions(user["id"])
    return jsonify(preds)


@app.route("/api/my-prediction/<int:match_id>")
def api_my_prediction(match_id):
    user = get_user_from_request()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    pred = db.get_user_prediction(user["id"], match_id)
    return jsonify(pred or {})


@app.route("/api/leaderboard")
def api_leaderboard():
    lb = db.get_leaderboard()
    return jsonify(lb)


@app.route("/api/my-rank")
def api_my_rank():
    user = get_user_from_request()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    rank = db.get_user_rank(user["telegram_id"])
    return jsonify(rank or {"rank": 0, "total": 0, "points": 0})


@app.route("/api/user/register", methods=["POST"])
def api_register():
    data = request.json
    user = db.get_or_create_user(
        telegram_id=data["telegram_id"],
        username=data.get("username"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
    )
    return jsonify(user)


# ────────────────────────────────────────
#  ADMIN PANEL
# ────────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        return render_template("admin_login.html", error="Wrong password")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin/login")


@app.route("/admin")
@admin_required
def admin_dashboard():
    matches = db.get_all_matches()
    teams = db.get_all_teams()
    return render_template("admin.html", matches=matches, teams=teams)


@app.route("/admin/match/<int:match_id>")
@admin_required
def admin_match(match_id):
    match = db.get_match(match_id)
    players = db.get_players_for_match(match_id)
    teams = db.get_all_teams()
    predictions = db.get_match_predictions_detail(match_id)
    return render_template("admin_match.html", match=match, players=players, teams=teams, predictions=predictions)


@app.route("/admin/match/<int:match_id>/results", methods=["POST"])
@admin_required
def admin_set_results(match_id):
    data = request.form
    db.set_match_results(
        match_id=match_id,
        toss_winner_id=int(data["toss_winner_id"]) if data.get("toss_winner_id") else None,
        match_winner_id=int(data["match_winner_id"]) if data.get("match_winner_id") else None,
        top_scorer_id=int(data["top_scorer_id"]) if data.get("top_scorer_id") else None,
        top_wicket_taker_id=int(data["top_wicket_taker_id"]) if data.get("top_wicket_taker_id") else None,
        player_of_match_id=int(data["player_of_match_id"]) if data.get("player_of_match_id") else None,
    )
    return redirect(f"/admin/match/{match_id}")


@app.route("/admin/add-match", methods=["POST"])
@admin_required
def admin_add_match():
    data = request.form
    db.add_match(
        match_number=int(data["match_number"]),
        match_date=data["match_date"],
        match_time=data.get("match_time", "19:30"),
        home_team_id=int(data["home_team_id"]),
        away_team_id=int(data["away_team_id"]),
        venue=data["venue"],
    )
    return redirect("/admin")


@app.route("/admin/add-player", methods=["POST"])
@admin_required
def admin_add_player():
    data = request.form
    db.add_player(
        name=data["name"],
        team_id=int(data["team_id"]),
        role=data.get("role", "Unknown"),
    )
    return redirect("/admin")


@app.route("/admin/team/<int:team_id>/players")
@admin_required
def admin_team_players(team_id):
    players = db.get_players_by_team(team_id)
    teams = db.get_all_teams()
    team = next((t for t in teams if t["id"] == team_id), None)
    return render_template("admin_players.html", players=players, team=team, teams=teams)


if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
