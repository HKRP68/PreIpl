"""Telegram Bot for IPL 2026 Predictions."""
import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

import database as db

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://your-domain.com")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /start
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.get_or_create_user(user.id, user.username, user.first_name, user.last_name)

    text = (
        f"🏏 <b>IPL 2026 PREDICTION BOT</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Hey <b>{user.first_name}</b>! 👋\n"
        f"Predict & compete with friends!\n\n"
        f"<b>📌 Points System</b>\n"
        f"┌──────────────────────────┐\n"
        f"│ 🪙  Toss Winner        →  <b>5</b>  pts  │\n"
        f"│ 🏆  Match Winner      →  <b>10</b> pts  │\n"
        f"│ 🏏  Top Run-Scorer   →  <b>20</b> pts  │\n"
        f"│ 🎯  Top Wicket-Taker → <b>20</b> pts  │\n"
        f"│ ⭐  Player of Match   →  <b>25</b> pts  │\n"
        f"└──────────────────────────┘\n\n"
        f"<b>📋 Commands</b>\n"
        f"/predict — Open Prediction App\n"
        f"/leaderboard — Top 10 Rankings\n"
        f"/myprediction — Today's Predictions\n"
    )

    keyboard = [[InlineKeyboardButton("🏏 Open Prediction App", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /predict  →  Opens Mini App
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.get_or_create_user(user.id, user.username, user.first_name, user.last_name)

    upcoming = db.get_upcoming_matches()
    todays = db.get_todays_matches()

    if not upcoming:
        await update.message.reply_html(
            "😔 <b>No matches open for predictions right now.</b>\n"
            "Check back before the next match!"
        )
        return

    text = "🏏 <b>IPL 2026 — PREDICT NOW</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    if todays:
        text += "📅 <b>TODAY'S MATCH</b>\n\n"
        for m in todays:
            time_str = "3:30 PM" if m["match_time"] == "15:30" else "7:30 PM"
            text += (
                f"  ┌─────────────────────┐\n"
                f"  │  #{m['match_number']}  <b>{m['home_short']}</b>  🆚  <b>{m['away_short']}</b>\n"
                f"  │  ⏰ {time_str} IST\n"
                f"  │  📍 {m['venue']}\n"
                f"  └─────────────────────┘\n\n"
            )
    else:
        m = upcoming[0]
        time_str = "3:30 PM" if m["match_time"] == "15:30" else "7:30 PM"
        date_obj = datetime.strptime(m["match_date"], "%Y-%m-%d")
        date_str = date_obj.strftime("%d %b %Y")
        text += "📅 <b>NEXT MATCH</b>\n\n"
        text += (
            f"  ┌─────────────────────┐\n"
            f"  │  #{m['match_number']}  <b>{m['home_short']}</b>  🆚  <b>{m['away_short']}</b>\n"
            f"  │  📅 {date_str}\n"
            f"  │  ⏰ {time_str} IST\n"
            f"  │  📍 {m['venue']}\n"
            f"  └─────────────────────┘\n\n"
        )

    text += f"📊 <b>{len(upcoming)} matches</b> open for prediction\n"
    text += "👇 <b>Tap below to predict</b>"

    keyboard = [[InlineKeyboardButton("🏏 Open Prediction App", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /leaderboard  →  Top 10 + Your Rank
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.get_or_create_user(user.id, user.username, user.first_name, user.last_name)

    lb = db.get_leaderboard(10)
    rank_info = db.get_user_rank(user.id)

    if not lb:
        await update.message.reply_html(
            "🏆 <b>LEADERBOARD</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "No predictions yet!\n"
            "Use /predict to be the first! 🏏"
        )
        return

    text = "🏆 <b>IPL 2026 — LEADERBOARD</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    user_in_top10 = False

    for i, entry in enumerate(lb):
        rank_icon = medals.get(i, f" {i+1}.")
        name = entry["username"] or entry["first_name"] or "Anonymous"
        pts = entry["total_points"]
        preds = entry["predictions_made"]
        is_you = entry["telegram_id"] == user.id

        if is_you:
            user_in_top10 = True
            text += f"{rank_icon} <b>➤ {name} — {pts} pts</b>  ({preds}P) 👈\n"
        else:
            text += f"{rank_icon}  {name} — <b>{pts} pts</b>  ({preds}P)\n"

    # Your rank at bottom always
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━\n"

    if rank_info and rank_info["rank"] > 0:
        if user_in_top10:
            text += f"📊 <b>You're #{rank_info['rank']}</b> of {rank_info['total']} players — <b>{rank_info['points']} pts</b> 🔥"
        else:
            text += (
                f"📊 <b>Your Rank: #{rank_info['rank']}</b> of {rank_info['total']}\n"
                f"    💰 <b>{rank_info['points']} pts</b> — Keep predicting! 💪"
            )
    else:
        text += "📊 You haven't predicted yet!\n    Use /predict to join the race 🏏"

    await update.message.reply_html(text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /myprediction  →  Today's Predictions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def myprediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = db.get_or_create_user(user.id, user.username, user.first_name, user.last_name)

    todays_matches = db.get_todays_matches()

    if not todays_matches:
        await update.message.reply_html(
            "📝 <b>MY PREDICTION — TODAY</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🚫 No match scheduled today!\n\n"
            "Use /predict to see upcoming matches."
        )
        return

    text = "📝 <b>MY PREDICTION — TODAY</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━\n"

    has_open_match = False

    for match in todays_matches:
        time_str = "3:30 PM" if match["match_time"] == "15:30" else "7:30 PM"
        match_start = f"{match['match_date']} {match['match_time']}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        is_open = now < match_start and match["status"] == "upcoming"
        if is_open:
            has_open_match = True

        text += f"\n🏏 <b>#{match['match_number']}  {match['home_short']}  🆚  {match['away_short']}</b>\n"
        text += f"    ⏰ {time_str} IST  •  📍 {match['venue']}\n"
        text += "    ─────────────────────\n"

        pred = db.get_user_prediction_detail(db_user["id"], match["id"])

        if pred:
            toss = pred.get("toss_team_short") or "—"
            winner = pred.get("match_team_short") or "—"
            scorer = pred.get("top_scorer_name") or "—"
            wicket = pred.get("top_wicket_name") or "—"
            potm = pred.get("potm_name") or "—"

            text += (
                f"    🪙  Toss Winner     →  <b>{toss}</b>\n"
                f"    🏆  Match Winner   →  <b>{winner}</b>\n"
                f"    🏏  Top Scorer        →  <b>{scorer}</b>\n"
                f"    🎯  Top Wicket       →  <b>{wicket}</b>\n"
                f"    ⭐  POTM               →  <b>{potm}</b>\n"
            )

            if match["status"] == "completed":
                pts = pred.get("points_earned", 0)
                if pts > 0:
                    text += f"\n    ✅ <b>+{pts} pts earned!</b> 🎉\n"
                else:
                    text += f"\n    ❌ <b>0 pts</b> — Better luck next time!\n"
            else:
                text += f"\n    ⏳ <i>Result awaited...</i>\n"
        else:
            if is_open:
                text += "    ❌ <b>Not predicted yet!</b>\n"
                text += "    ⚡ <i>Still open — hurry!</i>\n"
            else:
                text += "    ❌ <b>Not predicted</b>\n"
                text += "    🔒 <i>Predictions closed</i>\n"

    # Add predict button if any match is still open
    keyboard = None
    if has_open_match:
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🏏 Predict Now", web_app=WebAppInfo(url=WEBAPP_URL))]]
        )

    await update.message.reply_html(text, reply_markup=keyboard)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /help
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Main
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    if not BOT_TOKEN:
        print("ERROR: Set BOT_TOKEN environment variable!")
        return

    db.init_db()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("myprediction", myprediction))
    app.add_handler(CommandHandler("help", help_cmd))

    logger.info("🏏 IPL 2026 Prediction Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
