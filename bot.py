import discord
from discord.ext import commands
from datetime import timedelta
import json
import os

# -----------------------------
# CONFIGURATION
# -----------------------------
TOKEN = os.environ["TOKEN"]
GUILD_ID = 1492213186902888510
FRIENDLY_CHANNEL_ID = 1497522011872690217
VOTE_FILE = "friendly.json"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

warnings = {}

def load_votes():
    try:
        with open(VOTE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"total": 0}

def save_votes(data):
    with open(VOTE_FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.tree.command(name="friendly", description="Vote for a friendly match!")
async def friendly(interaction: discord.Interaction):
    data = load_votes()
    data["total"] = data.get("total", 0) + 1
    votes = data["total"]
    save_votes(data)

    embed = discord.Embed(
        title="🌟 Friendly Match Vote",
        description=f"{interaction.user.mention} wants a friendly match!\n\n**Votes:** `{votes}/5`",
        color=0x5865F2
    )
    await interaction.response.send_message(embed=embed)

    if votes >= 5:
        data["total"] = 0
        save_votes(data)
        channel = bot.get_channel(FRIENDLY_CHANNEL_ID)
        if channel:
            event_embed = discord.Embed(
                title="⚽ Friendly Match Incoming!",
                description="🔥 **5 votes reached!**\nA community friendly match is starting now!",
                color=0x00ff99
            )
            await channel.send(content="@everyone", embed=event_embed)

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

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"Synced commands for guild {GUILD_ID}")
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
