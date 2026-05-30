import discord
from discord.ext import commands
from datetime import timedelta
import json
import os
import requests
from bs4 import BeautifulSoup
from discord.ext import tasks
import asyncio
import time

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

WIPE_AUTHORIZED_ID = 974698574036217886  # Antoni's ID

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
# DM SENDER WITH PROGRESS
# -----------------------------

async def send_dms(interaction: discord.Interaction, embed: discord.Embed, is_followup: bool = False):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        msg = "❌ Could not find server."
        if is_followup:
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
        return

    members = [m for m in guild.members if not m.bot]
    total = len(members)
    sent = 0
    failed = 0
    start_time = time.time()

    if is_followup:
        progress_msg = await interaction.followup.send(
            f"📤 Sending DMs... `0/{total}` | ⏳ Estimated time: calculating...",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"📤 Sending DMs... `0/{total}` | ⏳ Estimated time: calculating...",
            ephemeral=True
        )
        progress_msg = await interaction.original_response()

    for i, member in enumerate(members, 1):
        try:
            await member.send(embed=embed)
            sent += 1
        except:
            failed += 1

        await asyncio.sleep(1)

        if i % 5 == 0 or i == total:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = int(avg_time * (total - i))
            mins, secs = divmod(remaining, 60)

            if remaining > 0:
                time_str = f"{mins}m {secs}s remaining"
            else:
                time_str = "almost done!"

            await progress_msg.edit(content=(
                f"📤 Sending DMs... `{i}/{total}`\n"
                f"✅ Sent: `{sent}` | ❌ Failed: `{failed}`\n"
                f"⏳ {time_str}"
            ))

    await progress_msg.edit(content=(
        f"✅ **Done!**\n"
        f"📤 Sent: `{sent}/{total}`\n"
        f"❌ Failed (DMs closed): `{failed}`\n"
        f"⏱️ Took: `{int(time.time() - start_time)}s`"
    ))

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
        await asyncio.sleep(1)

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

    await send_dms(interaction, embed)

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
# WIPE COMMAND — ANTONI ONLY
# -----------------------------

@bot.tree.command(name="wipe", description="Wipe the server — Antoni only")
@app_commands.describe(confirm="Type CONFIRM to proceed")
async def wipe(interaction: discord.Interaction, confirm: str):
    if interaction.user.id != WIPE_AUTHORIZED_ID:
        return await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)

    if confirm != "CONFIRM":
        return await interaction.response.send_message(
            "⚠️ To wipe the server, pass `CONFIRM` as the argument.",
            ephemeral=True
        )

    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    kicked = 0
    channels_deleted = 0
    roles_deleted = 0

    # Kick all non-bot members except Antoni
    for member in guild.members:
        if member.bot or member.id == WIPE_AUTHORIZED_ID:
            continue
        try:
            await member.kick(reason="Server wiped by Antoni")
            kicked += 1
        except:
            pass

    # Delete all channels
    for channel in guild.channels:
        try:
            await channel.delete(reason="Server wiped by Antoni")
            channels_deleted += 1
        except:
            pass

    # Delete all roles except @everyone and roles above the bot
    for role in guild.roles:
        if role.is_default() or role >= guild.me.top_role:
            continue
        try:
            await role.delete(reason="Server wiped by Antoni")
            roles_deleted += 1
        except:
            pass

    # Create a new channel and post the wipe notice
    try:
        new_channel = await guild.create_text_channel("general")
        embed = discord.Embed(
            title="🧹 Server Wiped",
            description="This server has been wiped by **Antoni**.",
            color=0xAA0000
        )
        embed.set_footer(text="DARK YANITED FC")
        await new_channel.send(embed=embed)
    except:
        pass

    print(f"Wipe complete — kicked {kicked}, deleted {channels_deleted} channels, {roles_deleted} roles")

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
