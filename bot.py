import discord
from discord.ext import commands
from datetime import timedelta
import json
import os
import requests
from bs4 import BeautifulSoup
from discord.ext import tasks

# -----------------------------
# CONFIGURATION
# -----------------------------
TOKEN = os.environ["TOKEN"]
GUILD_ID = 1492213186902888510
FRIENDLY_CHANNEL_ID = 1497522011872690217
VOTE_FILE = "friendly.json"
LAST_VIDEO_FILE = "last_video.json"
MOD_ROLE_ID = 1497531521597182123
TIKTOK_USERNAME = "darkyanitedtpss"

FANS_ROLE = 1497343156214173910
ACADEMY_ROLE = 1497348156164276316
MAIN_TEAM_ROLE = 1497351283642859550

LOGO_URL = "https://media.discordapp.net/attachments/1497519739776532630/1503483685368889496/file_000000000f147243bc92c61df07bf5d1_1.png?ex=6a0383cb&is=6a02324b&hm=d0b6809e1864ca9d1ab289256ea999374a92ffe904010de0a24a5250de9f86ee&=&format=webp&quality=lossless&width=847&height=847"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

warnings = {}

# -----------------------------
# DATA PERSISTENCE
# -----------------------------

def load_votes():
    try:
        with open(VOTE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"total": 0}

def save_votes(data):
    with open(VOTE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_last_video():
    try:
        with open(LAST_VIDEO_FILE, "r") as f:
            return json.load(f).get("last_video_id")
    except:
        return None

def save_last_video(video_id):
    with open(LAST_VIDEO_FILE, "w") as f:
        json.dump({"last_video_id": video_id}, f)

def is_mod(interaction: discord.Interaction):
    return any(role.id >= MOD_ROLE_ID for role in interaction.user.roles)

# -----------------------------
# TIKTOK CHECKER
# -----------------------------

def get_latest_tiktok():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.find_all("a", href=True)
        for link in links:
            href = link["href"]
            if "/video/" in href:
                video_id = href.split("/video/")[-1].split("?")[0]
                video_url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/{video_id}"
                return video_id, video_url
    except Exception as e:
        print(f"TikTok check failed: {e}")
    return None, None

@tasks.loop(minutes=5)
async def check_tiktok():
    video_id, video_url = get_latest_tiktok()
    if not video_id:
        return

    last_video_id = load_last_video()
    if video_id == last_video_id:
        return

    save_last_video(video_id)

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return

    embed = discord.Embed(
        title="🎵  DARK YANITED  |  NEW VIDEO",
        description=(
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            "📲  **A NEW TIKTOK HAS JUST DROPPED!**\n\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            f"🔗  **Watch it here:**\n{video_url}\n\n"
            "❤️  **Like, comment & share!**\n"
            "🔔  Turn on notifications so you never miss a drop!\n\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        ),
        color=0xAA0000
    )
    embed.set_thumbnail(url=LOGO_URL)
    embed.set_footer(text="DARK YANITED FC  •  Follow us on TikTok!")

    sent = 0
    failed = 0
    for member in guild.members:
        if member.bot:
            continue
        try:
            await member.send(embed=embed)
            sent += 1
        except:
            failed += 1

    print(f"TikTok DMs sent: {sent} success, {failed} failed")

# -----------------------------
# FRIENDLY SYSTEM
# -----------------------------

@bot.tree.command(name="friendly", description="Post a friendly match announcement!")
async def friendly(interaction: discord.Interaction):
    if not is_mod(interaction):
        return await interaction.response.send_message("❌ You don't have permission to use this.", ephemeral=True)

    channel = bot.get_channel(FRIENDLY_CHANNEL_ID)

    embed = discord.Embed(
        title="⚽  DARK YANITED  |  FRIENDLY",
        description=(
            "```\n"
            "██████╗ ██╗   ██╗\n"
            "██╔══██╗╚██╗ ██╔╝\n"
            "██║  ██║ ╚████╔╝ \n"
            "██║  ██║  ╚██╔╝  \n"
            "██████╔╝   ██║   \n"
            "╚═════╝    ╚═╝   \n"
            "```\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            "🏟️  **FRIENDLY MATCH — OPEN FOR SIGNUPS**\n\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            "4️⃣  **4 REACTS NEEDED TO START**\n"
            "⚡  React fast — spots fill quickly!\n\n"
            "📋  **SCRIM RULES**\n"
            "```\n"
            "  ➤  If you need to leave → UNREACT\n"
            "  ➤  Don't react if you can't commit\n"
            "  ➤  Respect all players\n"
            "```\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            "🔔  **REACT BELOW TO JOIN** ⬇️"
        ),
        color=0xAA0000
    )

    embed.set_thumbnail(url=LOGO_URL)
    embed.set_footer(text="DARK YANITED FC  •  React ⚽ to join the match!")

    pings = f"<@&{FANS_ROLE}> <@&{ACADEMY_ROLE}> <@&{MAIN_TEAM_ROLE}>"

    await interaction.response.send_message("✅ Friendly posted!", ephemeral=True)

    if channel:
        msg = await channel.send(content=pings, embed=embed)
        await msg.add_reaction("⚽")

# -----------------------------
# TEST VIDEO DM
# -----------------------------

@bot.tree.command(name="test-vid", description="Test the TikTok DM notification")
async def test_vid(interaction: discord.Interaction):
    if not is_mod(interaction):
        return await interaction.response.send_message("❌ You don't have permission to use this.", ephemeral=True)

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return await interaction.response.send_message("❌ Could not find server.", ephemeral=True)

    embed = discord.Embed(
        title="🎵  DARK YANITED  |  NEW VIDEO",
        description=(
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            "🧪  **THIS IS A TEST MESSAGE**\n\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            "📲  **A NEW TIKTOK HAS JUST DROPPED!**\n\n"
            "🔗  **Watch it here:**\nhttps://www.tiktok.com/@darkyanitedtpss\n\n"
            "❤️  **Like, comment & share!**\n"
            "🔔  Turn on notifications so you never miss a drop!\n\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        ),
        color=0xAA0000
    )
    embed.set_thumbnail(url=LOGO_URL)
    embed.set_footer(text="DARK YANITED FC  •  Follow us on TikTok!")

    await interaction.response.send_message("✅ Sending test DMs...", ephemeral=True)

    sent = 0
    failed = 0
    for member in guild.members:
        if member.bot:
            continue
        try:
            await member.send(embed=embed)
            sent += 1
        except:
            failed += 1

    await interaction.followup.send(f"✅ Test done! {sent} sent, {failed} failed.", ephemeral=True)

# -----------------------------
# MODERATION COMMANDS
# -----------------------------

@bot.tree.command(name="ban", description="Ban a member from the server")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ You don't have permission to ban.", ephemeral=True)
    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ {member} has been banned. Reason: {reason}")

@bot.tree.command(name="kick", description="Kick a member from the server")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ You don't have permission to kick.", ephemeral=True)
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member} has been kicked. Reason: {reason}")

@bot.tree.command(name="warn", description="Warn a member")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ You don't have permission to warn.", ephemeral=True)
    uid = str(member.id)
    warnings.setdefault(uid, []).append(reason)
    await interaction.response.send_message(f"⚠️ {member.mention} has been warned. Total warnings: {len(warnings[uid])}")

@bot.tree.command(name="timeout", description="Timeout a member for a set number of minutes")
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason"):
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ You don't have permission to timeout.", ephemeral=True)
    await member.timeout(timedelta(minutes=minutes), reason=reason)
    await interaction.response.send_message(f"⏳ {member} has been timed out for {minutes} minutes.")

@bot.tree.command(name="untimeout", description="Remove a timeout from a member")
async def untimeout(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ You don't have permission to do this.", ephemeral=True)
    await member.timeout(None)
    await interaction.response.send_message(f"✅ {member}'s timeout has been removed.")

@bot.tree.command(name="clear", description="Delete a number of messages from this channel")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ You don't have permission to clear messages.", ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)

# -----------------------------
# STARTUP & SYNC
# -----------------------------

@bot.event
async def on_ready():
    await bot.tree.sync()
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    check_tiktok.start()
    print(f"Synced commands for guild {GUILD_ID}")
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
