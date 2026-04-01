import sqlite3
import os
from datetime import datetime

DB_PATH = os.environ.get("DB_PATH", "ipl_predictions.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        short_name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        team_id INTEGER NOT NULL,
        role TEXT DEFAULT 'Unknown',
        FOREIGN KEY (team_id) REFERENCES teams(id)
    );

    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_number INTEGER UNIQUE NOT NULL,
        match_date TEXT NOT NULL,
        match_time TEXT NOT NULL DEFAULT '19:30',
        home_team_id INTEGER NOT NULL,
        away_team_id INTEGER NOT NULL,
        venue TEXT NOT NULL,
        status TEXT DEFAULT 'upcoming',
        toss_winner_id INTEGER,
        match_winner_id INTEGER,
        top_scorer_id INTEGER,
        top_wicket_taker_id INTEGER,
        player_of_match_id INTEGER,
        FOREIGN KEY (home_team_id) REFERENCES teams(id),
        FOREIGN KEY (away_team_id) REFERENCES teams(id),
        FOREIGN KEY (toss_winner_id) REFERENCES teams(id),
        FOREIGN KEY (match_winner_id) REFERENCES teams(id),
        FOREIGN KEY (top_scorer_id) REFERENCES players(id),
        FOREIGN KEY (top_wicket_taker_id) REFERENCES players(id),
        FOREIGN KEY (player_of_match_id) REFERENCES players(id)
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        total_points INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        match_id INTEGER NOT NULL,
        toss_winner_id INTEGER,
        match_winner_id INTEGER,
        top_scorer_id INTEGER,
        top_wicket_taker_id INTEGER,
        player_of_match_id INTEGER,
        points_earned INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (match_id) REFERENCES matches(id),
        UNIQUE(user_id, match_id)
    );

    CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user_id);
    CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions(match_id);
    CREATE INDEX IF NOT EXISTS idx_users_telegram ON users(telegram_id);
    CREATE INDEX IF NOT EXISTS idx_users_points ON users(total_points DESC);
    """)

    conn.commit()
    conn.close()


# ── Team Operations ──
def get_or_create_team(name, short_name):
    conn = get_db()
    row = conn.execute("SELECT id FROM teams WHERE name=?", (name,)).fetchone()
    if row:
        conn.close()
        return row["id"]
    c = conn.execute("INSERT INTO teams (name, short_name) VALUES (?,?)", (name, short_name))
    conn.commit()
    tid = c.lastrowid
    conn.close()
    return tid


def get_all_teams():
    conn = get_db()
    rows = conn.execute("SELECT * FROM teams ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Player Operations ──
def add_player(name, team_id, role="Unknown"):
    conn = get_db()
    existing = conn.execute("SELECT id FROM players WHERE name=? AND team_id=?", (name, team_id)).fetchone()
    if existing:
        conn.close()
        return existing["id"]
    c = conn.execute("INSERT INTO players (name, team_id, role) VALUES (?,?,?)", (name, team_id, role))
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return pid


def get_players_by_team(team_id):
    conn = get_db()
    rows = conn.execute("SELECT * FROM players WHERE team_id=? ORDER BY role, name", (team_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_players_for_match(match_id):
    conn = get_db()
    match = conn.execute("SELECT home_team_id, away_team_id FROM matches WHERE id=?", (match_id,)).fetchone()
    if not match:
        conn.close()
        return []
    rows = conn.execute("""
        SELECT p.*, t.name as team_name, t.short_name as team_short
        FROM players p JOIN teams t ON p.team_id = t.id
        WHERE p.team_id IN (?, ?)
        ORDER BY t.name, p.role, p.name
    """, (match["home_team_id"], match["away_team_id"])).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Match Operations ──
def add_match(match_number, match_date, match_time, home_team_id, away_team_id, venue):
    conn = get_db()
    existing = conn.execute("SELECT id FROM matches WHERE match_number=?", (match_number,)).fetchone()
    if existing:
        conn.close()
        return existing["id"]
    c = conn.execute("""
        INSERT INTO matches (match_number, match_date, match_time, home_team_id, away_team_id, venue)
        VALUES (?,?,?,?,?,?)
    """, (match_number, match_date, match_time, home_team_id, away_team_id, venue))
    conn.commit()
    mid = c.lastrowid
    conn.close()
    return mid


def get_upcoming_matches():
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = conn.execute("""
        SELECT m.*, ht.name as home_team, ht.short_name as home_short,
               at.name as away_team, at.short_name as away_short
        FROM matches m
        JOIN teams ht ON m.home_team_id = ht.id
        JOIN teams at ON m.away_team_id = at.id
        WHERE m.status = 'upcoming'
          AND (m.match_date || ' ' || m.match_time) > ?
        ORDER BY m.match_date, m.match_time
    """, (now,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_matches():
    conn = get_db()
    rows = conn.execute("""
        SELECT m.*, ht.name as home_team, ht.short_name as home_short,
               at.name as away_team, at.short_name as away_short
        FROM matches m
        JOIN teams ht ON m.home_team_id = ht.id
        JOIN teams at ON m.away_team_id = at.id
        ORDER BY m.match_number
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_match(match_id):
    conn = get_db()
    row = conn.execute("""
        SELECT m.*, ht.name as home_team, ht.short_name as home_short,
               at.name as away_team, at.short_name as away_short
        FROM matches m
        JOIN teams ht ON m.home_team_id = ht.id
        JOIN teams at ON m.away_team_id = at.id
        WHERE m.id = ?
    """, (match_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def set_match_results(match_id, toss_winner_id, match_winner_id, top_scorer_id, top_wicket_taker_id, player_of_match_id):
    conn = get_db()
    conn.execute("""
        UPDATE matches SET
            status='completed',
            toss_winner_id=?, match_winner_id=?,
            top_scorer_id=?, top_wicket_taker_id=?,
            player_of_match_id=?
        WHERE id=?
    """, (toss_winner_id, match_winner_id, top_scorer_id, top_wicket_taker_id, player_of_match_id, match_id))
    conn.commit()

    # Calculate points for all predictions on this match
    predictions = conn.execute("SELECT * FROM predictions WHERE match_id=?", (match_id,)).fetchall()
    for pred in predictions:
        points = 0
        if pred["toss_winner_id"] and pred["toss_winner_id"] == toss_winner_id:
            points += 5
        if pred["match_winner_id"] and pred["match_winner_id"] == match_winner_id:
            points += 10
        if pred["top_scorer_id"] and pred["top_scorer_id"] == top_scorer_id:
            points += 20
        if pred["top_wicket_taker_id"] and pred["top_wicket_taker_id"] == top_wicket_taker_id:
            points += 20
        if pred["player_of_match_id"] and pred["player_of_match_id"] == player_of_match_id:
            points += 25

        conn.execute("UPDATE predictions SET points_earned=? WHERE id=?", (points, pred["id"]))
        conn.execute("""
            UPDATE users SET total_points = (
                SELECT COALESCE(SUM(points_earned), 0) FROM predictions WHERE user_id=?
            ) WHERE id=?
        """, (pred["user_id"], pred["user_id"]))

    conn.commit()
    conn.close()


# ── User Operations ──
def get_or_create_user(telegram_id, username=None, first_name=None, last_name=None):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
    if row:
        # Update info
        conn.execute("UPDATE users SET username=?, first_name=?, last_name=? WHERE telegram_id=?",
                      (username, first_name, last_name, telegram_id))
        conn.commit()
        updated = conn.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
        conn.close()
        return dict(updated)
    conn.execute("INSERT INTO users (telegram_id, username, first_name, last_name) VALUES (?,?,?,?)",
                  (telegram_id, username, first_name, last_name))
    conn.commit()
    row = conn.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
    conn.close()
    return dict(row)


# ── Prediction Operations ──
def save_prediction(user_id, match_id, toss_winner_id, match_winner_id, top_scorer_id, top_wicket_taker_id, player_of_match_id):
    conn = get_db()
    # Check if match is still open
    match = conn.execute("SELECT * FROM matches WHERE id=?", (match_id,)).fetchone()
    if not match:
        conn.close()
        return {"error": "Match not found"}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    match_start = f"{match['match_date']} {match['match_time']}"
    if now >= match_start:
        conn.close()
        return {"error": "Predictions are closed for this match"}
    if match["status"] != "upcoming":
        conn.close()
        return {"error": "Match is not open for predictions"}

    existing = conn.execute("SELECT id FROM predictions WHERE user_id=? AND match_id=?",
                             (user_id, match_id)).fetchone()
    if existing:
        conn.execute("""
            UPDATE predictions SET
                toss_winner_id=?, match_winner_id=?,
                top_scorer_id=?, top_wicket_taker_id=?,
                player_of_match_id=?
            WHERE user_id=? AND match_id=?
        """, (toss_winner_id, match_winner_id, top_scorer_id, top_wicket_taker_id,
              player_of_match_id, user_id, match_id))
    else:
        conn.execute("""
            INSERT INTO predictions (user_id, match_id, toss_winner_id, match_winner_id,
                                     top_scorer_id, top_wicket_taker_id, player_of_match_id)
            VALUES (?,?,?,?,?,?,?)
        """, (user_id, match_id, toss_winner_id, match_winner_id,
              top_scorer_id, top_wicket_taker_id, player_of_match_id))

    conn.commit()
    conn.close()
    return {"success": True}


def get_user_prediction(user_id, match_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM predictions WHERE user_id=? AND match_id=?",
                        (user_id, match_id)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_predictions(user_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT p.*, m.match_number, m.match_date,
               ht.short_name as home_short, at.short_name as away_short,
               m.status as match_status
        FROM predictions p
        JOIN matches m ON p.match_id = m.id
        JOIN teams ht ON m.home_team_id = ht.id
        JOIN teams at ON m.away_team_id = at.id
        WHERE p.user_id=?
        ORDER BY m.match_number DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Leaderboard ──
def get_leaderboard(limit=50):
    conn = get_db()
    rows = conn.execute("""
        SELECT u.telegram_id, u.username, u.first_name, u.last_name, u.total_points,
               COUNT(p.id) as predictions_made,
               (SELECT COUNT(*) FROM predictions p2
                JOIN matches m2 ON p2.match_id = m2.id
                WHERE p2.user_id = u.id AND m2.status='completed' AND p2.points_earned > 0
               ) as correct_predictions
        FROM users u
        LEFT JOIN predictions p ON u.id = p.user_id
        GROUP BY u.id
        ORDER BY u.total_points DESC, predictions_made DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_rank(telegram_id):
    conn = get_db()
    user = conn.execute("SELECT id, total_points FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
    if not user:
        conn.close()
        return None
    rank = conn.execute("""
        SELECT COUNT(*) + 1 as rank FROM users WHERE total_points > ?
    """, (user["total_points"],)).fetchone()
    total = conn.execute("SELECT COUNT(*) as total FROM users").fetchone()
    conn.close()
    return {"rank": rank["rank"], "total": total["total"], "points": user["total_points"]}


# ── Admin: Match result detail for showing who predicted what ──
def get_match_predictions_detail(match_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT p.*, u.username, u.first_name, u.telegram_id,
               tw.name as toss_team_name, mw.name as match_team_name,
               ts.name as top_scorer_name, twk.name as top_wicket_name,
               pom.name as potm_name
        FROM predictions p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN teams tw ON p.toss_winner_id = tw.id
        LEFT JOIN teams mw ON p.match_winner_id = mw.id
        LEFT JOIN players ts ON p.top_scorer_id = ts.id
        LEFT JOIN players twk ON p.top_wicket_taker_id = twk.id
        LEFT JOIN players pom ON p.player_of_match_id = pom.id
        WHERE p.match_id=?
        ORDER BY p.points_earned DESC
    """, (match_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
