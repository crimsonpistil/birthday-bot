import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# Load token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ── Configuration ──────────────────────────────────────────────────────────────
BIRTHDAY_ROLE_NAME = "Birthday!!"
BIRTHDAY_CHANNEL_ID = 681924312604999754  # 🛡・mil-hangout
MODERATOR_ROLE_NAME = "Moderator"
DATA_FILE = "/data/birthdays.json"

# ── Bot setup ──────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ── Data helpers ───────────────────────────────────────────────────────────────
def load_birthdays() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_birthdays(data: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def format_date(month: int, day: int) -> str:
    dt = datetime(2001, month, day)
    return dt.strftime("%B %#d")

def is_moderator(interaction: discord.Interaction) -> bool:
    return any(role.name == MODERATOR_ROLE_NAME for role in interaction.user.roles)

# ── Events ─────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
    hourly_birthday_check.start()

# ── Slash Commands ─────────────────────────────────────────────────────────────
@bot.tree.command(name="setbirthday", description="Set your birthday (month and day only)")
@app_commands.describe(month="Month (1-12)", day="Day (1-31)")
async def setbirthday(interaction: discord.Interaction, month: int, day: int):
    if not (1 <= month <= 12):
        await interaction.response.send_message("❌ Month must be between 1 and 12.", ephemeral=True)
        return
    if not (1 <= day <= 31):
        await interaction.response.send_message("❌ Day must be between 1 and 31.", ephemeral=True)
        return
    try:
        datetime(year=2001, month=month, day=day)
    except ValueError:
        await interaction.response.send_message(
            f"❌ {month}/{day} isn't a valid date.", ephemeral=True
        )
        return

    data = load_birthdays()
    user_id = str(interaction.user.id)
    data[user_id] = {"month": month, "day": day, "announced": False}
    save_birthdays(data)

    await interaction.response.send_message(
        f"🎂 Got it! Your birthday is saved as **{format_date(month, day)}**.", ephemeral=True
    )

@bot.tree.command(name="setbirthdayfor", description="[Moderator] Set a birthday for another user")
@app_commands.describe(user="The member to set a birthday for", month="Month (1-12)", day="Day (1-31)")
async def setbirthdayfor(interaction: discord.Interaction, user: discord.Member, month: int, day: int):
    if not is_moderator(interaction):
        await interaction.response.send_message("❌ You need the Moderator role to use this command.", ephemeral=True)
        return
    if not (1 <= month <= 12):
        await interaction.response.send_message("❌ Month must be between 1 and 12.", ephemeral=True)
        return
    if not (1 <= day <= 31):
        await interaction.response.send_message("❌ Day must be between 1 and 31.", ephemeral=True)
        return
    try:
        datetime(year=2001, month=month, day=day)
    except ValueError:
        await interaction.response.send_message(
            f"❌ {month}/{day} isn't a valid date.", ephemeral=True
        )
        return

    data = load_birthdays()
    user_id = str(user.id)
    data[user_id] = {"month": month, "day": day, "announced": False}
    save_birthdays(data)

    await interaction.response.send_message(
        f"🎂 Birthday for **{user.display_name}** saved as **{format_date(month, day)}**.", ephemeral=True
    )

@bot.tree.command(name="mybirthday", description="Check what birthday is saved for you")
async def mybirthday(interaction: discord.Interaction):
    data = load_birthdays()
    entry = data.get(str(interaction.user.id))
    if not entry:
        await interaction.response.send_message(
            "You haven't set a birthday yet! Use `/setbirthday` to add one.", ephemeral=True
        )
        return
    m, d = entry["month"], entry["day"]
    await interaction.response.send_message(
        f"🎂 Your saved birthday is **{format_date(m, d)}**.", ephemeral=True
    )

@bot.tree.command(name="removebirthday", description="Remove your saved birthday")
async def removebirthday(interaction: discord.Interaction):
    data = load_birthdays()
    user_id = str(interaction.user.id)
    if user_id not in data:
        await interaction.response.send_message("You don't have a birthday saved.", ephemeral=True)
        return
    del data[user_id]
    save_birthdays(data)
    await interaction.response.send_message("🗑️ Your birthday has been removed.", ephemeral=True)

@bot.tree.command(name="removebirthdayfor", description="[Moderator] Remove a birthday for another user")
@app_commands.describe(user="The member whose birthday to remove")
async def removebirthdayfor(interaction: discord.Interaction, user: discord.Member):
    if not is_moderator(interaction):
        await interaction.response.send_message("❌ You need the Moderator role to use this command.", ephemeral=True)
        return
    data = load_birthdays()
    user_id = str(user.id)
    if user_id not in data:
        await interaction.response.send_message(f"**{user.display_name}** doesn't have a birthday saved.", ephemeral=True)
        return
    del data[user_id]
    save_birthdays(data)
    await interaction.response.send_message(f"🗑️ Birthday for **{user.display_name}** has been removed.", ephemeral=True)

@bot.tree.command(name="listbirthdays", description="See all upcoming birthdays in the server")
async def listbirthdays(interaction: discord.Interaction):
    data = load_birthdays()
    if not data:
        await interaction.response.send_message("No birthdays saved yet!", ephemeral=True)
        return

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    entries = []

    for uid, bd in data.items():
        member = interaction.guild.get_member(int(uid))
        if not member:
            continue
        this_year = datetime(today.year, bd["month"], bd["day"])
        if this_year < today:
            this_year = datetime(today.year + 1, bd["month"], bd["day"])
        days_away = (this_year - today).days
        entries.append((days_away, format_date(bd["month"], bd["day"]), member.display_name))

    entries.sort()

    if not entries:
        await interaction.response.send_message("No members with saved birthdays found.", ephemeral=True)
        return

    lines = [
        f"🎂 **{name}** — {label} ({d} day{'s' if d != 1 else ''} away)"
        for d, label, name in entries
    ]

    embed = discord.Embed(
        title="🎉 Upcoming Birthdays",
        description="\n".join(lines),
        color=discord.Color.pink()
    )
    await interaction.response.send_message(embed=embed)

# ── Hourly check loop ──────────────────────────────────────────────────────────
@tasks.loop(hours=1)
async def hourly_birthday_check():
    now = datetime.utcnow()
    today_month, today_day = now.month, now.day
    data = load_birthdays()
    data_changed = False

    for guild in bot.guilds:
        role = discord.utils.get(guild.roles, name=BIRTHDAY_ROLE_NAME)
        if not role:
            try:
                role = await guild.create_role(
                    name=BIRTHDAY_ROLE_NAME,
                    color=discord.Color.gold(),
                    reason="Auto-created by Birthday Bot"
                )
            except discord.Forbidden:
                print(f"⚠️ Missing permissions to create role in {guild.name}")
                continue

        channel = bot.get_channel(BIRTHDAY_CHANNEL_ID)

        for uid, bd in data.items():
            member = guild.get_member(int(uid))
            if not member:
                continue

            is_birthday = (bd["month"] == today_month and bd["day"] == today_day)
            already_announced = bd.get("announced", False)

            if is_birthday:
                if role not in member.roles:
                    try:
                        await member.add_roles(role, reason="Happy Birthday!")
                    except discord.Forbidden:
                        print(f"⚠️ Can't assign role to {member}")

                if not already_announced and channel:
                    await channel.send(
                        f"🎂 Happy Birthday, {member.mention}!"
                    )
                    data[uid]["announced"] = True
                    data_changed = True

            else:
                if role in member.roles:
                    try:
                        await member.remove_roles(role, reason="Birthday over")
                    except discord.Forbidden:
                        pass
                if already_announced:
                    data[uid]["announced"] = False
                    data_changed = True

    if data_changed:
        save_birthdays(data)

@hourly_birthday_check.before_loop
async def before_check():
    await bot.wait_until_ready()
    now = datetime.utcnow()
    seconds_to_wait = (60 - now.minute) * 60 - now.second
    print(f"⏰ First birthday check in {seconds_to_wait // 60} minutes (then every hour)")
    await asyncio.sleep(seconds_to_wait)

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN not found! Make sure your .env file exists and has DISCORD_TOKEN=your-token")
    bot.run(TOKEN)
