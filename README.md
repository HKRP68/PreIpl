# 🏏 IPL 2026 Prediction Bot — Telegram Mini App

A full-featured Telegram Mini App + Bot for IPL 2026 cricket match predictions with leaderboard, admin panel, and point scoring.

## Features

**For Users:**
- `/predict` — Open Mini App to make predictions
- `/leaderboard` — View top rankers
- `/myrank` — Check your current ranking
- `/mypredictions` — View your prediction history
- `/schedule` — Upcoming match schedule
- Predict: Toss Winner, Match Winner, Top Scorer, Top Wicket-Taker, Player of Match
- Predictions auto-close at match start time (IST)
- Only players from the two playing teams shown

**For Admin (you):**
- Web dashboard at `/admin`
- Set match results → auto-calculates points for all users
- Add new matches and players
- View who predicted what for each match
- Manage all 10 teams and their squads

## Points System

| Prediction | Points |
|---|---|
| Toss Winner | 5 |
| Match Winner | 10 |
| Top Run-Scorer | 20 |
| Top Wicket-Taker | 20 |
| Player of the Match | 25 |
| **Max per match** | **80** |

## Setup Guide (Step by Step)

### 1. Create Telegram Bot

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Choose a name: `IPL 2026 Predictor`
4. Choose a username: `ipl2026predict_bot` (must end with `bot`)
5. **Copy the bot token** — you'll need it

### 2. Get a Server (Free Options)

**Option A: Railway.app (Recommended, easiest)**
1. Go to [railway.app](https://railway.app) and sign up
2. Create new project → Deploy from GitHub
3. Upload this code to a GitHub repo first

**Option B: Render.com (Free tier)**
1. Go to [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repo

**Option C: Your own VPS (DigitalOcean, AWS, etc.)**

### 3. Deploy the App

```bash
# Clone/upload the project to your server
cd ipl-prediction-bot

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export BOT_TOKEN="your-bot-token-from-botfather"
export WEBAPP_URL="https://your-domain.com"     # Your server's public URL
export ADMIN_PASSWORD="your-secret-password"     # For admin panel
export FLASK_SECRET="random-secret-string"       # Any random string

# Seed the database (run once)
python seed_data.py

# Start the web server
gunicorn app:app --bind 0.0.0.0:5000

# In another terminal, start the bot
python bot.py
```

### 4. Configure Telegram Mini App

1. Go to **@BotFather** on Telegram
2. Send `/mybots` → Select your bot
3. Go to **Bot Settings** → **Menu Button**
4. Set the URL to: `https://your-domain.com`
5. Set the text to: `🏏 Predict`

Also configure the web app:
1. Send `/setmenubutton` to BotFather
2. Or send `/newapp` to configure a Mini App

### 5. Set Up HTTPS (Required for Telegram)

Telegram Mini Apps **require HTTPS**. Options:
- Railway/Render provide HTTPS automatically
- For VPS: Use **Cloudflare** (free) or **Let's Encrypt** with nginx

### Procfile (for Railway/Render)

Create a `Procfile`:
```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

Create a separate worker or use the start command for the bot:
```
worker: python bot.py
```

### Environment Variables Summary

| Variable | Description | Example |
|---|---|---|
| `BOT_TOKEN` | Telegram bot token from BotFather | `7123456789:AAF...` |
| `WEBAPP_URL` | Your server's public HTTPS URL | `https://ipl-predict.railway.app` |
| `ADMIN_PASSWORD` | Password for admin panel | `mysecretpass` |
| `FLASK_SECRET` | Flask session secret key | `any-random-string` |
| `DB_PATH` | SQLite database path (optional) | `ipl_predictions.db` |

## File Structure

```
ipl-prediction-bot/
├── app.py              # Flask web server + API
├── bot.py              # Telegram bot
├── database.py         # SQLite database operations
├── seed_data.py        # Seed IPL 2026 data (run once)
├── requirements.txt    # Python dependencies
├── templates/
│   ├── miniapp.html         # Telegram Mini App UI
│   ├── admin.html           # Admin dashboard
│   ├── admin_login.html     # Admin login
│   ├── admin_match.html     # Match result management
│   └── admin_players.html   # Team player management
└── README.md
```

## How It Works

1. User opens bot → sends `/predict`
2. Bot shows upcoming matches with "Open Prediction App" button
3. User taps button → Mini App opens inside Telegram
4. User selects a match → makes 5 predictions
5. Predictions are saved; locked when match starts
6. **You (admin)** go to `/admin` after match ends
7. Enter actual results → system auto-calculates points
8. Leaderboard updates for all users

## Admin Panel

Access at: `https://your-domain.com/admin`

- **Dashboard**: View all matches, add new ones
- **Match Detail**: Set results, view all user predictions
- **Team Players**: View/add players per team
- **Auto Points**: When you save results, points are calculated automatically

## Testing Locally

```bash
# Seed database
python seed_data.py

# Start Flask server
python app.py

# Open in browser (dev mode — no Telegram needed)
# http://localhost:5000?telegram_id=12345&username=testuser&first_name=Test
```

The Mini App works in a regular browser for testing — it falls back to query parameters when Telegram's WebApp JS isn't available.

## Pre-loaded Data

- **70 league matches** (full IPL 2026 schedule)
- **10 teams** with complete squads
- **200+ players** with roles (Batter/Bowler/All-Rounder)

---

Built with Flask + python-telegram-bot + SQLite. No external database needed.
