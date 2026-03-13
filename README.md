\# Birthday Bot



A Discord bot that automatically celebrates server members' birthdays — assigning a special role, announcing in a designated channel, and checking hourly so no one gets missed.



Built with Python and deployed to the cloud via Railway.



---



\## Features



| Command | Description |

|---|---|

| `/setbirthday` | Save your birthday (month + day) |

| `/mybirthday` | Check your saved birthday |

| `/removebirthday` | Delete your saved birthday |

| `/listbirthdays` | See all upcoming birthdays, sorted by soonest |



\*\*Automatic birthday handling:\*\*

\- Checks every hour so late registrations are never missed

\- Assigns a \*\*Birthday\*\* role on the member's birthday (auto-created if it doesn't exist)

\- Pings the member with a birthday announcement in a designated channel

\- Removes the role the next day and resets for the following year

\- Announces only once per birthday — no duplicate pings even with hourly checks



---



\## Tech Stack



\- \*\*Python 3.11\*\*

\- \*\*discord.py 2.x\*\* — slash commands, role management, task loops

\- \*\*python-dotenv\*\* — secure token handling

\- \*\*Railway\*\* — cloud hosting for 24/7 uptime

\- \*\*GitHub\*\* — version control and auto-deploy pipeline



---



\## Architecture



```

GitHub (source) → Railway (auto-deploy) → Discord (live bot)

&nbsp;    ↑

Local edits (git push triggers redeploy)

```



Birthdays are stored in a local `birthdays.json` file. The bot runs an hourly task loop that:

1\. Checks all saved birthdays against today's date (UTC)

2\. Assigns/removes the Birthday role as appropriate

3\. Sends a one-time announcement per birthday using a per-user `announced` flag



---



\## Setup



\### Prerequisites

\- Python 3.10+

\- A Discord account and server

\- A \[Discord Developer Portal](https://discord.com/developers/applications) application with a bot token



\### 1. Clone the repo

```bash

git clone https://github.com/crimsonpistil/birthday-bot.git

cd birthday-bot

```



\### 2. Install dependencies

```bash

pip install -r requirements.txt

```



\### 3. Configure environment

Create a `.env` file in the project root:

```

DISCORD\_TOKEN=your-bot-token-here

```



\### 4. Configure the bot

Open `bot.py` and update these values:

```python

BIRTHDAY\_ROLE\_NAME = "Birthday"       # Role name to assign on birthdays

BIRTHDAY\_CHANNEL\_ID = 000000000000    # Right-click channel → Copy ID

```



\### 5. Discord Developer Portal setup

\- Enable \*\*Server Members Intent\*\* and \*\*Message Content Intent\*\* under Bot → Privileged Gateway Intents

\- Invite the bot with scopes: `bot`, `applications.commands`

\- Bot permissions: `Manage Roles`, `Send Messages`, `View Channels`

\- Ensure the bot's role is ranked \*\*above\*\* the Birthday role in Server Settings → Roles



\### 6. Run locally

```bash

python bot.py

```



---



\## Cloud Deployment (Railway)



1\. Push the repo to GitHub

2\. Connect the repo to \[Railway](https://railway.app) via \*\*Deploy from GitHub\*\*

3\. Add `DISCORD\_TOKEN` as an environment variable in Railway's Variables tab

4\. Railway auto-deploys on every `git push`



---



\## Project Structure



```

birthday-bot/

├── bot.py            # Main bot logic

├── requirements.txt  # Dependencies

├── .env              # Secret token (not committed)

├── .gitignore        # Excludes .env and runtime files

└── birthdays.json    # Auto-generated at runtime (not committed)

```



---



\## Security Notes



\- The `.env` file and `birthdays.json` are excluded from version control via `.gitignore`

\- No personal data (names, full dates of birth) is stored — only Discord user IDs with a month and day

\- The bot token is loaded from environment variables, never hardcoded



---



\## License



MIT — free to use, modify, and deploy.



