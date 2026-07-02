# Deploy (VPS + Docker Compose + Caddy auto-TLS)

Stack: `db` (Postgres) · `redis` · `bot` (aiogram, polling) · `web` (FastAPI Mini App) · `caddy` (HTTPS).
Only Caddy is exposed publicly (80/443); it reverse-proxies the Mini App. The bot uses
polling, so it needs no inbound port.

## 0. Security first (do this before anything else)
Secrets were committed to git. Even though the repo is private:
- **Rotate the bot token**: BotFather → `/revoke` → put the new token in `.env`.
- Consider rotating the OpenAI key and DB password too.
- `.env` and `bot/token_bot.env` are now untracked (see `.gitignore`). Commit that removal:
  ```bash
  git add .gitignore .dockerignore
  git commit -m "Stop tracking secrets and build junk"
  git push
  ```
- Optional (private repo → lower priority): purge them from history with
  [BFG](https://rtfin.github.io/bfg-repo-cleaner/) or `git filter-repo`, then force-push.

## 1. Get a VPS + domain
- VPS: Hetzner CX22 (~€4.5/mo, 2 vCPU / 4 GB) or DigitalOcean, Ubuntu 22.04. 4 GB RAM matters — the image is ~2–3 GB (torch).
- Domain: buy any cheap one. Add a DNS **A record** → your VPS IP (e.g. `rating.example.com`).

## 2. Install Docker on the VPS
```bash
curl -fsSL https://get.docker.com | sh
```

## 3. Get the code + secrets onto the VPS
```bash
git clone https://github.com/sithxxx/facebot.git && cd facebot
cp .env.example .env
nano .env   # fill TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, DOMAIN, MINIAPP_URL, DATABASE_URL...
```
Set in `.env`:
- `DOMAIN=rating.example.com`
- `MINIAPP_URL=https://rating.example.com`
- `DATABASE_URL=postgresql+asyncpg://user:password@db:5432/facebot`
- `WEBHOOK_URL=` (empty → polling)

`.env` is git-ignored, so it lives only on the server — never commit it.

## 4. Launch
```bash
docker compose up -d --build
docker compose logs -f bot web caddy
```
- Caddy fetches the TLS cert automatically on first hit (DNS must already point at the box).
- `bot` creates DB tables on startup (`init_db` → `create_all`).

## 4.5 Payments (before going live)
Prices: ⭐ 250 Stars · 💳 299 ₽ · 🪙 3.5 USDT. In `.env` on the server:

- **`TEST_MODE=false`** — CRITICAL. `true` bypasses all payments (every analysis
  becomes free). The bot screams into the log on startup if it's on.
- **Stars** — works out of the box, no token needed. Payout of earned Stars is
  done later via Fragment (needs a TON wallet; Stars mature for 21 days).
- **Card (RUB)** — set `CARD_PROVIDER_TOKEN`: BotFather → `/mybots` → your bot →
  Bot Settings → Payments → pick a RU provider (ЮKassa / Robokassa / PayMaster).
  The provider requires self-employed/ИП/ООО registration. Until the token is
  set, the card button will error — consider it disabled.
- **Crypto** — set `CRYPTOBOT_TOKEN`: open @CryptoBot in Telegram → Crypto Pay →
  Create App → copy the token.

## 5. Verify
- `https://rating.example.com` opens (browser shows the "open via bot" state — normal, no initData).
- In Telegram: `/start` → button **🏆 Открыть рейтинг** opens the Mini App.
- Do a face analysis → you appear in the leaderboard.

## Notes / gotchas
- **DB schema**: the new `User` columns (`best_score`, `best_at`, `show_on_leaderboard`) are
  created for a fresh DB. Migrating an existing DB needs a manual `ALTER TABLE` (no Alembic).
- **Image size**: first build is slow (~2–3 GB). Ensure a few GB free disk.
- **Bot token in one place only**: the app reads env vars; `.env` is loaded via `env_file` in
  compose and is NOT baked into the image (`.dockerignore` excludes it).
- **Updates**: `git pull && docker compose up -d --build`.
