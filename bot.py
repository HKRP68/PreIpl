"""Telegram Bot for IPL 2026 Predictions."""
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

import database as db

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://your-domain.com")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    welcome = (
        f"🏏 <b>Welcome to IPL 2026 Prediction Bot!</b>\n\n"
        f"Hey {user.first_name}! Ready to test your cricket knowledge?\n\n"
        f"<b>How to earn points:</b>\n"
        f"🪙 Toss Winner — 5 pts\n"
        f"🏆 Match Winner — 10 pts\n"
        f"🏏 Top Run-Scorer — 20 pts\n"
        f"🎯 Top Wicket-Taker — 20 pts\n"
        f"⭐ Player of the Match — 25 pts\n\n"
        f"<b>Commands:</b>\n"
        f"/predict — Make predictions\n"
        f"/leaderboard — View rankings\n"
        f"/myrank — Your current rank\n"
        f"/mypredictions — Your predictions\n"
        f"/schedule — Match schedule\n"
        f"/help — Show this message"
    )

    keyboard = [[InlineKeyboardButton("🏏 Open Prediction App", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_html(welcome, reply_markup=InlineKeyboardMarkup(keyboard))


async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    upcoming = db.get_upcoming_matches()
    if not upcoming:
        await update.message.reply_text("No upcoming matches available for prediction right now!")
        return

    keyboard = [[InlineKeyboardButton(
        f"🏏 Predict Now — {len(upcoming)} matches open",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )]]
    text = f"🏏 <b>{len(upcoming)} matches open for predictions!</b>\n\n"
    for m in upcoming[:5]:
        text += f"#{m['match_number']} {m['home_short']} vs {m['away_short']} — {m['match_date']}\n"
    if len(upcoming) > 5:
        text += f"\n...and {len(upcoming) - 5} more!\n"
    text += "\nTap below to make your predictions:"

    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lb = db.get_leaderboard(20)
    if not lb:
        await update.message.reply_text("No predictions yet! Be the first to predict.")
        return

    user = update.effective_user
    rank_info = db.get_user_rank(user.id)

    text = "🏆 <b>IPL 2026 Prediction Leaderboard</b>\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, entry in enumerate(lb):
        medal = medals[i] if i < 3 else f"{i+1}."
        name = entry["username"] or entry["first_name"] or "Anonymous"
        is_you = " ← You" if entry["telegram_id"] == user.id else ""
        text += f"{medal} <b>{name}</b> — {entry['total_points']} pts ({entry['predictions_made']} predictions){is_you}\n"

    if rank_info:
        text += f"\n📊 <b>Your rank: #{rank_info['rank']}</b> of {rank_info['total']} players ({rank_info['points']} pts)"

    keyboard = [[InlineKeyboardButton("📊 Full Leaderboard", web_app=WebAppInfo(url=f"{WEBAPP_URL}#leaderboard"))]]
    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def myrank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.get_or_create_user(user.id, user.username, user.first_name, user.last_name)
    rank_info = db.get_user_rank(user.id)

    if not rank_info or rank_info["rank"] == 0:
        await update.message.reply_text("You haven't made any predictions yet! Use /predict to start.")
        return

    text = (
        f"📊 <b>Your IPL 2026 Stats</b>\n\n"
        f"🏅 Rank: <b>#{rank_info['rank']}</b> of {rank_info['total']}\n"
        f"💰 Total Points: <b>{rank_info['points']}</b>\n"
    )
    await update.message.reply_html(text)


async def mypredictions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = db.get_or_create_user(user.id, user.username, user.first_name, user.last_name)
    preds = db.get_user_predictions(db_user["id"])

    if not preds:
        await update.message.reply_text("You haven't made any predictions yet! Use /predict to start.")
        return

    text = f"📝 <b>Your Predictions</b>\n\n"
    for p in preds[:10]:
        status = "✅" if p["match_status"] == "completed" else "⏳"
        pts = f" (+{p['points_earned']} pts)" if p["match_status"] == "completed" and p["points_earned"] > 0 else ""
        text += f"{status} #{p['match_number']} {p['home_short']} vs {p['away_short']}{pts}\n"

    if len(preds) > 10:
        text += f"\n...and {len(preds) - 10} more predictions"

    keyboard = [[InlineKeyboardButton("📝 View All", web_app=WebAppInfo(url=f"{WEBAPP_URL}#predictions"))]]
    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    upcoming = db.get_upcoming_matches()
    if not upcoming:
        await update.message.reply_text("No upcoming matches scheduled!")
        return

    text = "📅 <b>Upcoming IPL 2026 Matches</b>\n\n"
    for m in upcoming[:10]:
        text += f"#{m['match_number']} <b>{m['home_short']} vs {m['away_short']}</b>\n"
        text += f"   📅 {m['match_date']} ⏰ {m['match_time']} IST\n"
        text += f"   📍 {m['venue']}\n\n"

    if len(upcoming) > 10:
        text += f"...and {len(upcoming) - 10} more matches"

    await update.message.reply_html(text)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


def main():
    if not BOT_TOKEN:
        print("ERROR: Set BOT_TOKEN environment variable!")
        return

    db.init_db()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("myrank", myrank))
    app.add_handler(CommandHandler("mypredictions", mypredictions))
    app.add_handler(CommandHandler("schedule", schedule))
    app.add_handler(CommandHandler("help", help_cmd))

    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
