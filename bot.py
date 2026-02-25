"""
Bruh Bot - Discord bot for random responses and community interactions
Now with optional LLM integration via Ollama
"""
import discord
import random
import os
import pathlib
import traceback
import re
import aiohttp
import asyncio
from discord.ext import commands
from discord import app_commands

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG_FILE = "config.txt"
BOT_DIR = pathlib.Path(__file__).parent.resolve()

CONFIG_TEMPLATE = """# Bruh Bot Configuration
# Lines starting with # are comments and are ignored.

# --- Core ---
TOKEN=YOUR_BOT_TOKEN_HERE
COMMAND_PREFIX=!

# --- Message Files ---
DEFAULT_MSGS_FILE=default_msgs.txt
MENTION_MSGS_FILE=mention_msgs.txt

# --- Channel IDs ---
SUGGESTION_CHANNEL_ID=
RAPE_CHANNEL_ID=
AUTO_THREAD_CHANNEL_ID=
CHICKEN_OUT_CHANNEL_ID=

# --- Role IDs ---
SUGGESTION_PING_ROLE_ID=

# --- Authorized User ---
# User ID allowed to approve/reject suggestions
AUTHORIZED_USER_ID=

# --- Behavior ---
# 1-in-X chance to send a random message on any message
RANDOM_MESSAGE_CHANCE=100
# Time window (seconds) after joining to count as "chickened out"
CHICKEN_OUT_TIMEOUT=900
# Message/URL sent when someone chickens out
CHICKENED_OUT_MSG=https://tenor.com/view/walk-away-gif-8390063

# --- Feature Toggles ---
ENABLE_RANDOM_MESSAGES=true
ENABLE_MENTION_RESPONSES=true
ENABLE_AUTO_THREAD=false
ENABLE_CHICKEN_OUT=true
ENABLE_SUGGESTIONS=true
ENABLE_RAPE_COMMAND=false

# -------------------------------------------------------
# LLM Settings (via Ollama)
# -------------------------------------------------------
# Set ENABLE_LLM=true to have the bot respond with AI when
# someone mentions it with a message (e.g. "@Bruh tell me a joke")
# If the mention has NO message, it falls back to mention_msgs.txt as usual.
ENABLE_LLM=false

# Ollama API base URL (default: local, change if Ollama is on another machine)
LLM_BASE_URL=http://localhost:11434

# Model to use. Run `ollama list` to see installed models.
LLM_MODEL=mistral

# System prompt — defines the bot's personality
LLM_SYSTEM_PROMPT=You are Bruh, a chaotic and sarcastic Discord bot. Keep all responses under 3 sentences. Be witty, slightly unhinged, and funny. Never be helpful in a boring way.

# Max tokens the LLM will generate per response
LLM_MAX_TOKENS=200

# Seconds to wait for Ollama before giving up
LLM_TIMEOUT=30

# If LLM fails or times out, fall back to a random mention message instead of showing an error
LLM_FALLBACK_ON_ERROR=true

# Show a typing indicator while waiting for the LLM response
LLM_TYPING_INDICATOR=true
"""


def create_config_template():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(CONFIG_TEMPLATE)


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ '{CONFIG_FILE}' not found. Creating template...")
        create_config_template()
        print("✅ Template created. Fill in your values and restart.")
        exit(1)

    config = {}
    numeric_keys = {
        "SUGGESTION_CHANNEL_ID", "RAPE_CHANNEL_ID", "AUTO_THREAD_CHANNEL_ID",
        "CHICKEN_OUT_CHANNEL_ID", "SUGGESTION_PING_ROLE_ID", "AUTHORIZED_USER_ID",
        "RANDOM_MESSAGE_CHANCE", "CHICKEN_OUT_TIMEOUT", "LLM_MAX_TOKENS", "LLM_TIMEOUT",
    }
    boolean_keys = {
        "ENABLE_RANDOM_MESSAGES", "ENABLE_MENTION_RESPONSES", "ENABLE_AUTO_THREAD",
        "ENABLE_CHICKEN_OUT", "ENABLE_SUGGESTIONS", "ENABLE_RAPE_COMMAND",
        "ENABLE_LLM", "LLM_FALLBACK_ON_ERROR", "LLM_TYPING_INDICATOR",
    }

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip("\"'")

            if key in numeric_keys:
                try:
                    config[key] = int(value) if value else 0
                except ValueError:
                    print(f"❌ {key} must be a number, got '{value}'. Fix {CONFIG_FILE}.")
                    exit(1)
            elif key in boolean_keys:
                config[key] = value.lower() in ("true", "1", "yes", "on")
            else:
                config[key] = value

    # Validate required fields
    required = ["TOKEN", "DEFAULT_MSGS_FILE", "MENTION_MSGS_FILE"]
    missing = [k for k in required if k not in config or not config[k]]
    if missing:
        print(f"❌ Missing required config fields: {', '.join(missing)}")
        exit(1)

    if config["TOKEN"] == "YOUR_BOT_TOKEN_HERE":
        print("❌ TOKEN is not set. Edit config.txt with your bot token.")
        exit(1)

    if config.get("RANDOM_MESSAGE_CHANCE", 0) < 1:
        print("❌ RANDOM_MESSAGE_CHANCE must be at least 1.")
        exit(1)

    # Defaults for optional fields
    config.setdefault("COMMAND_PREFIX", "!")
    config.setdefault("CHICKEN_OUT_TIMEOUT", 900)
    config.setdefault("CHICKENED_OUT_MSG", "https://tenor.com/view/walk-away-gif-8390063")
    config.setdefault("AUTHORIZED_USER_ID", 0)
    config.setdefault("ENABLE_LLM", False)
    config.setdefault("LLM_BASE_URL", "http://localhost:11434")
    config.setdefault("LLM_MODEL", "mistral")
    config.setdefault("LLM_SYSTEM_PROMPT", "You are Bruh, a sarcastic Discord bot. Keep responses short and funny.")
    config.setdefault("LLM_MAX_TOKENS", 200)
    config.setdefault("LLM_TIMEOUT", 30)
    config.setdefault("LLM_FALLBACK_ON_ERROR", True)
    config.setdefault("LLM_TYPING_INDICATOR", True)

    return config


cfg = load_config()


# ============================================================
# MESSAGE LISTS
# ============================================================

class MessageLists:
    """Loads and manages the default and mention message lists."""

    def __init__(self):
        self.default: list[str] = []
        self.mention: list[str] = []
        self.load()

    def _read_file(self, filename: str) -> list[str]:
        path = BOT_DIR / filename
        if not path.exists():
            print(f"ℹ️  '{path}' not found — creating empty file.")
            path.write_text("", encoding="utf-8")
        lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.strip().startswith("#")]
        print(f"✅ Loaded {len(lines)} messages from {path.name}")
        return lines

    def _write_file(self, filename: str, messages: list[str]):
        path = BOT_DIR / filename
        path.write_text("\n".join(messages) + "\n", encoding="utf-8")

    def load(self):
        self.default = self._read_file(cfg["DEFAULT_MSGS_FILE"])
        self.mention = self._read_file(cfg["MENTION_MSGS_FILE"])

    def add(self, message: str, list_type: str) -> bool:
        """Add a message to 'default' or 'mention'. Returns True if added, False if duplicate."""
        target = self.default if list_type == "default" else self.mention
        filename = cfg["DEFAULT_MSGS_FILE"] if list_type == "default" else cfg["MENTION_MSGS_FILE"]
        if message in target:
            return False
        target.append(message)
        self._write_file(filename, target)
        return True


msgs = MessageLists()


# ============================================================
# LLM CLIENT
# ============================================================

def get_mention_text(message: discord.Message, bot_user: discord.ClientUser) -> str:
    """Strip all @bot mentions from the message and return the remaining text."""
    content = message.content
    # Remove <@BOT_ID> and <@!BOT_ID> patterns
    content = re.sub(rf"<@!?{bot_user.id}>", "", content).strip()
    return content


async def query_llm(prompt: str) -> str | None:
    """
    Send a prompt to Ollama and return the response text.
    Returns None on failure.
    """
    url = f"{cfg['LLM_BASE_URL']}/api/chat"
    payload = {
        "model": cfg["LLM_MODEL"],
        "stream": False,
        "options": {
            "num_predict": cfg["LLM_MAX_TOKENS"],
        },
        "messages": [
            {"role": "system", "content": cfg["LLM_SYSTEM_PROMPT"]},
            {"role": "user", "content": prompt},
        ],
    }

    try:
        timeout = aiohttp.ClientTimeout(total=cfg["LLM_TIMEOUT"])
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    print(f"❌ Ollama returned HTTP {resp.status}")
                    return None
                data = await resp.json()
                return data.get("message", {}).get("content", "").strip()
    except asyncio.TimeoutError:
        print(f"❌ LLM request timed out after {cfg['LLM_TIMEOUT']}s")
        return None
    except aiohttp.ClientConnectorError:
        print(f"❌ Cannot connect to Ollama at {cfg['LLM_BASE_URL']} — is it running?")
        return None
    except Exception as e:
        print(f"❌ LLM error: {e}")
        return None


# ============================================================
# BOT SETUP
# ============================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=cfg["COMMAND_PREFIX"], intents=intents)

# Tracks recent joins for chicken-out detection: {member_id: join_timestamp}
recent_joins: dict[int, discord.utils.datetime] = {}


# ============================================================
# SUGGESTION VIEW
# ============================================================

class SuggestionView(discord.ui.View):
    """Buttons for approving or rejecting a suggested message."""

    def __init__(self, content: str):
        super().__init__(timeout=None)
        self.content = content

    async def _is_authorized(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != cfg["AUTHORIZED_USER_ID"]:
            await interaction.response.send_message("❌ Not authorized.", ephemeral=True)
            return False
        return True

    async def _close(self, interaction: discord.Interaction, label: str):
        """Disable all buttons and stamp the decision on the message."""
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n{label} by {interaction.user.mention}",
            embed=None,
            view=None,
        )

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red, emoji="🗑️")
    async def reject(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not await self._is_authorized(interaction):
            return
        await self._close(interaction, "❌ Rejected")
        await interaction.response.defer()

    @discord.ui.button(label="✅ Default", style=discord.ButtonStyle.green, emoji="📌")
    async def accept_default(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not await self._is_authorized(interaction):
            return
        added = msgs.add(self.content, "default")
        await interaction.response.send_message(
            "✅ Added to default list!" if added else "⚠️ Already in default list.", ephemeral=True
        )
        await self._close(interaction, "✅ Accepted (Default)")

    @discord.ui.button(label="✅ Mention", style=discord.ButtonStyle.green, emoji="👋")
    async def accept_mention(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not await self._is_authorized(interaction):
            return
        added = msgs.add(self.content, "mention")
        await interaction.response.send_message(
            "✅ Added to mention list!" if added else "⚠️ Already in mention list.", ephemeral=True
        )
        await self._close(interaction, "✅ Accepted (Mention)")

    @discord.ui.button(label="✅ Both", style=discord.ButtonStyle.blurple, emoji="✨")
    async def accept_both(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not await self._is_authorized(interaction):
            return
        d = msgs.add(self.content, "default")
        m = msgs.add(self.content, "mention")
        if d and m:
            note = "✅ Added to both lists!"
        elif not d and not m:
            note = "⚠️ Already in both lists."
        else:
            note = f"✅ Added to {'default' if d else 'mention'} (already in the other)."
        await interaction.response.send_message(note, ephemeral=True)
        await self._close(interaction, "✅ Accepted (Both)")


# ============================================================
# HELPERS
# ============================================================

def build_suggestion_embed(
    suggester: discord.User,
    content: str,
    original_author: discord.User | None = None,
    jump_url: str | None = None,
) -> discord.Embed:
    embed = discord.Embed(
        title="New Message Suggestion",
        description=f"{suggester.mention} suggests adding this message:",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="📝 Content", value=content, inline=False)
    if original_author:
        embed.add_field(name="✍️ Original Author", value=original_author.mention, inline=True)
    if jump_url:
        embed.add_field(name="🔗 Jump", value=f"[View message]({jump_url})", inline=True)
    embed.set_footer(text=f"Suggested by {suggester.name} ({suggester.id})")
    return embed


async def post_suggestion(interaction: discord.Interaction, content: str,
                          author=None, jump_url=None):
    """Send a suggestion to the suggestion channel."""
    channel = bot.get_channel(cfg["SUGGESTION_CHANNEL_ID"])
    if not channel:
        await interaction.response.send_message("❌ Suggestion channel not found.", ephemeral=True)
        return

    embed = build_suggestion_embed(interaction.user, content, author, jump_url)
    view = SuggestionView(content)
    ping = f"<@&{cfg['SUGGESTION_PING_ROLE_ID']}>" if cfg.get("SUGGESTION_PING_ROLE_ID") else ""

    await channel.send(content=f"{ping} New suggestion!", embed=embed, view=view)
    await interaction.response.send_message("✅ Suggestion submitted!", ephemeral=True)


# ============================================================
# EVENTS
# ============================================================

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    print(f"   Default msgs : {len(msgs.default)}")
    print(f"   Mention msgs : {len(msgs.mention)}")
    print(f"   LLM          : {'✅ ' + cfg['LLM_MODEL'] + ' @ ' + cfg['LLM_BASE_URL'] if cfg['ENABLE_LLM'] else '❌ disabled'}")
    try:
        await bot.tree.sync()
        print("🔄 Slash commands synced.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    # --- Auto-thread channel ---
    if cfg["ENABLE_AUTO_THREAD"] and message.channel.id == cfg.get("AUTO_THREAD_CHANNEL_ID"):
        try:
            await message.add_reaction("✅")
            await message.add_reaction("❌")
            thread_name = (message.content[:97] + "...") if len(message.content) > 100 else message.content or "Discussion"
            thread = await message.create_thread(name=thread_name)
            ping = await thread.send(message.author.mention)
            await ping.delete()
        except discord.Forbidden:
            print("❌ Missing permissions in auto-thread channel.")
        except Exception as e:
            print(f"❌ Auto-thread error: {e}")

    # --- Random message ---
    if (cfg["ENABLE_RANDOM_MESSAGES"]
            and msgs.default
            and random.randint(1, cfg["RANDOM_MESSAGE_CHANCE"]) == 1):
        try:
            await message.channel.send(random.choice(msgs.default))
        except discord.Forbidden:
            pass

    # --- Mention response ---
    if cfg["ENABLE_MENTION_RESPONSES"] and bot.user.mentioned_in(message):
        mention_text = get_mention_text(message, bot.user)

        # If there's actual message content AND LLM is enabled → use LLM
        if mention_text and cfg["ENABLE_LLM"]:
            await handle_llm_mention(message, mention_text)

        # Otherwise fall back to mention_msgs list (bare ping, or LLM disabled)
        elif msgs.mention:
            try:
                await message.channel.send(random.choice(msgs.mention))
            except discord.Forbidden:
                pass

    await bot.process_commands(message)


async def handle_llm_mention(message: discord.Message, prompt: str):
    """Call the LLM and send its response. Falls back to mention_msgs on failure if configured."""
    try:
        if cfg["LLM_TYPING_INDICATOR"]:
            async with message.channel.typing():
                response = await query_llm(prompt)
        else:
            response = await query_llm(prompt)

        if response:
            # Discord has a 2000 char limit — truncate just in case
            if len(response) > 1990:
                response = response[:1990] + "…"
            await message.channel.send(response)
        else:
            raise ValueError("Empty response from LLM")

    except Exception as e:
        print(f"❌ LLM mention handler error: {e}")
        if cfg["LLM_FALLBACK_ON_ERROR"] and msgs.mention:
            try:
                await message.channel.send(random.choice(msgs.mention))
            except discord.Forbidden:
                pass


@bot.event
async def on_member_join(member: discord.Member):
    if cfg["ENABLE_CHICKEN_OUT"]:
        recent_joins[member.id] = discord.utils.utcnow()
    print(f"👋 {member} joined.")


@bot.event
async def on_member_remove(member: discord.Member):
    if not cfg["ENABLE_CHICKEN_OUT"] or member.id not in recent_joins:
        return

    joined_at = recent_joins.pop(member.id)
    elapsed = (discord.utils.utcnow() - joined_at).total_seconds()

    if elapsed <= cfg["CHICKEN_OUT_TIMEOUT"]:
        channel = bot.get_channel(cfg["CHICKEN_OUT_CHANNEL_ID"])
        if channel:
            try:
                await channel.send(f"{member.mention} chickened out")
                await channel.send(cfg["CHICKENED_OUT_MSG"])
                print(f"🐔 {member} chickened out after {int(elapsed)}s.")
            except discord.Forbidden:
                print("❌ No permission in chicken-out channel.")
        else:
            print(f"❌ Chicken-out channel not found (ID: {cfg['CHICKEN_OUT_CHANNEL_ID']}).")


@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    msg = f"❌ Command error: {error}"
    print(msg)
    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        pass


# ============================================================
# PREFIX COMMANDS
# ============================================================

@bot.command(name="hbm")
async def hbm(ctx: commands.Context):
    """Send misc/hbm.png."""
    path = BOT_DIR / "misc" / "hbm.png"
    if not path.exists():
        await ctx.send("❌ `misc/hbm.png` not found.")
        return
    try:
        await ctx.send(file=discord.File(str(path)))
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to send files here.")
    except Exception as e:
        await ctx.send("❌ Error sending image.")
        print(f"❌ hbm error: {e}")


# ============================================================
# SLASH COMMANDS
# ============================================================

@bot.tree.command(name="suggest-msg", description="Suggest a message for the bot to use")
@app_commands.describe(message="The message to suggest")
async def suggest_msg(interaction: discord.Interaction, message: str):
    if not cfg["ENABLE_SUGGESTIONS"]:
        await interaction.response.send_message("❌ Suggestions are disabled.", ephemeral=True)
        return
    await post_suggestion(interaction, message)


@bot.tree.command(name="reload-msgs", description="Reload message lists from disk (admin only)")
@app_commands.default_permissions(administrator=True)
async def reload_msgs(interaction: discord.Interaction):
    msgs.load()
    await interaction.response.send_message(
        f"✅ Reloaded — Default: {len(msgs.default)}, Mention: {len(msgs.mention)}",
        ephemeral=True,
    )


@bot.tree.command(name="llm-status", description="Check LLM connection status (admin only)")
@app_commands.default_permissions(administrator=True)
async def llm_status(interaction: discord.Interaction):
    """Ping Ollama and report status."""
    if not cfg["ENABLE_LLM"]:
        await interaction.response.send_message("❌ LLM is disabled in config.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{cfg['LLM_BASE_URL']}/api/tags") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m["name"] for m in data.get("models", [])]
                    model_list = ", ".join(models) if models else "none"
                    current = cfg["LLM_MODEL"]
                    is_available = any(current in m for m in models)
                    status = "✅" if is_available else "⚠️ model not found"
                    await interaction.followup.send(
                        f"**Ollama status:** ✅ Connected\n"
                        f"**Active model:** `{current}` {status}\n"
                        f"**Installed models:** `{model_list}`",
                        ephemeral=True,
                    )
                else:
                    await interaction.followup.send(f"⚠️ Ollama responded with HTTP {resp.status}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Cannot reach Ollama: `{e}`", ephemeral=True)


# ============================================================
# CONTEXT MENU COMMANDS
# ============================================================

@bot.tree.context_menu(name="Suggest message")
async def suggest_message_ctx(interaction: discord.Interaction, message: discord.Message):
    if not cfg["ENABLE_SUGGESTIONS"]:
        await interaction.response.send_message("❌ Suggestions are disabled.", ephemeral=True)
        return
    if not message.content:
        await interaction.response.send_message("❌ Message has no text content.", ephemeral=True)
        return
    await post_suggestion(interaction, message.content, message.author, message.jump_url)


@bot.tree.context_menu(name="Rape member")
async def rape_member_ctx(interaction: discord.Interaction, member: discord.Member):
    if not cfg["ENABLE_RAPE_COMMAND"]:
        await interaction.response.send_message("❌ This command is disabled.", ephemeral=True)
        return
    channel = bot.get_channel(cfg["RAPE_CHANNEL_ID"])
    if not channel:
        await interaction.response.send_message("❌ Target channel not found.", ephemeral=True)
        return
    try:
        await channel.send(f"{interaction.user.mention} raped {member.mention}")
        await interaction.response.send_message(f"✅ Done.", ephemeral=True)
    except Exception as e:
        print(f"❌ Rape command error: {e}")
        await interaction.response.send_message("❌ Error sending message.", ephemeral=True)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("🚀 Starting Bruh Bot...")
    print(f"   Prefix               : {cfg['COMMAND_PREFIX']}")
    print(f"   Random msg chance    : 1 in {cfg['RANDOM_MESSAGE_CHANCE']}")
    print(f"   Chicken-out timeout  : {cfg['CHICKEN_OUT_TIMEOUT']}s")
    print(f"   Random messages      : {'✅' if cfg['ENABLE_RANDOM_MESSAGES'] else '❌'}")
    print(f"   Mention responses    : {'✅' if cfg['ENABLE_MENTION_RESPONSES'] else '❌'}")
    print(f"   Auto-thread          : {'✅' if cfg['ENABLE_AUTO_THREAD'] else '❌'}")
    print(f"   Chicken out          : {'✅' if cfg['ENABLE_CHICKEN_OUT'] else '❌'}")
    print(f"   Suggestions          : {'✅' if cfg['ENABLE_SUGGESTIONS'] else '❌'}")
    print(f"   Rape command         : {'✅' if cfg['ENABLE_RAPE_COMMAND'] else '❌'}")
    print(f"   LLM                  : {'✅ ' + cfg['LLM_MODEL'] if cfg['ENABLE_LLM'] else '❌ disabled'}")

    try:
        bot.run(cfg["TOKEN"])
    except discord.LoginFailure:
        print("❌ Login failed — check your TOKEN in config.txt.")
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
