# Agoda Price Agent

This project automatically updates prices on Agoda from a message sent to a Telegram bot.

I built it to help grow my family's business: I was the one changing prices by hand every time, which took a lot of time away from more important parts of the business.

**Project status:** this project is not finished yet. By my own estimate it is about 80% complete (see the Status section below for what works and what is still missing).

## How it works

1. You send a price message to the Telegram bot.
2. Groq parses the message into structured JSON, and the bot sends it back to you.
3. You review the JSON. If everything is correct, you confirm by replying "OK".
4. The bot logs into the Agoda Partner Portal and Playwright updates the prices automatically.

The confirmation step is a safety rule: the bot never touches Agoda without an explicit "OK".

## Status

**Working**
- Reads a price message and returns structured JSON (dates, weekday price, weekend price).
- Waits for the user's "OK" before doing anything on Agoda.
- Logs into the Agoda Partner Portal. When Agoda asks for an email verification, the bot reads the verification email over IMAP and opens the sign-in link.
- Updates the prices of every room of one property, once for weekdays and once for weekends.

**In progress**
- Support for the other properties: their room IDs are collected, but the bot is not wired to them yet.
- Reading the property name from the message instead of using a fixed one.
- Whole-house prices (one room per property, different logic).
- Special dates (for example public holidays) written in the message.

**Not included**
- Other platforms (Expedia, Trip.com).
- Automated tests.
- Logging beyond simple console messages.

## Tech stack

- Python 3.11
- python-telegram-bot (async)
- Groq API (the model parses the message into JSON)
- Playwright (async API) to control the browser
- `imaplib` (standard library) to read the verification email

## Setup

1. Clone the repository and create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```
2. Copy `.env.example` to `.env` and fill in your own values (Telegram bot token, Groq API key, Agoda login, Gmail app password).
3. Edit the `PROPRIETES` dictionary in `agoda_updater.py` with your own property, room and rate plan IDs.
4. Run the bot:
   ```
   python bot.py
   ```

The Gmail account needs 2-Step Verification enabled to create an app password.

## Notes

- This tool runs on my family's own Agoda account, on our own properties, and asks for a confirmation before every change.
- Agoda's login flow changes sometimes (password, one-time code, email link), so the login code may need updating.
- I have not checked Agoda's terms of use on automation. Read them before using this on your own account.
- Never commit your `.env` file: it contains your passwords and tokens.
