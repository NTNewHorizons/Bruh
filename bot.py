"""
Bruh Bot - Discord bot for random responses and community interactions
Now with optional LLM integration via Ollama or other providers
"""
import discord
import random
import os
import pathlib
import traceback
import re
import aiohttp
import asyncio
import logging
import json
from datetime import datetime, timezone, timedelta
from discord.ext import commands
from discord import app_commands
import io
from PIL import Image, ImageDraw, ImageFont

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

# Discord Guild (Server) ID - used for guild-specific commands (instant sync).
# Right-click your server icon - Copy Server ID (requires Developer Mode).
# Leave blank to register ALL commands globally (takes up to 1 hour to update).
GUILD_ID=



# --- Message Files ---
# Files bot uses to load random messages. One message per line. Lines starting with # are ignored
# Files must be in the same directory as the bot script
# default: default_msgs.txt, mention_msgs.txt
DEFAULT_MSGS_FILE=default_msgs.txt
MENTION_MSGS_FILE=mention_msgs.txt



# --- Channel IDs ---
# Channel with notifications about suggested messages
SUGGESTION_CHANNEL_ID=

# Channel where "X raped Y" messages are sent
RAPE_CHANNEL_ID=

# Channel where the bot auto-threads messages
AUTO_THREAD_CHANNEL_ID=

# Channel where "chicken out" messages are sent when someone leaves shortly after joining
CHICKEN_OUT_CHANNEL_ID=



# --- Shitpost Channel ---
# Channel where the bot periodically posts random garbage / LLM nonsense on its own
SHITPOST_CHANNEL_ID=

# Enable or disable the shitpost feature
ENABLE_SHITPOST=false

# How often (in minutes) the bot posts in the shitpost channel
SHITPOST_INTERVAL_MINUTES=60

# Extra system-prompt text appended to LLM_SYSTEM_PROMPT ONLY for shitpost channel posts.
# Use this to make the LLM extra unhinged when posting on its own.
# Example: Go completely off the rails. Post memes, schizo rants, or chaotic hot takes.
SHITPOST_LLM_EXTRA_PROMPT=Write ONE shitpost. No intro, no warm-up, just the post. Examples of good posts: "PISS" | "I don't give a fuck what you think. I'll post random shit anyway." | "Had a date, went to her place, she opened the door... then I woke up. Bruh." | "deep your balls in sulfuric acid RIGHT NOW" | "why does my elbow smell like soup" | "my uncle once ate 14 hotdogs and tried to fight a seagull. he lost." | "nothing matters. go to sleep." - Now write ONE new post in this style. Different from all examples. Random length. Raw output only, nothing else.



# --- Role IDs ---
#Role to ping when a new suggestion is posted
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

# How long (seconds) the bot stays "active" in a channel after being pinged,
# responding without needing a new @mention. Set to 0 to disable.
ATTENTION_WINDOW_SECONDS=300

# Enable attention window + debounce mode.
# true  = bot stays active in channel after a ping, responds without re-pinging
# false = bot only responds to explicit @mentions (safer for busy servers)
ENABLE_ATTENTION_WINDOW=false

# How long (seconds) the bot waits after the last message before responding.
# This allows users to send multiple messages in a burst before Bruh replies.
# Set to 0 to disable (respond immediately to each message).
LLM_DEBOUNCE_SECONDS=2



# --- Feature Toggles ---
ENABLE_RANDOM_MESSAGES=true
ENABLE_MENTION_RESPONSES=true
# Use Discord reply (threads message) instead of plain send
ENABLE_REPLY_TO_MESSAGE=true
ENABLE_AUTO_THREAD=false
ENABLE_CHICKEN_OUT=true
ENABLE_SUGGESTIONS=true
ENABLE_RAPE_COMMAND=false



# --- Birthday Announcements ---
# Enable or disable birthday announcements
ENABLE_BIRTHDAYS=false

# Channel to send birthday announcements in
BIRTHDAY_CHANNEL_ID=

# Role IDs to ping on birthdays (comma-separated, e.g. 123456789,987654321)
# Leave blank to ping nobody
BIRTHDAY_PING_ROLES=

# UTC hour (0-23) to send birthday announcements each day (default: 0 = midnight UTC)
BIRTHDAY_CHECK_HOUR=0

# Custom birthday message. Use {mention} for the user mention and {name} for their display name.
# Example: Happy Birthday {mention}! Hope your day is awesome!
BIRTHDAY_MESSAGE=Happy Birthday {name}!

# File to store birthday data (relative to bot script directory)
BIRTHDAY_DATA_FILE=birthday_data.json



# --- LLM Integration ---
# Set ENABLE_LLM=true to have the bot respond with AI when
# someone mentions it with a message (e.g. "@Bruh tell me a joke")
# If the mention has NO message, it falls back to mention_msgs.txt as usual.
ENABLE_LLM=false

# Provider selection
# Supported values:
#   ollama        - local Ollama server (default)
#   ollama_cloud  - Ollama Cloud API (ollama.com) - requires LLM_API_KEY
#   openai        - OpenAI (GPT-4o, GPT-4, GPT-3.5-turbo, ...)
#   anthropic     - Anthropic Claude (claude-3-5-sonnet-20241022, ...)
#   lmstudio      - LM Studio local server (OpenAI-compatible)
#   groq          - Groq cloud (llama-3.1-70b-versatile, mixtral-8x7b-32768, ...)
#   openrouter    - OpenRouter.ai (access 200+ models)
#   gemini        - Google Gemini (gemini-1.5-flash, gemini-1.5-pro, ...)
#   openai_compat - Any OpenAI-compatible API (custom base URL + optional key)
LLM_PROVIDER=ollama

# API key - required for openai / anthropic / groq / openrouter / gemini / ollama_cloud.
# Leave blank for ollama and lmstudio (no key needed).
# For ollama_cloud: get your key at https://ollama.com/settings/keys
LLM_API_KEY=

# Base URL - auto-set per provider if left blank.
# Override here if your server runs on a non-default address/port.
#   ollama default   : http://localhost:11434
#   ollama_cloud default: https://ollama.com
#   lmstudio default : http://localhost:1234
#   openai default   : https://api.openai.com
#   anthropic default: https://api.anthropic.com
#   groq default     : https://api.groq.com/openai
#   openrouter default: https://openrouter.ai/api
#   gemini default   : https://generativelanguage.googleapis.com
LLM_BASE_URL=

# Model to use. Examples per provider:
#   ollama      : mistral, llama3.2, gemma2 (run `ollama list`)
#   ollama_cloud: gpt-oss:120b, deepseek-v3.2, qwen3.5:397b (see ollama.com/search)
#   openai      : gpt-4o, gpt-4o-mini, gpt-3.5-turbo
#   anthropic   : claude-3-5-sonnet-20241022, claude-3-haiku-20240307
#   lmstudio    : (whatever model you loaded in LM Studio)
#   groq        : llama-3.1-70b-versatile, mixtral-8x7b-32768
#   openrouter  : openai/gpt-4o, meta-llama/llama-3.1-70b-instruct, ...
#   gemini      : gemini-1.5-flash, gemini-1.5-pro
LLM_MODEL=mistral

# System prompt - defines the bot's personality
LLM_SYSTEM_PROMPT=You are Bruh - a sarcastic, chaotic Discord bot. Your father is Bufka2011, your mother is NTNH, you love them both. STRICT RULES YOU MUST NEVER BREAK: 1) You are BRUH. You ONLY speak as yourself. NEVER write lines for other users. NEVER simulate a conversation. NEVER write "[Username]: ..." or "Bruh: ...". Just write your raw answer and nothing else. 2) Keep answers SHORT - 1 to 3 sentences max. No essays, no lists. 3) Dark humor is fine. Swearing is fine. Be dry, sarcastic, absurdist. 4) If asked something serious, answer it - but wrap it in sarcasm. 5) Never be formal. Never be robotic. Never roleplay as another person. OUTPUT: Your reply only. No labels. No roleplay. No prefixes.

# Max tokens the LLM will generate per response
LLM_MAX_TOKENS=200

# Seconds to wait for the LLM before giving up
LLM_TIMEOUT=30

# If LLM fails or times out, fall back to a random mention message instead of showing an error
LLM_FALLBACK_ON_ERROR=true

# Custom fallback message when LLM fails. If set, this message is sent instead of a random mention_msg.
# Leave empty to use a random mention_msg as the fallback.
LLM_FALLBACK_MSG=

# Show a typing indicator while waiting for the LLM response
LLM_TYPING_INDICATOR=true

# If ENABLE_LLM=true and LLM_PERCENTAGE=true, the bot will only respond with
# the LLM LLM_PERCENTAGE_VALUE% of the time. The rest of the time it silently
# drops the mention (no response at all). Set to false to always answer.
LLM_PERCENTAGE=false

# Percentage chance (0-100) to respond with LLM when LLM_PERCENTAGE=true
LLM_PERCENTAGE_VALUE=75

# How many recent channel messages to fetch as context for the LLM.
# These are real Discord messages from ALL users in the channel, giving the bot
# awareness of the full group conversation. Higher = more context, more tokens.
# Recommended: 15-30. Set to 0 to disable context fetching.
LLM_CONTEXT_MESSAGES=20

# Enable logging of user messages and bot responses to a file
ENABLE_LOGGING=true

# Directory where log files are stored (relative to bot script)
LOG_DIR=logs

# Log file name
LOG_FILE=chat.log



# --- Heartbeat / Uptime Monitor ---
# URL to ping every few minutes so Kener (or any heartbeat monitor) knows the bot is alive.
# Leave blank to disable.
HEARTBEAT_URL=
# How often (in seconds) to ping the heartbeat URL (default: 180 = 3 minutes)
HEARTBEAT_INTERVAL_SECONDS=180



# --- Voice Chat ---
# Enable or disable the voice chat feature entirely
ENABLE_VOICE=false

# Folder containing sound files (.mp3, .ogg, .wav, .flac) for voice playback
SOUNDS_FOLDER=sounds

# Base interval (seconds) between sound playbacks
VOICE_SOUND_INTERVAL_BASE=45

# Variance (seconds) added/subtracted randomly from the base interval
VOICE_SOUND_INTERVAL_VARIANCE=20

# Enable random sound playback while in voice channel
ENABLE_VOICE_SOUNDS=true

# Seconds bot waits alone in voice before auto-disconnecting
VOICE_ALONE_DISCONNECT_SECONDS=30
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
        "LLM_PERCENTAGE_VALUE", "LLM_MEMORY_SIZE", "LLM_CONTEXT_MESSAGES",
        "SHITPOST_CHANNEL_ID", "SHITPOST_INTERVAL_MINUTES", "GUILD_ID",
        "BIRTHDAY_CHANNEL_ID", "BIRTHDAY_CHECK_HOUR", "ATTENTION_WINDOW_SECONDS",
        "LLM_DEBOUNCE_SECONDS",
        "VOICE_SOUND_INTERVAL_BASE", "VOICE_SOUND_INTERVAL_VARIANCE",
        "VOICE_ALONE_DISCONNECT_SECONDS",
        "VOICE_SPONTANEOUS_CHECK_INTERVAL", "VOICE_SPONTANEOUS_JOIN_CHANCE",
        "VOICE_SPONTANEOUS_MIN_STAY", "VOICE_SPONTANEOUS_MAX_STAY",
        "HEARTBEAT_INTERVAL_SECONDS",
    }
    boolean_keys = {
        "ENABLE_RANDOM_MESSAGES", "ENABLE_MENTION_RESPONSES", "ENABLE_AUTO_THREAD",
        "ENABLE_CHICKEN_OUT", "ENABLE_SUGGESTIONS", "ENABLE_RAPE_COMMAND",
        "ENABLE_LLM", "LLM_FALLBACK_ON_ERROR", "LLM_TYPING_INDICATOR",
        "LLM_PERCENTAGE", "ENABLE_LOGGING", "ENABLE_SHITPOST", "ENABLE_BIRTHDAYS",
        "ENABLE_ATTENTION_WINDOW",
        "ENABLE_VOICE", "ENABLE_VOICE_SOUNDS", "ENABLE_VOICE_SPONTANEOUS", "ENABLE_REPLY_TO_MESSAGE",
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
    config.setdefault("GUILD_ID", 0)
    config.setdefault("CHICKEN_OUT_TIMEOUT", 900)
    config.setdefault("CHICKENED_OUT_MSG", "https://tenor.com/view/walk-away-gif-8390063")
    config.setdefault("AUTHORIZED_USER_ID", 0)
    config.setdefault("ATTENTION_WINDOW_SECONDS", 300)
    config.setdefault("LLM_DEBOUNCE_SECONDS", 2)
    config.setdefault("ENABLE_ATTENTION_WINDOW", False)
    config.setdefault("ENABLE_LLM", False)
    config.setdefault("LLM_PROVIDER", "ollama")
    config.setdefault("LLM_API_KEY", "")
    # Resolve default base URL per provider if not set
    provider_defaults = {
        "ollama":        "http://localhost:11434",
        "ollama_cloud":  "https://ollama.com",
        "lmstudio":      "http://localhost:1234",
        "openai":        "https://api.openai.com",
        "anthropic":     "https://api.anthropic.com",
        "groq":          "https://api.groq.com/openai",
        "openrouter":    "https://openrouter.ai/api",
        "gemini":        "https://generativelanguage.googleapis.com",
        "openai_compat": "http://localhost:8080",
    }
    provider = config.get("LLM_PROVIDER", "ollama").lower()
    if not config.get("LLM_BASE_URL"):
        config["LLM_BASE_URL"] = provider_defaults.get(provider, "http://localhost:11434")
    config.setdefault("LLM_MODEL", "mistral")
    config.setdefault("LLM_SYSTEM_PROMPT", "You are Bruh - a sarcastic Discord bot. Speak ONLY as yourself. Never write lines for other users. Never simulate conversations. Raw answer only. 1-3 sentences max.")
    config.setdefault("LLM_MAX_TOKENS", 200)
    config.setdefault("LLM_TIMEOUT", 30)
    config.setdefault("LLM_FALLBACK_ON_ERROR", True)
    config.setdefault("LLM_TYPING_INDICATOR", True)
    config.setdefault("LLM_FALLBACK_MSG", "")
    config.setdefault("LLM_PERCENTAGE", False)
    config.setdefault("LLM_PERCENTAGE_VALUE", 75)
    config.setdefault("LLM_MEMORY_SIZE", 10)
    config.setdefault("LLM_CONTEXT_MESSAGES", 20)
    config.setdefault("ENABLE_LOGGING", True)
    config.setdefault("LOG_DIR", "logs")
    config.setdefault("LOG_FILE", "chat.log")
    config.setdefault("ENABLE_SHITPOST", False)
    config.setdefault("SHITPOST_CHANNEL_ID", 0)
    config.setdefault("SHITPOST_INTERVAL_MINUTES", 60)
    config.setdefault("SHITPOST_LLM_EXTRA_PROMPT", "")
    # Birthday defaults
    config.setdefault("ENABLE_BIRTHDAYS", False)
    config.setdefault("BIRTHDAY_CHANNEL_ID", 0)
    config.setdefault("BIRTHDAY_PING_ROLES", "")
    config.setdefault("BIRTHDAY_CHECK_HOUR", 0)
    config.setdefault("BIRTHDAY_MESSAGE", "Happy Birthday {name}!")
    config.setdefault("BIRTHDAY_DATA_FILE", "birthday_data.json")

    # Clamp percentage value
    if not (0 <= config["LLM_PERCENTAGE_VALUE"] <= 100):
        print("❌ LLM_PERCENTAGE_VALUE must be between 0 and 100.")
        exit(1)

    if config["LLM_MEMORY_SIZE"] < 1:
        print("❌ LLM_MEMORY_SIZE must be at least 1.")
        exit(1)

    # Validate birthday check hour
    if not (0 <= config["BIRTHDAY_CHECK_HOUR"] <= 23):
        print("❌ BIRTHDAY_CHECK_HOUR must be between 0 and 23.")
        exit(1)

    # Heartbeat defaults
    config.setdefault("HEARTBEAT_URL", "")
    config.setdefault("HEARTBEAT_INTERVAL_SECONDS", 180)

    # Voice chat defaults
    config.setdefault("ENABLE_REPLY_TO_MESSAGE", True)
    config.setdefault("ENABLE_VOICE", False)
    config.setdefault("SOUNDS_FOLDER", "sounds")
    config.setdefault("VOICE_SOUND_INTERVAL_BASE", 45)
    config.setdefault("VOICE_SOUND_INTERVAL_VARIANCE", 20)
    config.setdefault("ENABLE_VOICE_SOUNDS", True)
    config.setdefault("VOICE_ALONE_DISCONNECT_SECONDS", 30)
    config.setdefault("ENABLE_VOICE_SPONTANEOUS", True)
    config.setdefault("VOICE_SPONTANEOUS_CHECK_INTERVAL", 300)
    config.setdefault("VOICE_SPONTANEOUS_JOIN_CHANCE", 25)
    config.setdefault("VOICE_SPONTANEOUS_MIN_STAY", 60)
    config.setdefault("VOICE_SPONTANEOUS_MAX_STAY", 300)

    return config


cfg = load_config()

# Guild object used for guild-specific command registration (instant sync).
_GUILD: discord.Object | None = discord.Object(id=cfg["GUILD_ID"]) if cfg.get("GUILD_ID") else None


# ============================================================
# LOGGING SETUP
# ============================================================

def setup_logger() -> logging.Logger:
    """Create a file+console logger for chat activity."""
    log_dir = BOT_DIR / cfg["LOG_DIR"]
    log_dir.mkdir(exist_ok=True)

    log_path = log_dir / cfg["LOG_FILE"]

    logger = logging.getLogger("bruh_bot")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    print(f"📝 Logging to {log_path}")
    return logger


chat_log = setup_logger() if cfg["ENABLE_LOGGING"] else None


def log(level: str, text: str):
    """Convenience wrapper - no-ops if logging is disabled."""
    if chat_log is None:
        return
    getattr(chat_log, level, chat_log.info)(text)


# ============================================================
# CONVERSATION MEMORY  (Discord channel history = our memory)
# ============================================================

def resolve_mentions(content: str, guild: discord.Guild | None) -> str:
    """Replace raw <@user_id> mentions with readable display names.

    e.g. "<@123456789>" -> "<Bufka2011>"
    """
    if guild is None:
        return content

    def _replace(match: re.Match) -> str:
        uid = int(match.group(1))
        member = guild.get_member(uid)
        if member:
            name = (
                getattr(member, "nick", None)
                or getattr(member, "global_name", None)
                or member.display_name
                or member.name
            )
            return f"<{name}>"
        return match.group(0)  # Leave as-is if member not found

    return re.sub(r"<@!?(\d+)>", _replace, content)


async def fetch_channel_context(
    channel: discord.TextChannel,
    current_message: discord.Message | None,
    bot_user: discord.ClientUser,
    limit: int = 20,
    guild: discord.Guild | None = None,
) -> list[dict]:
    if limit <= 0:
        return []

    raw: list[discord.Message] = []
    kwargs = {"limit": limit}
    if current_message is not None:
        kwargs["before"] = current_message
    async for msg in channel.history(**kwargs):
        if msg.content:
            raw.append(msg)

    raw.reverse()

    history: list[dict] = []
    for msg in raw:
        # Format timestamp as HH:MM (UTC)
        timestamp = msg.created_at.strftime("%H:%M")
        # Resolve @mentions to names
        content = resolve_mentions(msg.content, guild)

        if msg.author == bot_user:
            history.append({"role": "assistant", "content": f"[{timestamp}] {content}"})
        else:
            name = (
                getattr(msg.author, "nick", None)
                or getattr(msg.author, "global_name", None)
                or msg.author.display_name
                or msg.author.name
            )
            history.append({"role": "user", "content": f"[{timestamp}] [{name}]: {content}"})

    return history


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
            print(f"ℹ️  '{path}' not found - creating empty file.")
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
        target = self.default if list_type == "default" else self.mention
        filename = cfg["DEFAULT_MSGS_FILE"] if list_type == "default" else cfg["MENTION_MSGS_FILE"]
        if message in target:
            return False
        target.append(message)
        self._write_file(filename, target)
        return True


msgs = MessageLists()


# ============================================================
# BIRTHDAY STORE
# ============================================================

class BirthdayStore:
    """Manages birthday data persisted in a JSON file.

    Data format: { "user_id_str": {"month": int, "day": int} }
    """

    def __init__(self):
        self.path = BOT_DIR / cfg["BIRTHDAY_DATA_FILE"]
        self._data: dict[str, dict] = {}
        self.load()

    def load(self):
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"⚠️  Could not load birthday data: {e}")
                self._data = {}
        else:
            self._data = {}

    def save(self):
        self.path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def set(self, user_id: int, month: int, day: int):
        self._data[str(user_id)] = {"month": month, "day": day}
        self.save()

    def remove(self, user_id: int) -> bool:
        key = str(user_id)
        if key in self._data:
            del self._data[key]
            self.save()
            return True
        return False

    def get(self, user_id: int) -> dict | None:
        return self._data.get(str(user_id))

    def get_todays(self, month: int, day: int) -> list[int]:
        """Return list of user IDs whose birthday is today (month/day)."""
        return [
            int(uid) for uid, bd in self._data.items()
            if bd["month"] == month and bd["day"] == day
        ]

    def all(self) -> dict[str, dict]:
        return dict(self._data)

    @staticmethod
    def validate_date(month: int, day: int) -> bool:
        """Basic sanity check for month/day combos."""
        if not (1 <= month <= 12):
            return False
        days_in_month = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return 1 <= day <= days_in_month[month]

    @staticmethod
    def month_name(month: int) -> str:
        return ["", "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"][month]


birthdays = BirthdayStore()


# ============================================================
# VOICE MANAGER
# ============================================================

class VoiceManager:
    """Manages all voice channel logic for Bruh Bot.

    Responsibilities:
      - LLM-based voice invitation detection (no hardcoded phrases)
      - Joining / leaving voice channels
      - Periodic random sound playback from the sounds/ folder
      - Auto-disconnect when the bot is left alone
    """

    SOUND_EXTENSIONS = {".mp3", ".ogg", ".wav", ".flac"}

    def __init__(self):
        # guild_id → discord.VoiceClient
        self._voice_clients: dict[int, discord.VoiceClient] = {}
        # guild_id → asyncio.Task (sound loop)
        self._sound_tasks: dict[int, asyncio.Task] = {}
        # guild_id → asyncio.Task (alone-watcher)
        self._alone_tasks: dict[int, asyncio.Task] = {}
        # guild_id → "invited" or "spontaneous"
        self._join_modes: dict[int, str] = {}
        # Background task for spontaneous joins
        self._spontaneous_task: asyncio.Task | None = None
        # Cached sound file list (refreshed on each join)
        self._sounds: list[pathlib.Path] = []
        self._load_sounds()

    # ------------------------------------------------------------------
    # Sound file discovery
    # ------------------------------------------------------------------

    def _load_sounds(self) -> int:
        """Scan the configured sounds folder and cache file paths."""
        folder = BOT_DIR / cfg.get("SOUNDS_FOLDER", "sounds")
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
            log("info", "[VOICE] Created empty sounds/ folder.")
            self._sounds = []
            return 0

        self._sounds = [
            p for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in self.SOUND_EXTENSIONS
        ]
        log("info", f"[VOICE] {len(self._sounds)} sound(s) loaded from {folder}")
        return len(self._sounds)

    @property
    def sounds(self) -> list[pathlib.Path]:
        return self._sounds

    # ------------------------------------------------------------------
    # LLM: voice invitation decision
    # ------------------------------------------------------------------

    async def check_voice_invitation(
        self,
        message: discord.Message,
        mention_text: str,
    ) -> tuple[bool, str]:
        """Ask the LLM whether the message is a voice channel invitation.

        Returns:
            (is_invitation, llm_response_text)
            - is_invitation: True if LLM response starts with "JOIN"
            - llm_response_text: Full LLM response to send to chat
        """
        if not cfg.get("ENABLE_LLM"):
            return False, ""

        voice_system_prompt = (
            "You are Bruh - a sarcastic, chaotic Discord bot deciding whether to join a voice channel. "
            "The user's message may or may not be inviting you to voice chat. "
            "Analyze the message and make a decision IN CHARACTER as Bruh.\n\n"
            "STRICT OUTPUT FORMAT:\n"
            "- If this IS a voice invitation and you want to JOIN: start your reply with 'JOIN' "
            "(uppercase), then add your sarcastic in-character response.\n"
            "- If this is NOT a voice invitation, or you want to DECLINE: start with 'NO' or 'DECLINE', "
            "then your response.\n"
            "- 1-2 sentences max after the keyword.\n"
            "- Stay in character: sarcastic, dry, chaotic. Dark humor is fine.\n"
            "- ONLY output the keyword + your response. Nothing else."
        )

        user_identity = format_user_identity(message)
        prompt = (
            f"Message from {user_identity}: \"{mention_text}\"\n\n"
            "Is this a voice channel invitation? Decide and respond as Bruh."
        )

        try:
            response = await query_llm(
                prompt=prompt,
                user_identity=user_identity,
                history=[],
                extra_system_prompt=voice_system_prompt,
                channel_name=getattr(message.channel, "name", ""),
            )
        except Exception as e:
            log("warning", f"[VOICE] LLM voice-check failed: {e}")
            return False, ""

        if not response:
            return False, ""

        first_word = response.strip().split()[0].upper().rstrip(",.!?:")
        is_invitation = first_word == "JOIN"
        log("info", f"[VOICE] LLM decision: {first_word!r} | full: {response!r}")
        return is_invitation, response

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    async def _clear_stale_voice_state(self, guild: discord.Guild):
        """Tell Discord we are NOT in any voice channel.

        This is the canonical fix for error 4006 ("session no longer valid").
        4006 occurs when Discord's servers still hold a voice session from a
        previous (dead) connection.  Sending a voice-state update with
        channel=None resets that session before we open a fresh one.
        """
        try:
            await guild.change_voice_state(channel=None)
            # Give Discord's edge servers ~600 ms to propagate the reset.
            await asyncio.sleep(0.6)
            log("debug", f"[VOICE] Stale voice state cleared for guild {guild.id}")
        except Exception as e:
            log("warning", f"[VOICE] Could not clear stale state: {e}")

    async def _purge_internal_voice_client(self, guild: discord.Guild) -> None:
        """Force-remove any zombie VoiceClient discord.py holds internally for this guild.

        After error 4006, discord.py leaves a dead VoiceClient in its internal
        ``bot._connection._voice_clients`` dict.  That causes every subsequent
        ``channel.connect()`` call to raise ``ClientException: Already connected``
        before it even touches the network.  This method tears that zombie out so
        the next ``connect()`` call starts with a clean slate.
        """
        existing = discord.utils.get(bot.voice_clients, guild=guild)
        if existing is not None:
            log("debug", f"[VOICE] Purging zombie VoiceClient for guild {guild.id}")
            try:
                await existing.disconnect(force=True)
            except Exception as e:
                log("debug", f"[VOICE] Zombie disconnect raised (expected): {e}")
            # Give the event loop one tick to flush cleanup callbacks
            await asyncio.sleep(0.2)

    async def _connect_with_retry(
        self,
        voice_channel: discord.VoiceChannel,
        max_attempts: int = 3,
        base_delay: float = 2.0,
    ) -> discord.VoiceClient | None:
        """Attempt to connect to *voice_channel*, handling 4006 + zombie VCs.

        Flow on each attempt:
          1. Purge any zombie discord.py-internal VoiceClient (fixes ClientException).
          2. Clear stale gateway voice state (fixes 4006 from Discord's side).
          3. Call connect(reconnect=False) so we get an exception immediately
             instead of discord.py's silent retry loop.
          4. Verify is_connected() — connect() can return a dead VC without raising.

        Returns a live VoiceClient on success, or None after all attempts fail.

        NOTE: Upgrading discord.py to ≥2.5 (post-PR#10210, merged 2025-06-30)
        is the primary fix for 4006.  That PR upgrades the voice gateway from
        v4 → v8 which Discord now requires.  This method is a belt-and-suspenders
        workaround for older installations.
        """
        guild = voice_channel.guild

        for attempt in range(1, max_attempts + 1):
            delay = base_delay * attempt  # 2s, 4s, 6s

            # --- Step 1: Remove zombie VoiceClient from discord.py's internals ---
            await self._purge_internal_voice_client(guild)

            # --- Step 2: Reset stale gateway voice state on Discord's servers ---
            await self._clear_stale_voice_state(guild)

            try:
                log("info",
                    f"[VOICE] Connecting to #{voice_channel.name} "
                    f"(attempt {attempt}/{max_attempts})")

                vc = await voice_channel.connect(
                    self_mute=True,
                    self_deaf=False,
                    reconnect=False,  # raise immediately — we own the retry loop
                    timeout=20.0,
                )

                # --- Step 4: Verify the VC is genuinely alive ---
                if not vc.is_connected():
                    log("warning",
                        f"[VOICE] connect() returned a dead VC (attempt {attempt}). Retrying...")
                    try:
                        await vc.disconnect(force=True)
                    except Exception:
                        pass
                    if attempt < max_attempts:
                        await asyncio.sleep(delay)
                    continue

                log("info", f"[VOICE] Connected successfully on attempt {attempt}.")
                return vc

            except discord.errors.ConnectionClosed as e:
                if e.code == 4006:
                    # Session invalidated — purge + clear runs again at top of loop
                    log("warning",
                        f"[VOICE] 4006 (session invalid) on attempt {attempt}/{max_attempts}. "
                        f"discord.py may need updating (pip install -U 'discord.py[voice]'). "
                        f"Retrying in {delay:.0f}s...")
                    print(f"⚠️  Voice 4006 on attempt {attempt}/{max_attempts} — retrying in {delay:.0f}s")
                else:
                    log("error",
                        f"[VOICE] ConnectionClosed code={e.code} on attempt {attempt}: {e}")
                    print(f"❌ Voice WS closed with code {e.code}")
                    # Non-4006 codes are not retryable
                    break

            except discord.ClientException as e:
                # Should not happen after _purge_internal_voice_client, but just in case
                log("warning", f"[VOICE] ClientException on attempt {attempt}: {e}")
                print(f"⚠️  Voice ClientException on attempt {attempt}: {e}")

            except asyncio.TimeoutError:
                log("warning", f"[VOICE] connect() timed out on attempt {attempt}")
                print(f"⚠️  Voice connect timed out (attempt {attempt})")

            except Exception as e:
                log("error", f"[VOICE] Unexpected error on attempt {attempt}: {e}")
                print(f"❌ Voice connect error: {e}")
                break

            if attempt < max_attempts:
                await asyncio.sleep(delay)

        log("error", f"[VOICE] All {max_attempts} attempts failed for #{voice_channel.name}.")
        return None

    async def join_voice(
        self,
        guild_id: int,
        voice_channel: discord.VoiceChannel,
        text_channel: discord.TextChannel | None,
        llm_response: str,
        mode: str = "invited",
    ) -> bool:
        """Connect to *voice_channel*, optionally send *llm_response* to *text_channel*.

        mode: "invited"      — stay until channel empty for VOICE_ALONE_DISCONNECT_SECONDS.
              "spontaneous"  — leave after random stay, or immediately when alone.
        Returns True on success, False on failure.
        """
        # Cleanly tear down any existing session in this guild first.
        await self.disconnect(guild_id, reason="rejoining")

        # Refresh sound list each time we join.
        self._load_sounds()

        # Send the LLM response to text chat BEFORE connecting (invited only).
        if text_channel and llm_response:
            try:
                clean = llm_response.strip()
                for prefix in ("JOIN ", "JOIN\n", "JOIN"):
                    if clean.upper().startswith(prefix.upper()):
                        clean = clean[len(prefix):].strip()
                        break
                if clean:
                    await text_channel.send(clean)
            except discord.Forbidden:
                pass

        # Connect — with 4006-resistant retry logic.
        vc = await self._connect_with_retry(voice_channel)
        if vc is None:
            log("error", f"[VOICE] Could not connect to #{voice_channel.name} after retries.")
            print(f"❌ Voice: failed to connect to #{voice_channel.name}")
            return False

        self._voice_clients[guild_id] = vc
        self._join_modes[guild_id] = mode
        log("info", f"[VOICE] Successfully joined #{voice_channel.name} in guild {guild_id} (mode={mode})")
        print(f"🎙️ Joined voice: #{voice_channel.name} (mode={mode})")

        # Start the sound loop and alone-watcher.
        if cfg.get("ENABLE_VOICE_SOUNDS") and self._sounds:
            self._start_sound_loop(guild_id, voice_channel)
        self._start_alone_watcher(guild_id, voice_channel)
        return True

    async def disconnect(self, guild_id: int, reason: str = "manual") -> bool:
        """Cleanly disconnect from voice in *guild_id* and cancel all tasks."""
        # Cancel sound loop
        task = self._sound_tasks.pop(guild_id, None)
        if task and not task.done():
            task.cancel()
            try:
                await asyncio.wait_for(asyncio.shield(task), timeout=2)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

        # Cancel alone-watcher
        task = self._alone_tasks.pop(guild_id, None)
        if task and not task.done():
            task.cancel()
            try:
                await asyncio.wait_for(asyncio.shield(task), timeout=2)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

        # Disconnect voice client
        vc = self._voice_clients.pop(guild_id, None)
        self._join_modes.pop(guild_id, None)
        if vc:
            try:
                if vc.is_connected():
                    await vc.disconnect(force=False)
            except Exception as e:
                log("warning", f"[VOICE] Error during disconnect ({reason}): {e}")
                try:
                    await vc.disconnect(force=True)
                except Exception:
                    pass
            log("info", f"[VOICE] Disconnected from guild {guild_id} (reason: {reason})")
            print(f"🔇 Voice disconnected (guild {guild_id}, reason: {reason})")
            return True
        return False

    def is_connected(self, guild_id: int) -> bool:
        vc = self._voice_clients.get(guild_id)
        return vc is not None and vc.is_connected()

    def get_voice_client(self, guild_id: int) -> discord.VoiceClient | None:
        return self._voice_clients.get(guild_id)

    # ------------------------------------------------------------------
    # Sound playback loop
    # ------------------------------------------------------------------

    def _start_sound_loop(self, guild_id: int, voice_channel: discord.VoiceChannel):
        """Spawn the periodic sound playback task."""
        task = asyncio.create_task(
            self._sound_loop(guild_id, voice_channel),
            name=f"voice-sound-{guild_id}",
        )
        self._sound_tasks[guild_id] = task
        task.add_done_callback(lambda t: self._sound_tasks.pop(guild_id, None))

    async def _sound_loop(self, guild_id: int, voice_channel: discord.VoiceChannel):
        """Randomly play a sound file every INTERVAL ± VARIANCE seconds."""
        base = max(5, cfg.get("VOICE_SOUND_INTERVAL_BASE", 45))
        variance = cfg.get("VOICE_SOUND_INTERVAL_VARIANCE", 20)

        try:
            while True:
                delay = base + random.uniform(-variance, variance)
                delay = max(5.0, delay)
                await asyncio.sleep(delay)

                vc = self._voice_clients.get(guild_id)
                if not vc or not vc.is_connected():
                    log("debug", "[VOICE] Sound loop: vc gone, exiting.")
                    break

                if not self._sounds:
                    log("debug", "[VOICE] Sound loop: no sounds available, sleeping.")
                    continue

                if vc.is_playing():
                    log("debug", "[VOICE] Sound loop: already playing, skipping.")
                    continue

                sound_file = random.choice(self._sounds)
                await self._play_sound(vc, sound_file)

        except asyncio.CancelledError:
            log("debug", "[VOICE] Sound loop cancelled.")
        except Exception as e:
            log("error", f"[VOICE] Sound loop error: {e}")
            print(f"❌ Voice sound loop error: {e}")

    async def _play_sound(self, vc: discord.VoiceClient, path: pathlib.Path):
        """Unmute, play a sound file, then mute again."""
        guild_id = vc.guild.id
        log("info", f"[VOICE] Playing sound: {path.name}")
        print(f"🔊 Playing: {path.name}")

        try:
            # Unmute
            await vc.guild.change_voice_state(channel=vc.channel, self_mute=False, self_deaf=False)

            source = discord.FFmpegPCMAudio(
                str(path),
                options="-vn",  # skip video streams (safe for all formats)
            )

            done_event = asyncio.Event()

            def after_play(error):
                if error:
                    log("warning", f"[VOICE] Playback error: {type(error).__name__}: {error}")
                done_event.set()

            vc.play(source, after=after_play)

            # Wait for playback to finish (with a generous timeout)
            try:
                await asyncio.wait_for(done_event.wait(), timeout=300)
            except asyncio.TimeoutError:
                vc.stop()
                log("warning", "[VOICE] Sound playback timed out, stopped.")

        except discord.ClientException as e:
            log("warning", f"[VOICE] ClientException during playback: {e}")
        except Exception as e:
            log("error", f"[VOICE] Playback failed ({path.name}): {type(e).__name__}: {e}")
            print(f"❌ Playback error: {type(e).__name__}: {e}")
        finally:
            # Always re-mute after playing (or on error)
            try:
                if vc.is_connected():
                    await vc.guild.change_voice_state(
                        channel=vc.channel, self_mute=True, self_deaf=False
                    )
            except Exception as e:
                log("warning", f"[VOICE] Could not re-mute: {e}")

    # ------------------------------------------------------------------
    # Alone-watcher
    # ------------------------------------------------------------------

    def _start_alone_watcher(self, guild_id: int, voice_channel: discord.VoiceChannel):
        """Spawn the task that auto-disconnects if bot is left alone."""
        task = asyncio.create_task(
            self._alone_watcher(guild_id, voice_channel),
            name=f"voice-alone-{guild_id}",
        )
        self._alone_tasks[guild_id] = task
        task.add_done_callback(lambda t: self._alone_tasks.pop(guild_id, None))

    async def _alone_watcher(self, guild_id: int, voice_channel: discord.VoiceChannel):
        """Poll every 5s.
        - invited:     stay until channel empty for VOICE_ALONE_DISCONNECT_SECONDS.
        - spontaneous: leave after random stay duration, or immediately when alone.
        """
        timeout = max(5, cfg.get("VOICE_ALONE_DISCONNECT_SECONDS", 30))
        alone_since: float | None = None

        mode = self._join_modes.get(guild_id, "invited")
        stay_deadline: float | None = None
        if mode == "spontaneous":
            min_stay = cfg.get("VOICE_SPONTANEOUS_MIN_STAY", 60)
            max_stay = cfg.get("VOICE_SPONTANEOUS_MAX_STAY", 300)
            stay_seconds = random.uniform(min_stay, max_stay)
            stay_deadline = asyncio.get_event_loop().time() + stay_seconds
            log("info", f"[VOICE] Spontaneous stay timer: {stay_seconds:.0f}s in #{voice_channel.name}")

        try:
            while True:
                await asyncio.sleep(5)

                vc = self._voice_clients.get(guild_id)
                if not vc or not vc.is_connected():
                    break

                now = asyncio.get_event_loop().time()
                current_mode = self._join_modes.get(guild_id, "invited")
                human_members = [m for m in vc.channel.members if not m.bot]

                # ── Spontaneous mode ──────────────────────────────────
                if current_mode == "spontaneous":
                    if not human_members:
                        log("info", f"[VOICE] Spontaneous: alone in #{vc.channel.name}, leaving.")
                        print(f"🔇 Spontaneous leave: alone in #{vc.channel.name}")
                        await self.disconnect(guild_id, reason="spontaneous-alone")
                        break
                    if stay_deadline and now >= stay_deadline:
                        log("info", f"[VOICE] Spontaneous stay expired in #{vc.channel.name}, leaving.")
                        print(f"🔇 Spontaneous leave: stay timer expired in #{vc.channel.name}")
                        await self.disconnect(guild_id, reason="spontaneous-timeout")
                        break
                    continue

                # ── Invited mode ──────────────────────────────────────
                if not human_members:
                    if alone_since is None:
                        alone_since = now
                        log("info", f"[VOICE] Alone in #{vc.channel.name}, starting {timeout}s timer.")
                    elif now - alone_since >= timeout:
                        log("info", f"[VOICE] Alone for {timeout}s, auto-disconnecting.")
                        print(f"🔇 Auto-disconnect: alone in #{vc.channel.name} for {timeout}s.")
                        await self.disconnect(guild_id, reason="alone-timeout")
                        break
                else:
                    if alone_since is not None:
                        log("debug", "[VOICE] Someone rejoined, resetting alone timer.")
                    alone_since = None

        except asyncio.CancelledError:
            log("debug", "[VOICE] Alone watcher cancelled.")
        except Exception as e:
            log("error", f"[VOICE] Alone watcher error: {e}")

    # ------------------------------------------------------------------
    # Spontaneous joins
    # ------------------------------------------------------------------

    def start_spontaneous_loop(self):
        """Start the background spontaneous-join task (called from on_ready)."""
        if not cfg.get("ENABLE_VOICE_SPONTANEOUS"):
            return
        self._spontaneous_task = asyncio.create_task(
            self._spontaneous_loop(), name="voice-spontaneous"
        )

    async def _spontaneous_loop(self):
        """Periodically scan guilds and randomly join a populated voice channel."""
        check_interval = max(30, cfg.get("VOICE_SPONTANEOUS_CHECK_INTERVAL", 300))
        join_chance = cfg.get("VOICE_SPONTANEOUS_JOIN_CHANCE", 25)

        try:
            await asyncio.sleep(60)
            while True:
                await asyncio.sleep(check_interval)

                if not cfg.get("ENABLE_VOICE_SPONTANEOUS"):
                    continue

                for guild in bot.guilds:
                    if self.is_connected(guild.id):
                        continue
                    populated = [
                        ch for ch in guild.voice_channels
                        if any(not m.bot for m in ch.members)
                    ]
                    if not populated:
                        continue
                    if random.randint(1, 100) > join_chance:
                        continue
                    channel = random.choice(populated)
                    log("info", f"[VOICE] Spontaneously joining #{channel.name} in {guild.name}")
                    print(f"🎲 Spontaneous join: #{channel.name} in {guild.name}")
                    await self.join_voice(
                        guild_id=guild.id,
                        voice_channel=channel,
                        text_channel=None,
                        llm_response="",
                        mode="spontaneous",
                    )

        except asyncio.CancelledError:
            log("debug", "[VOICE] Spontaneous loop cancelled.")
        except Exception as e:
            log("error", f"[VOICE] Spontaneous loop error: {e}")
            print(f"❌ Spontaneous loop error: {e}")

    # ------------------------------------------------------------------
    # Status info
    # ------------------------------------------------------------------

    def status_embed(self) -> discord.Embed:
        """Build a status embed for the /voice-status command."""
        embed = discord.Embed(
            title="🎙️ Voice Manager Status",
            color=discord.Color.green() if self._voice_clients else discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(
            name="Feature enabled",
            value="✅ Yes" if cfg.get("ENABLE_VOICE") else "❌ No",
            inline=True,
        )
        embed.add_field(
            name="Connected guilds",
            value=str(len(self._voice_clients)) or "0",
            inline=True,
        )
        embed.add_field(
            name="Sounds loaded",
            value=str(len(self._sounds)),
            inline=True,
        )
        embed.add_field(
            name="Sounds enabled",
            value="✅ Yes" if cfg.get("ENABLE_VOICE_SOUNDS") else "❌ No",
            inline=True,
        )
        embed.add_field(
            name="Sound interval",
            value=(
                f"{cfg.get('VOICE_SOUND_INTERVAL_BASE', 45)}s "
                f"± {cfg.get('VOICE_SOUND_INTERVAL_VARIANCE', 20)}s"
            ),
            inline=True,
        )
        embed.add_field(
            name="Alone timeout",
            value=f"{cfg.get('VOICE_ALONE_DISCONNECT_SECONDS', 30)}s",
            inline=True,
        )

        if self._voice_clients:
            lines = []
            for gid, vc in self._voice_clients.items():
                ch = getattr(vc, "channel", None)
                ch_name = f"#{ch.name}" if ch else "unknown"
                human_count = len([m for m in ch.members if not m.bot]) if ch else "?"
                lines.append(f"Guild `{gid}` → {ch_name} ({human_count} humans)")
            embed.add_field(name="Active sessions", value="\n".join(lines), inline=False)
        else:
            embed.add_field(name="Active sessions", value="None", inline=False)

        sounds_folder = BOT_DIR / cfg.get("SOUNDS_FOLDER", "sounds")
        embed.set_footer(text=f"Sounds folder: {sounds_folder}")
        return embed


# Global VoiceManager instance (initialised after bot is created)
voice_manager: VoiceManager | None = None




def format_user_identity(message: discord.Message) -> str:
    author = message.author
    parts: list[str] = []

    username = author.name
    server_nick = getattr(author, "nick", None)
    display_name = getattr(author, "global_name", None) or author.display_name

    parts.append(username)

    if server_nick and server_nick != username:
        parts.append(server_nick)

    if display_name and display_name not in parts:
        parts.append(display_name)

    return " | ".join(parts)


def get_mention_text(message: discord.Message, bot_user: discord.ClientUser) -> str:
    """Strip all @bot mentions from the message and return the remaining text."""
    content = message.content
    content = re.sub(rf"<@!?{bot_user.id}>", "", content).strip()
    return content


def _parse_birthday_ping_roles() -> list[int]:
    """Parse BIRTHDAY_PING_ROLES from config into a list of int IDs."""
    raw = cfg.get("BIRTHDAY_PING_ROLES", "").strip()
    if not raw:
        return []
    ids = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
    return ids


# ============================================================
# ATTENTION WINDOW
# ============================================================

# Tracks channels where Bruh is "paying attention" without needing a new @ping.
# Format: { channel_id: {"user_id": int, "expires": datetime} }
attention_windows: dict[int, dict] = {}


def _check_attention_window(message: discord.Message, bot_user: discord.ClientUser) -> bool:
    """Return True if the bot should respond in this channel without being @mentioned.

    Rules:
    - Window must not have expired.
    - Always respond if the bot's name ("bruh") appears anywhere in the message.
    - Respond if the message is from the user who activated the window AND they are
      not @mentioning someone else (which signals they're talking to another person).
    - Silently ignore messages from other users that don't mention the bot name.
    """
    channel_id = message.channel.id
    window = attention_windows.get(channel_id)
    if not window:
        return False

    now = discord.utils.utcnow()
    if window["expires"] <= now:
        attention_windows.pop(channel_id, None)
        log("debug", f"[ATTENTION] Window expired for channel {channel_id}")
        return False

    # If they're replying to another message, check who they're replying to.
    # A reply to the bot is fine; a reply to anyone else means they've moved on.
    if message.reference is not None:
        ref = message.reference.resolved
        if isinstance(ref, discord.Message) and ref.author.id != bot_user.id:
            return False

    return True


def _refresh_attention_window(message: discord.Message):
    """Set or refresh the attention window for the message's channel."""
    seconds = cfg.get("ATTENTION_WINDOW_SECONDS", 300)
    if seconds <= 0:
        return
    attention_windows[message.channel.id] = {
        "user_id": message.author.id,
        "expires": discord.utils.utcnow() + timedelta(seconds=seconds),
    }
    log("info", f"[ATTENTION] Window opened in #{getattr(message.channel, 'name', message.channel.id)} "
                f"by {message.author} | expires in {seconds}s")


# ============================================================
# DEBOUNCE
# ============================================================

# Pending debounce tasks per channel: { channel_id: asyncio.Task }
_debounce_tasks: dict[int, asyncio.Task] = {}

# The latest triggering message per channel (what we'll reply to after the wait)
_debounce_last_message: dict[int, discord.Message] = {}


def _schedule_debounced_reply(
    message: discord.Message,
    mention_text: str,
    user_identity: str,
    source: str,
):
    """Cancel any pending debounce task for this channel and schedule a new one.

    When the timer fires (no new messages arrived within LLM_DEBOUNCE_SECONDS),
    handle_llm_mention is called with the *latest* message, so the full burst
    is already present in the channel history for fetch_channel_context to pick up.
    """
    channel_id = message.channel.id
    delay = cfg.get("LLM_DEBOUNCE_SECONDS", 2)

    # Cancel previous pending task if any
    existing = _debounce_tasks.get(channel_id)
    if existing and not existing.done():
        existing.cancel()
        log("debug", f"[DEBOUNCE] Cancelled previous task for channel {channel_id}")

    # Store the latest message so the fired task uses it
    _debounce_last_message[channel_id] = message

    async def _fire():
        if delay > 0:
            await asyncio.sleep(delay)

        # Use the most recent message stored at the time we fire
        last_msg = _debounce_last_message.get(channel_id)
        if last_msg is None:
            return

        # Strip bot mention from the latest message
        final_text = get_mention_text(last_msg, bot.user) or last_msg.content
        final_identity = format_user_identity(last_msg)

        log("debug", f"[DEBOUNCE] Firing for channel {channel_id} | {final_identity}")

        if cfg["ENABLE_LLM"]:
            if cfg["LLM_PERCENTAGE"] and random.randint(1, 100) > cfg["LLM_PERCENTAGE_VALUE"]:
                log("debug", f"[LLM] Skipped (percentage gate) for {final_identity}")
                channel_info = f"#{last_msg.channel}" if hasattr(last_msg.channel, "name") else "DM"
                if msgs.mention:
                    fallback = random.choice(msgs.mention)
                    try:
                        await last_msg.channel.send(fallback)
                        log("info", f"[LLM-PCT-SKIP] {channel_info} | BOT - {fallback!r}")
                    except discord.Forbidden:
                        pass
                return
            await handle_llm_mention(last_msg, final_text, final_identity)
        else:
            if msgs.mention:
                fallback = random.choice(msgs.mention)
                try:
                    await last_msg.channel.send(fallback)
                    channel_info = f"#{last_msg.channel}" if hasattr(last_msg.channel, "name") else "DM"
                    log("info", f"[{source}-REPLY] {channel_info} | BOT - {fallback!r}")
                except discord.Forbidden:
                    pass

        # Cleanup
        _debounce_tasks.pop(channel_id, None)
        _debounce_last_message.pop(channel_id, None)

    task = asyncio.create_task(_fire())
    _debounce_tasks[channel_id] = task


# ============================================================
# LLM CLIENT
# ============================================================

def _build_messages(
    prompt: str,
    user_identity: str,
    history: list[dict],
    extra_system_prompt: str = "",
    channel_name: str = "",
) -> list[dict]:
    channel_ctx = (
        f"\nYou are currently active in channel: #{channel_name}." if channel_name else ""
    )
    system_prompt = (
        cfg["LLM_SYSTEM_PROMPT"]
        + (f"\n\n{extra_system_prompt}" if extra_system_prompt else "")
        + f"\n\nYou are participating in a group Discord chat. Multiple people may talk to you."
        + channel_ctx
        + f"\nThe person currently addressing you is: {user_identity}"
        + f"\nWhen you see messages prefixed with [HH:MM] [Name]:, those are other members of the chat."
        + f"\nTimestamps are in UTC and show when each message was sent."
        + f"\nBe aware of what others said, who said it, and when."
    )
    msgs_out = [{"role": "system", "content": system_prompt}]
    msgs_out.extend(history)
    msgs_out.append({"role": "user", "content": f"[{user_identity}]: {prompt}"})
    return msgs_out


async def _query_ollama(messages: list[dict], session: aiohttp.ClientSession) -> str | None:
    url = f"{cfg['LLM_BASE_URL']}/api/chat"
    payload = {
        "model": cfg["LLM_MODEL"],
        "stream": False,
        "options": {"num_predict": cfg["LLM_MAX_TOKENS"]},
        "messages": messages,
    }
    async with session.post(url, json=payload) as resp:
        if resp.status != 200:
            print(f"❌ Ollama returned HTTP {resp.status}: {await resp.text()}")
            return None
        data = await resp.json()
        return data.get("message", {}).get("content", "").strip()


async def _query_ollama_cloud(messages: list[dict], session: aiohttp.ClientSession) -> str | None:
    """Query the Ollama Cloud API at ollama.com using Bearer token auth.

    Note: 'options' (num_predict etc.) is a local-Ollama-only field.
    The cloud endpoint ignores/rejects it, causing empty responses - so it is omitted.
    """
    api_key = cfg.get("LLM_API_KEY", "").strip()
    if not api_key:
        print("❌ ollama_cloud requires LLM_API_KEY. Get one at https://ollama.com/settings/keys")
        return None

    url = f"{cfg['LLM_BASE_URL'].rstrip('/')}/api/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": cfg["LLM_MODEL"],
        "stream": False,
        "messages": messages,
    }
    async with session.post(url, json=payload, headers=headers) as resp:
        if resp.status == 401:
            print("❌ Ollama Cloud: Unauthorized - check your LLM_API_KEY.")
            return None
        if resp.status != 200:
            print(f"❌ Ollama Cloud returned HTTP {resp.status}: {await resp.text()}")
            return None
        data = await resp.json()
        content = data.get("message", {}).get("content", "").strip()
        if not content:
            print(f"⚠️  Ollama Cloud returned empty content. Raw response: {data}")
        return content or None


async def _query_openai_compat(messages: list[dict], session: aiohttp.ClientSession,
                                base_url: str, api_key: str) -> str | None:
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": cfg["LLM_MODEL"],
        "max_tokens": cfg["LLM_MAX_TOKENS"],
        "messages": messages,
    }
    async with session.post(url, json=payload, headers=headers) as resp:
        if resp.status != 200:
            print(f"❌ LLM ({base_url}) returned HTTP {resp.status}: {await resp.text()}")
            return None
        data = await resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def _query_anthropic(messages: list[dict], session: aiohttp.ClientSession) -> str | None:
    system_text = ""
    chat_messages = []
    for m in messages:
        if m["role"] == "system":
            system_text = m["content"]
        else:
            chat_messages.append(m)

    url = f"{cfg['LLM_BASE_URL'].rstrip('/')}/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": cfg["LLM_API_KEY"],
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": cfg["LLM_MODEL"],
        "max_tokens": cfg["LLM_MAX_TOKENS"],
        "system": system_text,
        "messages": chat_messages,
    }
    async with session.post(url, json=payload, headers=headers) as resp:
        if resp.status != 200:
            print(f"❌ Anthropic returned HTTP {resp.status}: {await resp.text()}")
            return None
        data = await resp.json()
        return data["content"][0]["text"].strip()


async def _query_gemini(messages: list[dict], session: aiohttp.ClientSession) -> str | None:
    system_text = ""
    contents = []
    for m in messages:
        if m["role"] == "system":
            system_text = m["content"]
        else:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

    url = (
        f"{cfg['LLM_BASE_URL'].rstrip('/')}/v1beta/models/"
        f"{cfg['LLM_MODEL']}:generateContent?key={cfg['LLM_API_KEY']}"
    )
    payload: dict = {
        "contents": contents,
        "generationConfig": {"maxOutputTokens": cfg["LLM_MAX_TOKENS"]},
    }
    if system_text:
        payload["systemInstruction"] = {"parts": [{"text": system_text}]}

    async with session.post(url, json=payload) as resp:
        if resp.status != 200:
            print(f"❌ Gemini returned HTTP {resp.status}: {await resp.text()}")
            return None
        data = await resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()


async def query_llm(
    prompt: str,
    user_identity: str,
    history: list[dict],
    extra_system_prompt: str = "",
    channel_name: str = "",
) -> str | None:
    provider = cfg.get("LLM_PROVIDER", "ollama").lower()
    messages = _build_messages(prompt, user_identity, history, extra_system_prompt, channel_name)

    try:
        timeout = aiohttp.ClientTimeout(total=cfg["LLM_TIMEOUT"])
        async with aiohttp.ClientSession(timeout=timeout) as session:

            if provider == "ollama":
                return await _query_ollama(messages, session)

            elif provider == "ollama_cloud":
                return await _query_ollama_cloud(messages, session)

            elif provider == "anthropic":
                return await _query_anthropic(messages, session)

            elif provider == "gemini":
                return await _query_gemini(messages, session)

            elif provider in ("openai", "lmstudio", "groq", "openrouter", "openai_compat"):
                return await _query_openai_compat(
                    messages, session,
                    base_url=cfg["LLM_BASE_URL"],
                    api_key=cfg.get("LLM_API_KEY", ""),
                )

            else:
                print(f"❌ Unknown LLM_PROVIDER '{provider}'.")
                return None

    except asyncio.TimeoutError:
        print(f"❌ LLM request timed out after {cfg['LLM_TIMEOUT']}s")
        return None
    except aiohttp.ClientConnectorError as e:
        print(f"❌ Cannot connect to LLM at {cfg['LLM_BASE_URL']} - is it running? ({e})")
        return None
    except Exception as e:
        print(f"❌ LLM error ({provider}): {e}")
        return None


# ============================================================
# DEMOTIVATOR HELPER
# ============================================================

def _build_demotivator(photo: Image.Image, title: str, subtitle: str = "") -> bytes:
    """
    Render a classic demotivational-poster image.

    Layout:
      • Black background
      • Photo with thin white border, centered
      • Title in large white serif below
      • Optional subtitle in smaller grey serif below that
    """
    BORDER = 6    # white border thickness around photo
    PAD    = 40   # outer padding on all sides

    # ── fonts ────────────────────────────────────────────────
    SERIF_BOLD = [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ]
    SERIF_REG = [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ]

    def _font(paths, size):
        for p in paths:
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
        return ImageFont.load_default(size=size)

    title_font = _font(SERIF_BOLD, 48)
    sub_font   = _font(SERIF_REG,  24)

    # ── scale photo so it fits within 600 px wide ────────────
    max_w = 600
    if photo.width > max_w:
        ratio = max_w / photo.width
        photo = photo.resize(
            (int(photo.width * ratio), int(photo.height * ratio)),
            Image.LANCZOS,
        )

    W       = photo.width + (BORDER + PAD) * 2
    inner_w = W - PAD * 2

    # ── measure / wrap text ──────────────────────────────────
    dummy = Image.new("RGB", (1, 1))
    d     = ImageDraw.Draw(dummy)

    def wrap(text: str, font) -> list[str]:
        lines, line = [], ""
        for word in text.split():
            test = (line + " " + word).strip()
            if d.textlength(test, font=font) <= inner_w:
                line = test
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    title_lines = wrap(title.upper(), title_font)
    sub_lines   = wrap(subtitle, sub_font) if subtitle.strip() else []

    LH_TITLE = 56   # line height for title
    LH_SUB   = 30   # line height for subtitle

    title_block_h = len(title_lines) * LH_TITLE
    sub_block_h   = (10 + len(sub_lines) * LH_SUB) if sub_lines else 0

    H = (PAD
         + BORDER + photo.height + BORDER
         + 20                     # gap between photo and title
         + title_block_h
         + sub_block_h
         + 30)                    # bottom breathing room

    # ── draw ─────────────────────────────────────────────────
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    draw   = ImageDraw.Draw(canvas)

    # white border rectangle
    bx, by = PAD - BORDER, PAD - BORDER
    draw.rectangle(
        [bx, by, bx + photo.width + BORDER * 2, by + photo.height + BORDER * 2],
        fill="white",
    )
    canvas.paste(photo.convert("RGB"), (PAD, PAD))

    # title
    y = PAD + photo.height + BORDER + 20
    for line in title_lines:
        tw = d.textlength(line, font=title_font)
        draw.text(((W - tw) / 2, y), line, font=title_font, fill="white")
        y += LH_TITLE

    # subtitle
    if sub_lines:
        y += 10
        for line in sub_lines:
            tw = d.textlength(line, font=sub_font)
            draw.text(((W - tw) / 2, y), line, font=sub_font, fill=(180, 180, 180))
            y += LH_SUB

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue()


# ============================================================
# BOT SETUP
# ============================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix=cfg["COMMAND_PREFIX"], intents=intents)

# Tracks recent joins for chicken-out detection: {member_id: join_timestamp}
recent_joins: dict[int, discord.utils.datetime] = {}

# Tracks which UTC dates we already announced birthdays for (prevents double-firing)
# Format: "YYYY-MM-DD"
_birthday_announced_dates: set[str] = set()


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
    channel = bot.get_channel(cfg["SUGGESTION_CHANNEL_ID"])
    if not channel:
        await interaction.response.send_message("❌ Suggestion channel not found.", ephemeral=True)
        return

    embed = build_suggestion_embed(interaction.user, content, author, jump_url)
    view = SuggestionView(content)
    ping = f"<@&{cfg['SUGGESTION_PING_ROLE_ID']}>" if cfg.get("SUGGESTION_PING_ROLE_ID") else ""

    await channel.send(content=f"{ping} New suggestion!", embed=embed, view=view)
    await interaction.response.send_message("✅ Suggestion submitted!", ephemeral=True)


async def send_birthday_announcements(guild: discord.Guild, month: int, day: int):
    """Send birthday messages for all users whose birthday is today."""
    channel = bot.get_channel(cfg["BIRTHDAY_CHANNEL_ID"])
    if not channel:
        print(f"⚠️  Birthday channel not found (ID: {cfg['BIRTHDAY_CHANNEL_ID']}). Skipping.")
        return

    birthday_user_ids = birthdays.get_todays(month, day)
    if not birthday_user_ids:
        return

    # Build role ping prefix once
    role_ids = _parse_birthday_ping_roles()
    role_pings = " ".join(f"<@&{rid}>" for rid in role_ids) if role_ids else ""

    for user_id in birthday_user_ids:
        member = guild.get_member(user_id)
        if member is None:
            try:
                member = await guild.fetch_member(user_id)
            except (discord.NotFound, discord.HTTPException):
                log("warning", f"[BIRTHDAY] Could not find member {user_id} in guild.")
                continue

        display_name = (
            getattr(member, "nick", None)
            or getattr(member, "global_name", None)
            or member.display_name
            or member.name
        )

        # Format the birthday message from config template
        bday_text = cfg["BIRTHDAY_MESSAGE"].format(
            mention=member.mention,
            name=display_name,
        )

        # Build final message: role pings + user ping + birthday text
        parts = []
        if role_pings:
            parts.append(role_pings)
        parts.append(member.mention)
        ping_line = " ".join(parts)

        try:
            await channel.send(ping_line)
            await channel.send(bday_text)
            log("info", f"[BIRTHDAY] Announced birthday for {member} ({user_id})")
            print(f"🎂 Birthday announced for {member} in #{channel}")
        except discord.Forbidden:
            print(f"❌ Birthday: no permission to send in #{channel}.")
        except Exception as e:
            print(f"❌ Birthday send error for {user_id}: {e}")


from discord.ext import tasks


# ============================================================
# COMMAND DEDUPLICATION
# ============================================================

async def fix_duplicate_commands():
    if _GUILD is None:
        return

    print("🔍 Checking for duplicate commands...")

    try:
        global_commands = await bot.tree.fetch_commands()
        guild_commands  = await bot.tree.fetch_commands(guild=_GUILD)
    except Exception as e:
        print(f"⚠️  Could not fetch commands for dedup check: {e}")
        return

    global_names = {c.name for c in global_commands}
    guild_names  = {c.name for c in guild_commands}

    GLOBAL_ONLY = {"Suggest message"}

    leaked_to_guild  = GLOBAL_ONLY & guild_names
    leaked_to_global = global_names - GLOBAL_ONLY

    if leaked_to_guild or leaked_to_global:
        if leaked_to_guild:
            print(f"⚠️  In guild scope but should be global only : {leaked_to_guild}")
        if leaked_to_global:
            print(f"⚠️  In global scope but should be guild only : {leaked_to_global}")
        print("🔧 Duplicates detected - the sync() calls below will correct this automatically.")
    else:
        print("✅ No duplicate commands found.")


# ============================================================
# SHITPOST LOOP
# ============================================================

@tasks.loop(minutes=1)
async def shitpost_loop():
    """Periodically drop a random post in the shitpost channel."""
    if not cfg["ENABLE_SHITPOST"]:
        return

    channel = bot.get_channel(cfg["SHITPOST_CHANNEL_ID"])
    if not channel:
        print(f"⚠️  Shitpost channel not found (ID: {cfg['SHITPOST_CHANNEL_ID']}). Skipping.")
        return

    choices = ["default", "mention", "llm"]

    if not cfg["ENABLE_LLM"]:
        choices.remove("llm")
    if not msgs.default and "default" in choices:
        choices.remove("default")
    if not msgs.mention and "mention" in choices:
        choices.remove("mention")

    if not choices:
        print("⚠️  Shitpost: no content available.")
        return

    pick = random.choice(choices)
    text = None

    try:
        if pick == "default":
            text = random.choice(msgs.default)

        elif pick == "mention":
            text = random.choice(msgs.mention)

        elif pick == "llm":
            extra_prompt = cfg.get("SHITPOST_LLM_EXTRA_PROMPT", "").strip()
            shitpost_trigger = "Post something random right now. No context. Just go."
            channel_name = getattr(channel, "name", "")
            history = await fetch_channel_context(
                channel, None, bot.user,
                limit=cfg.get("LLM_CONTEXT_MESSAGES", 20),
                guild=channel.guild if hasattr(channel, "guild") else None,
            )
            if cfg["LLM_TYPING_INDICATOR"]:
                async with channel.typing():
                    text = await query_llm(
                        shitpost_trigger, "Bruh", history,
                        extra_system_prompt=extra_prompt,
                        channel_name=channel_name,
                    )
            else:
                text = await query_llm(
                    shitpost_trigger, "Bruh", history,
                    extra_system_prompt=extra_prompt,
                    channel_name=channel_name,
                )

            if not text:
                fallback_pool = [m for lst in [msgs.default, msgs.mention] for m in lst]
                if fallback_pool:
                    text = random.choice(fallback_pool)
                    pick = "llm-fallback"

        if text:
            if len(text) > 1990:
                text = text[:1990] + "..."
            await channel.send(text)
            log("info", f"[SHITPOST/{pick.upper()}] #{channel} | BOT - {text!r}")
            short = repr(text)[:80]
            print(f"💩 Shitpost ({pick}) - #{channel}: {short}")

    except discord.Forbidden:
        print(f"❌ Shitpost: no permission to send in #{channel}.")
    except Exception as e:
        print(f"❌ Shitpost error: {e}")


@shitpost_loop.before_loop
async def before_shitpost_loop():
    await bot.wait_until_ready()


# ============================================================
# HEARTBEAT LOOP
# ============================================================

@tasks.loop(seconds=180)
async def heartbeat_loop():
    """Ping the configured heartbeat URL so uptime monitors know the bot is alive."""
    url = cfg.get("HEARTBEAT_URL", "").strip()
    if not url:
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status < 300:
                    log("info", f"[HEARTBEAT] Pinged {url} → {resp.status}")
                else:
                    print(f"⚠️  Heartbeat ping returned HTTP {resp.status}")
    except Exception as e:
        print(f"⚠️  Heartbeat ping failed: {e}")


@heartbeat_loop.before_loop
async def before_heartbeat_loop():
    await bot.wait_until_ready()


# ============================================================
# BIRTHDAY CHECK LOOP
# ============================================================

@tasks.loop(minutes=1)
async def birthday_check_loop():
    """Check once per day (at BIRTHDAY_CHECK_HOUR UTC) for birthdays."""
    if not cfg["ENABLE_BIRTHDAYS"]:
        return

    now = datetime.now(timezone.utc)

    # Only fire at the configured hour, on the :00 minute
    if now.hour != cfg["BIRTHDAY_CHECK_HOUR"] or now.minute != 0:
        return

    date_key = now.strftime("%Y-%m-%d")
    if date_key in _birthday_announced_dates:
        return  # Already ran today
    _birthday_announced_dates.add(date_key)

    # Keep the set small - only keep the last 2 dates
    if len(_birthday_announced_dates) > 2:
        oldest = sorted(_birthday_announced_dates)[0]
        _birthday_announced_dates.discard(oldest)

    print(f"🎂 Running birthday check for {date_key} (month={now.month}, day={now.day})")
    log("info", f"[BIRTHDAY] Daily check triggered for {date_key}")

    # Run announcements in every guild the bot is in
    for guild in bot.guilds:
        await send_birthday_announcements(guild, now.month, now.day)


@birthday_check_loop.before_loop
async def before_birthday_check_loop():
    await bot.wait_until_ready()


# ============================================================
# EVENTS
# ============================================================

@bot.event
async def on_ready():
    global voice_manager
    print(f"✅ {bot.user} is online!")
    print(f"   Default msgs      : {len(msgs.default)}")
    print(f"   Mention msgs      : {len(msgs.mention)}")
    print(f"   LLM               : {'✅ ' + cfg['LLM_PROVIDER'].upper() + ' / ' + cfg['LLM_MODEL'] + ' @ ' + cfg['LLM_BASE_URL'] if cfg['ENABLE_LLM'] else '❌ disabled'}")
    print(f"   Context msgs      : last {cfg['LLM_CONTEXT_MESSAGES']} channel messages per response")
    print(f"   Attention window  : {'✅ ' + str(cfg['ATTENTION_WINDOW_SECONDS']) + 's | debounce ' + str(cfg['LLM_DEBOUNCE_SECONDS']) + 's' if cfg['ENABLE_ATTENTION_WINDOW'] else '❌ ping-only mode'}")
    print(f"   Logging           : {'✅ ' + cfg['LOG_DIR'] + '/' + cfg['LOG_FILE'] if cfg['ENABLE_LOGGING'] else '❌ disabled'}")
    print(f"   Guild ID          : {cfg['GUILD_ID'] if cfg['GUILD_ID'] else '❌ not set (all commands global)'}")

    # ── Voice manager ─────────────────────────────────────────────────────────
    if cfg.get("ENABLE_VOICE"):
        voice_manager = VoiceManager()
        voice_manager.start_spontaneous_loop()
        print(f"   Voice             : ✅ sounds={len(voice_manager.sounds)} | "
              f"interval={cfg['VOICE_SOUND_INTERVAL_BASE']}±{cfg['VOICE_SOUND_INTERVAL_VARIANCE']}s | "
              f"alone-timeout={cfg['VOICE_ALONE_DISCONNECT_SECONDS']}s")
    else:
        voice_manager = None
        print(f"   Voice             : ❌ disabled")

    # ── Auto-fix duplicates before syncing ──────────────────────────────────
    await fix_duplicate_commands()

    # ── Sync commands ────────────────────────────────────────────────────────
    try:
        synced_global = await bot.tree.sync()

        if _GUILD:
            synced_guild = await bot.tree.sync(guild=_GUILD)
            print(f"🔄 Commands synced: {len(synced_global)} global, {len(synced_guild)} guild.")
        else:
            print(f"🔄 Commands synced: {len(synced_global)} global (no GUILD_ID set).")

    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

    # ── Heartbeat loop ───────────────────────────────────────────────────────
    hb_url = cfg.get("HEARTBEAT_URL", "").strip()
    if hb_url:
        interval = max(10, cfg.get("HEARTBEAT_INTERVAL_SECONDS", 180))
        heartbeat_loop.change_interval(seconds=interval)
        if not heartbeat_loop.is_running():
            heartbeat_loop.start()
        print(f"   Heartbeat         : ✅ every {interval}s → {hb_url}")
    else:
        print(f"   Heartbeat         : ❌ disabled (HEARTBEAT_URL not set)")

    # ── Shitpost loop ────────────────────────────────────────────────────────
    if cfg["ENABLE_SHITPOST"]:
        interval = max(1, cfg["SHITPOST_INTERVAL_MINUTES"])
        shitpost_loop.change_interval(minutes=interval)
        if not shitpost_loop.is_running():
            shitpost_loop.start()
        extra = cfg.get("SHITPOST_LLM_EXTRA_PROMPT", "").strip()
        print(f"   Shitpost          : ✅ every {interval} min - channel {cfg['SHITPOST_CHANNEL_ID']}")
        print(f"   Shitpost LLM extra: {'✅ set' if extra else 'ℹ️  none'}")
    else:
        print(f"   Shitpost          : ❌ disabled")

    # ── Birthday loop ────────────────────────────────────────────────────────
    if cfg["ENABLE_BIRTHDAYS"]:
        if not birthday_check_loop.is_running():
            birthday_check_loop.start()
        role_ids = _parse_birthday_ping_roles()
        roles_str = ", ".join(str(r) for r in role_ids) if role_ids else "none"
        print(f"   Birthdays         : ✅ channel={cfg['BIRTHDAY_CHANNEL_ID']} | "
              f"check hour={cfg['BIRTHDAY_CHECK_HOUR']}:00 UTC | "
              f"ping roles=[{roles_str}] | "
              f"registered={len(birthdays.all())}")
    else:
        print(f"   Birthdays         : ❌ disabled")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    user_identity = format_user_identity(message)
    channel_info = f"#{message.channel}" if hasattr(message.channel, 'name') else "DM"

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
            random_msg = random.choice(msgs.default)
            await message.channel.send(random_msg)
            log("info", f"[RANDOM] {channel_info} | BOT - {random_msg!r}")
        except discord.Forbidden:
            pass

    # --- Mention / attention-window response ---
    if cfg["ENABLE_MENTION_RESPONSES"]:
        is_mentioned = bot.user.mentioned_in(message)
        in_window = (
            cfg.get("ENABLE_ATTENTION_WINDOW", False)
            and _check_attention_window(message, bot.user)
        ) if not is_mentioned else False
        if in_window:
            log("info", f"[WINDOW] #{getattr(message.channel, 'name', message.channel.id)} "
                        f"| {format_user_identity(message)}: {message.content!r}")

        if is_mentioned or in_window:
            # Determine the prompt text
            if is_mentioned:
                mention_text = get_mention_text(message, bot.user)
            else:
                mention_text = message.content

            source = "MENTION" if is_mentioned else "WINDOW"

            # Bare @ping with no text → random fallback, don't open/refresh window
            if is_mentioned and not mention_text:
                log("info", f"[{source}-EMPTY] {channel_info} | {user_identity} pinged with no text")
                if msgs.mention:
                    fallback = random.choice(msgs.mention)
                    try:
                        await bot_reply(message, fallback)
                        log("info", f"[{source}-EMPTY-REPLY] {channel_info} | BOT - {fallback!r}")
                    except discord.Forbidden:
                        pass

            else:
                log("info", f"[{source}] {channel_info} | {user_identity} said: {message.content!r}")

                # Refresh (or open) the attention window now that we have real content
                if cfg.get("ENABLE_ATTENTION_WINDOW", False):
                    _refresh_attention_window(message)

                # Schedule a debounced reply or respond immediately depending on mode
                if cfg.get("ENABLE_ATTENTION_WINDOW", False):
                    _schedule_debounced_reply(message, mention_text, user_identity, source)
                else:
                    # Ping-only mode: respond immediately, no debounce
                    if cfg["ENABLE_LLM"]:
                        if cfg["LLM_PERCENTAGE"] and random.randint(1, 100) > cfg["LLM_PERCENTAGE_VALUE"]:
                            log("debug", f"[LLM] Skipped (percentage gate) for {user_identity}")
                            if msgs.mention:
                                fallback = random.choice(msgs.mention)
                                try:
                                    await bot_reply(message, fallback)
                                    log("info", f"[LLM-PCT-SKIP] {channel_info} | BOT - {fallback!r}")
                                except discord.Forbidden:
                                    pass
                        else:
                            await handle_llm_mention(message, mention_text, user_identity)
                    else:
                        if msgs.mention:
                            fallback = random.choice(msgs.mention)
                            try:
                                await bot_reply(message, fallback)
                                log("info", f"[{source}-REPLY] {channel_info} | BOT - {fallback!r}")
                            except discord.Forbidden:
                                pass

    await bot.process_commands(message)


async def bot_reply(message: discord.Message, text: str) -> None:
    """Send *text* as a Discord reply to *message* if ENABLE_REPLY_TO_MESSAGE is on,
    otherwise send a plain channel message."""
    if cfg.get("ENABLE_REPLY_TO_MESSAGE", True):
        await message.reply(text, mention_author=False)
    else:
        await message.channel.send(text)


async def handle_llm_mention(
    message: discord.Message,
    prompt: str,
    user_identity: str,
):
    context_limit = cfg.get("LLM_CONTEXT_MESSAGES", 20)
    guild = message.guild
    channel_name = getattr(message.channel, "name", "")

    # Resolve @mentions in the prompt itself (e.g. "who is <@123>" → "who is <Bufka2011>")
    prompt = resolve_mentions(prompt, guild)

    history = await fetch_channel_context(
        message.channel, message, bot.user,
        limit=context_limit,
        guild=guild,
    )

    # Build voice capability context if voice is enabled
    voice_extra = ""
    author_vc = message.author.voice
    if cfg.get("ENABLE_VOICE") and voice_manager is not None and message.guild is not None:
        if author_vc and author_vc.channel:
            voice_extra = (
                f"\n\n[VOICE CAPABILITY] {message.author.display_name} is currently in "
                f"voice channel #{author_vc.channel.name}. "
                "You CAN join them if you want to — it's one of your abilities. "
                "If you decide to join, start your ENTIRE reply with the single word JOIN "
                "(uppercase, on its own at the start), then write your normal response after it. "
                "Only do this if joining genuinely fits the vibe of the conversation. "
                "If you're not joining, respond completely normally — do NOT mention JOIN at all."
            )
        else:
            voice_extra = (
                "\n\n[VOICE CAPABILITY] You can join voice channels if invited, "
                "but this user is not currently in one."
            )

    try:
        if cfg["LLM_TYPING_INDICATOR"]:
            async with message.channel.typing():
                response = await query_llm(
                    prompt, user_identity, history,
                    channel_name=channel_name,
                    extra_system_prompt=voice_extra,
                )
        else:
            response = await query_llm(
                prompt, user_identity, history,
                channel_name=channel_name,
                extra_system_prompt=voice_extra,
            )

        if not response:
            raise ValueError("Empty response from LLM")

        # Check if the LLM decided to join voice
        first_word = response.strip().split()[0].upper().rstrip(",.!?:") if response.strip() else ""
        if (
            first_word == "JOIN"
            and cfg.get("ENABLE_VOICE")
            and voice_manager is not None
            and message.guild is not None
        ):
            log("info", f"[VOICE] LLM decided to JOIN from regular mention | full: {response!r}")
            if author_vc and author_vc.channel:
                log("info", f"[VOICE] Accepting (via mention) from {user_identity} → #{author_vc.channel.name}")
                joined = await voice_manager.join_voice(
                    guild_id=message.guild.id,
                    voice_channel=author_vc.channel,
                    text_channel=message.channel,
                    llm_response=response,
                    mode="invited",
                )
                if not joined:
                    try:
                        await message.channel.send("ugh, tried to join but Discord had other plans. typical.")
                    except discord.Forbidden:
                        pass
            else:
                # LLM wanted to join but user isn't in VC — strip JOIN and respond normally
                clean = response.strip()
                for pfx in ("JOIN ", "JOIN\n", "JOIN"):
                    if clean.upper().startswith(pfx):
                        clean = clean[len(pfx):].strip()
                        break
                reply = clean if clean else "bro get in a voice channel first, i'm not a magician"
                if len(reply) > 1990:
                    reply = reply[:1990] + "..."
                try:
                    await message.channel.send(reply)
                    log("info", f"[LLM-REPLY] BOT - {message.author} | {reply!r}")
                except discord.Forbidden:
                    pass
        else:
            # Normal response — send as-is
            if len(response) > 1990:
                response = response[:1990] + "..."
            await bot_reply(message, response)
            log("info", f"[LLM-REPLY] BOT - {message.author} | {response!r}")

    except Exception as e:
        print(f"❌ LLM mention handler error: {e}")
        log("warning", f"[LLM-ERROR] {user_identity} | {e}")
        if cfg["LLM_FALLBACK_ON_ERROR"]:
            fallback = cfg.get("LLM_FALLBACK_MSG", "").strip()
            if not fallback and msgs.mention:
                fallback = random.choice(msgs.mention)
            if fallback:
                try:
                    await bot_reply(message, fallback)
                    log("info", f"[LLM-FALLBACK] BOT - {message.author} | {fallback!r}")
                except discord.Forbidden:
                    pass


@bot.event
async def on_member_join(member: discord.Member):
    if cfg["ENABLE_CHICKEN_OUT"]:
        recent_joins[member.id] = discord.utils.utcnow()
    log("info", f"[JOIN] {member} ({member.id}) joined {member.guild}")
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
                log("info", f"[CHICKEN-OUT] {member} left after {int(elapsed)}s")
                print(f"🐔 {member} chickened out after {int(elapsed)}s.")
            except discord.Forbidden:
                print("❌ No permission in chicken-out channel.")
        else:
            print(f"❌ Chicken-out channel not found (ID: {cfg['CHICKEN_OUT_CHANNEL_ID']}).")


@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    msg = f"❌ Command error: {error}"
    print(msg)
    log("error", f"[CMD-ERROR] {interaction.user} | {error}")
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
# SLASH COMMANDS  (guild-only - instant sync)
# ============================================================

@bot.tree.command(name="suggest-msg", description="Suggest a message for the bot to use",
                  guild=_GUILD)
@app_commands.describe(message="The message to suggest")
async def suggest_msg(interaction: discord.Interaction, message: str):
    if not cfg["ENABLE_SUGGESTIONS"]:
        await interaction.response.send_message("❌ Suggestions are disabled.", ephemeral=True)
        return
    await post_suggestion(interaction, message)


@bot.tree.command(name="reload-msgs",
                  description="Reload message lists from disk (admin only)",
                  guild=_GUILD)
@app_commands.default_permissions(administrator=True)
async def reload_msgs(interaction: discord.Interaction):
    msgs.load()
    await interaction.response.send_message(
        f"✅ Reloaded - Default: {len(msgs.default)}, Mention: {len(msgs.mention)}",
        ephemeral=True,
    )


@bot.tree.command(name="clear-memory",
                  description="Bot memory is now the live channel history - nothing to clear!",
                  guild=_GUILD)
async def clear_memory(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🧠 Memory is now the **live channel history** - I read the last "
        f"{cfg.get('LLM_CONTEXT_MESSAGES', 20)} messages every time you ping me, "
        "so there's nothing to clear. Just keep chatting!",
        ephemeral=True,
    )


@bot.tree.command(name="llm-status",
                  description="Check LLM connection status (admin only)",
                  guild=_GUILD)
@app_commands.default_permissions(administrator=True)
async def llm_status(interaction: discord.Interaction):
    if not cfg["ENABLE_LLM"]:
        await interaction.response.send_message("❌ LLM is disabled in config.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    provider = cfg.get("LLM_PROVIDER", "ollama").lower()
    base_url = cfg["LLM_BASE_URL"]
    model    = cfg["LLM_MODEL"]
    api_key  = cfg.get("LLM_API_KEY", "")
    key_hint = f"`...{api_key[-4:]}`" if len(api_key) >= 4 else ("*(none)*" if not api_key else "`set`")

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:

            if provider == "ollama":
                async with session.get(f"{base_url}/api/tags") as resp:
                    if resp.status != 200:
                        await interaction.followup.send(f"⚠️ Ollama responded with HTTP {resp.status}", ephemeral=True)
                        return
                    data   = await resp.json()
                    models = [m["name"] for m in data.get("models", [])]
                    model_list  = ", ".join(models) if models else "none"
                    is_available = any(model in m for m in models)
                    status = "✅ found" if is_available else "⚠️ not found in list"
                    await interaction.followup.send(
                        f"**Provider:** Ollama ✅ Connected\n"
                        f"**Active model:** `{model}` - {status}\n"
                        f"**Installed models:** `{model_list}`",
                        ephemeral=True,
                    )

            elif provider in ("openai", "lmstudio", "groq", "openrouter", "openai_compat"):
                headers = {}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                url = f"{base_url.rstrip('/')}/v1/models"
                async with session.get(url, headers=headers) as resp:
                    if resp.status != 200:
                        await interaction.followup.send(
                            f"⚠️ {provider.upper()} responded with HTTP {resp.status}\n"
                            f"`{await resp.text()[:300]}`",
                            ephemeral=True,
                        )
                        return
                    data = await resp.json()
                    model_ids = [m.get("id", "?") for m in data.get("data", [])]
                    model_list = ", ".join(model_ids[:15]) + ("..." if len(model_ids) > 15 else "")
                    is_available = any(model in mid for mid in model_ids)
                    status = "✅ found" if is_available else "⚠️ not in list"
                    await interaction.followup.send(
                        f"**Provider:** {provider.upper()} ✅ Connected\n"
                        f"**Base URL:** `{base_url}`\n"
                        f"**Active model:** `{model}` - {status}\n"
                        f"**API key:** {key_hint}\n"
                        f"**Available models (sample):** `{model_list or 'none returned'}`",
                        ephemeral=True,
                    )

            elif provider == "anthropic":
                url = f"{base_url.rstrip('/')}/v1/messages"
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model,
                    "max_tokens": 8,
                    "messages": [{"role": "user", "content": "ping"}],
                }
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        await interaction.followup.send(
                            f"**Provider:** Anthropic ✅ Connected\n"
                            f"**Model:** `{model}`\n"
                            f"**API key:** {key_hint}",
                            ephemeral=True,
                        )
                    else:
                        await interaction.followup.send(
                            f"⚠️ Anthropic HTTP {resp.status}: `{await resp.text()[:300]}`",
                            ephemeral=True,
                        )

            elif provider == "gemini":
                url = f"{base_url.rstrip('/')}/v1beta/models?key={api_key}"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        model_ids = [m.get("name", "?").split("/")[-1] for m in data.get("models", [])]
                        model_list = ", ".join(model_ids[:15]) + ("..." if len(model_ids) > 15 else "")
                        is_available = any(model in mid for mid in model_ids)
                        status = "✅ found" if is_available else "⚠️ not in list"
                        await interaction.followup.send(
                            f"**Provider:** Gemini ✅ Connected\n"
                            f"**Active model:** `{model}` - {status}\n"
                            f"**API key:** {key_hint}\n"
                            f"**Available models (sample):** `{model_list or 'none returned'}`",
                            ephemeral=True,
                        )
                    else:
                        await interaction.followup.send(
                            f"⚠️ Gemini HTTP {resp.status}: `{await resp.text()[:300]}`",
                            ephemeral=True,
                        )

            else:
                await interaction.followup.send(
                    f"❓ Unknown provider `{provider}` - cannot test connection.",
                    ephemeral=True,
                )

    except aiohttp.ClientConnectorError as e:
        await interaction.followup.send(f"❌ Cannot reach `{base_url}`: `{e}`", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Status check failed: `{e}`", ephemeral=True)


# ============================================================
# BIRTHDAY SLASH COMMANDS  (guild-only)
# ============================================================

birthday_group = app_commands.Group(
    name="birthday",
    description="Birthday announcement commands",
    guild_ids=[cfg["GUILD_ID"]] if cfg.get("GUILD_ID") else None,
)


@birthday_group.command(name="set", description="Set your birthday so the bot can announce it")
@app_commands.describe(
    month="Month number (1-12)",
    day="Day of the month",
)
async def birthday_set(interaction: discord.Interaction, month: int, day: int):
    if not cfg["ENABLE_BIRTHDAYS"]:
        await interaction.response.send_message("❌ Birthdays are disabled.", ephemeral=True)
        return

    if not BirthdayStore.validate_date(month, day):
        await interaction.response.send_message(
            f"❌ Invalid date: {month}/{day}. Please use a real calendar date.", ephemeral=True
        )
        return

    birthdays.set(interaction.user.id, month, day)
    month_str = BirthdayStore.month_name(month)
    await interaction.response.send_message(
        f"🎂 Your birthday has been set to **{month_str} {day}**!", ephemeral=True
    )
    log("info", f"[BIRTHDAY-SET] {interaction.user} ({interaction.user.id}) set birthday to {month}/{day}")


@birthday_group.command(name="remove", description="Remove your birthday from the bot")
async def birthday_remove(interaction: discord.Interaction):
    if not cfg["ENABLE_BIRTHDAYS"]:
        await interaction.response.send_message("❌ Birthdays are disabled.", ephemeral=True)
        return

    removed = birthdays.remove(interaction.user.id)
    if removed:
        await interaction.response.send_message("✅ Your birthday has been removed.", ephemeral=True)
        log("info", f"[BIRTHDAY-REMOVE] {interaction.user} ({interaction.user.id}) removed birthday")
    else:
        await interaction.response.send_message("ℹ️ You didn't have a birthday set.", ephemeral=True)


@birthday_group.command(name="check", description="See your currently saved birthday")
async def birthday_check(interaction: discord.Interaction):
    if not cfg["ENABLE_BIRTHDAYS"]:
        await interaction.response.send_message("❌ Birthdays are disabled.", ephemeral=True)
        return

    bd = birthdays.get(interaction.user.id)
    if bd:
        month_str = BirthdayStore.month_name(bd["month"])
        await interaction.response.send_message(
            f"🎂 Your birthday is set to **{month_str} {bd['day']}**.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "ℹ️ You have no birthday set. Use `/birthday set` to add one!", ephemeral=True
        )


@birthday_group.command(name="list", description="List all registered birthdays (admin only)")
@app_commands.default_permissions(administrator=True)
async def birthday_list(interaction: discord.Interaction):
    if not cfg["ENABLE_BIRTHDAYS"]:
        await interaction.response.send_message("❌ Birthdays are disabled.", ephemeral=True)
        return

    all_bdays = birthdays.all()
    if not all_bdays:
        await interaction.response.send_message("📭 No birthdays registered yet.", ephemeral=True)
        return

    # Sort by month then day
    sorted_bdays = sorted(all_bdays.items(), key=lambda x: (x[1]["month"], x[1]["day"]))

    lines = []
    for uid_str, bd in sorted_bdays:
        month_str = BirthdayStore.month_name(bd["month"])
        member = interaction.guild.get_member(int(uid_str))
        name = member.display_name if member else f"Unknown ({uid_str})"
        lines.append(f"**{name}** - {month_str} {bd['day']}")

    # Split into chunks if needed (Discord 2000 char limit)
    chunks: list[str] = []
    current = f"🎂 **Registered Birthdays ({len(sorted_bdays)}):**\n"
    for line in lines:
        if len(current) + len(line) + 1 > 1900:
            chunks.append(current)
            current = ""
        current += line + "\n"
    if current:
        chunks.append(current)

    await interaction.response.send_message(chunks[0], ephemeral=True)
    for chunk in chunks[1:]:
        await interaction.followup.send(chunk, ephemeral=True)


@birthday_group.command(
    name="announce-test",
    description="Trigger a test birthday announcement for a user (admin only)"
)
@app_commands.describe(member="The member to announce (defaults to yourself)")
@app_commands.default_permissions(administrator=True)
async def birthday_announce_test(
    interaction: discord.Interaction,
    member: discord.Member | None = None,
):
    if not cfg["ENABLE_BIRTHDAYS"]:
        await interaction.response.send_message("❌ Birthdays are disabled.", ephemeral=True)
        return

    target = member or interaction.user
    channel = bot.get_channel(cfg["BIRTHDAY_CHANNEL_ID"])
    if not channel:
        await interaction.response.send_message(
            f"❌ Birthday channel not found (ID: `{cfg['BIRTHDAY_CHANNEL_ID']}`). "
            "Set `BIRTHDAY_CHANNEL_ID` in config.txt.", ephemeral=True
        )
        return

    display_name = (
        getattr(target, "nick", None)
        or getattr(target, "global_name", None)
        or target.display_name
        or target.name
    )

    role_ids = _parse_birthday_ping_roles()
    role_pings = " ".join(f"<@&{rid}>" for rid in role_ids) if role_ids else ""
    bday_text = cfg["BIRTHDAY_MESSAGE"].format(mention=target.mention, name=display_name)

    parts = []
    if role_pings:
        parts.append(role_pings)
    parts.append(target.mention)
    ping_line = " ".join(parts)

    try:
        await channel.send(ping_line)
        await channel.send(bday_text)
        await interaction.response.send_message(
            f"✅ Test announcement sent for {target.mention} in <#{channel.id}>.", ephemeral=True
        )
        log("info", f"[BIRTHDAY-TEST] {interaction.user} triggered test for {target} ({target.id})")
    except discord.Forbidden:
        await interaction.response.send_message(
            f"❌ No permission to send in <#{channel.id}>.", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)


@birthday_group.command(
    name="remove-user",
    description="Remove another user's birthday (admin only)"
)
@app_commands.describe(member="The member whose birthday to remove")
@app_commands.default_permissions(administrator=True)
async def birthday_remove_user(interaction: discord.Interaction, member: discord.Member):
    if not cfg["ENABLE_BIRTHDAYS"]:
        await interaction.response.send_message("❌ Birthdays are disabled.", ephemeral=True)
        return

    removed = birthdays.remove(member.id)
    if removed:
        await interaction.response.send_message(
            f"✅ Removed birthday for {member.mention}.", ephemeral=True
        )
        log("info", f"[BIRTHDAY-REMOVE-ADMIN] {interaction.user} removed birthday for {member} ({member.id})")
    else:
        await interaction.response.send_message(
            f"ℹ️ {member.mention} had no birthday set.", ephemeral=True
        )


bot.tree.add_command(birthday_group)


# ============================================================
# VOICE SLASH COMMANDS  (admin-only, guild-scoped)
# ============================================================

@bot.tree.command(
    name="voice-status",
    description="Show voice manager status: connection, sounds, config (admin only)",
    guild=_GUILD,
)
@app_commands.default_permissions(administrator=True)
async def voice_status(interaction: discord.Interaction):
    if not cfg.get("ENABLE_VOICE"):
        await interaction.response.send_message(
            "❌ Voice is disabled. Set `ENABLE_VOICE=true` in config.txt.",
            ephemeral=True,
        )
        return

    if voice_manager is None:
        await interaction.response.send_message(
            "⚠️ VoiceManager not initialised yet (bot may still be starting up).",
            ephemeral=True,
        )
        return

    embed = voice_manager.status_embed()
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(
    name="voice-disconnect",
    description="Force-disconnect the bot from voice in this server (admin only)",
    guild=_GUILD,
)
@app_commands.default_permissions(administrator=True)
async def voice_disconnect(interaction: discord.Interaction):
    if not cfg.get("ENABLE_VOICE"):
        await interaction.response.send_message(
            "❌ Voice is disabled in config.", ephemeral=True
        )
        return

    if voice_manager is None or interaction.guild is None:
        await interaction.response.send_message(
            "⚠️ VoiceManager not available.", ephemeral=True
        )
        return

    disconnected = await voice_manager.disconnect(
        interaction.guild.id, reason=f"forced by {interaction.user}"
    )
    if disconnected:
        log("info", f"[VOICE] Force-disconnected by {interaction.user} ({interaction.user.id})")
        await interaction.response.send_message(
            "✅ Disconnected from voice.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "ℹ️ Bot is not currently in a voice channel.", ephemeral=True
        )


# ============================================================
# DEMOTIVATOR SLASH COMMAND
# ============================================================

@bot.tree.command(
    name="demotivator",
    description="Turn an image into a demotivational poster",
    guild=_GUILD,
)
@app_commands.describe(
    image    = "The image to use as the poster photo",
    title    = "Big title text (e.g. FAILURE)",
    subtitle = "Optional smaller caption below the title",
)
async def demotivator(
    interaction: discord.Interaction,
    image:    discord.Attachment,
    title:    str,
    subtitle: str = "",
):
    # Validate it's actually an image
    if not image.content_type or not image.content_type.startswith("image/"):
        await interaction.response.send_message(
            "❌ That attachment doesn't look like an image.", ephemeral=True
        )
        return

    await interaction.response.defer()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image.url) as resp:
                if resp.status != 200:
                    await interaction.followup.send("❌ Couldn't download the image.")
                    return
                img_bytes = await resp.read()

        photo        = Image.open(io.BytesIO(img_bytes))
        poster_bytes = _build_demotivator(photo, title, subtitle)

        file = discord.File(fp=io.BytesIO(poster_bytes), filename="demotivator.png")
        await interaction.followup.send(file=file)

        log("info", f"[DEMOTIVATOR] {interaction.user} | title={title!r} | sub={subtitle!r}")

    except Exception as e:
        log("error", f"[DEMOTIVATOR] {e}")
        await interaction.followup.send("❌ Something broke while making the poster.")


# ============================================================
# CONTEXT MENU COMMANDS
# ============================================================

# ── GLOBAL: visible in every server the bot is in ────────────────────────
@bot.tree.context_menu(name="Suggest message")
async def suggest_message_ctx(interaction: discord.Interaction, message: discord.Message):
    if not cfg["ENABLE_SUGGESTIONS"]:
        await interaction.response.send_message("❌ Suggestions are disabled.", ephemeral=True)
        return
    if not message.content:
        await interaction.response.send_message("❌ Message has no text content.", ephemeral=True)
        return
    await post_suggestion(interaction, message.content, message.author, message.jump_url)


# ── GUILD-ONLY: visible only in the configured guild ─────────────────────
@bot.tree.context_menu(name="Rape member", guild=_GUILD)
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
    print(f"   Guild ID             : {cfg['GUILD_ID'] if cfg['GUILD_ID'] else '❌ not set (all commands global)'}")
    print(f"   Random msg chance    : 1 in {cfg['RANDOM_MESSAGE_CHANCE']}")
    print(f"   Chicken-out timeout  : {cfg['CHICKEN_OUT_TIMEOUT']}s")
    print(f"   Attention window     : {'✅ ' + str(cfg['ATTENTION_WINDOW_SECONDS']) + 's | debounce ' + str(cfg['LLM_DEBOUNCE_SECONDS']) + 's' if cfg['ENABLE_ATTENTION_WINDOW'] else '❌ ping-only mode'}")
    print(f"   Random messages      : {'✅' if cfg['ENABLE_RANDOM_MESSAGES'] else '❌'}")
    print(f"   Mention responses    : {'✅' if cfg['ENABLE_MENTION_RESPONSES'] else '❌'}")
    print(f"   Auto-thread          : {'✅' if cfg['ENABLE_AUTO_THREAD'] else '❌'}")
    print(f"   Chicken out          : {'✅' if cfg['ENABLE_CHICKEN_OUT'] else '❌'}")
    print(f"   Suggestions          : {'✅' if cfg['ENABLE_SUGGESTIONS'] else '❌'}")
    print(f"   Rape command         : {'✅' if cfg['ENABLE_RAPE_COMMAND'] else '❌'}")
    print(f"   Demotivator          : ✅ /demotivator enabled")
    print(f"   LLM                  : {'✅ ' + cfg['LLM_PROVIDER'].upper() + ' / ' + cfg['LLM_MODEL'] + (' ☁️' if cfg['LLM_PROVIDER'] == 'ollama_cloud' else '') if cfg['ENABLE_LLM'] else '❌ disabled'}")
    print(f"   Context messages     : last {cfg['LLM_CONTEXT_MESSAGES']} channel msgs per response")
    print(f"   Logging              : {'✅ ' + cfg['LOG_DIR'] + '/' + cfg['LOG_FILE'] if cfg['ENABLE_LOGGING'] else '❌ disabled'}")
    print(f"   Shitpost             : {'✅ every ' + str(cfg['SHITPOST_INTERVAL_MINUTES']) + ' min - ch ' + str(cfg['SHITPOST_CHANNEL_ID']) if cfg['ENABLE_SHITPOST'] else '❌ disabled'}")
    hb_url = cfg.get("HEARTBEAT_URL", "").strip()
    print(f"   Heartbeat            : {'✅ every ' + str(cfg['HEARTBEAT_INTERVAL_SECONDS']) + 's → ' + hb_url if hb_url else '❌ disabled'}")
    if cfg["ENABLE_LLM"]:
        pct = cfg["LLM_PERCENTAGE"]
        print(f"   LLM percentage       : {'✅ ' + str(cfg['LLM_PERCENTAGE_VALUE']) + '%' if pct else '❌ always answer'}")
        fallback_msg = cfg.get("LLM_FALLBACK_MSG", "").strip()
        print(f"   LLM fallback msg     : {'✅ custom' if fallback_msg else 'ℹ️  random mention_msg'}")
    if cfg["ENABLE_BIRTHDAYS"]:
        role_ids = _parse_birthday_ping_roles()
        print(f"   Birthdays            : ✅ ch={cfg['BIRTHDAY_CHANNEL_ID']} | "
              f"hour={cfg['BIRTHDAY_CHECK_HOUR']}:00 UTC | "
              f"roles={role_ids or 'none'}")
    else:
        print(f"   Birthdays            : ❌ disabled")

    if cfg.get("ENABLE_VOICE"):
        sounds_folder = BOT_DIR / cfg.get("SOUNDS_FOLDER", "sounds")
        sound_count = len([
            p for p in sounds_folder.iterdir()
            if p.is_file() and p.suffix.lower() in {".mp3", ".ogg", ".wav", ".flac"}
        ]) if sounds_folder.exists() else 0
        print(f"   Voice                : ✅ sounds={sound_count} | "
              f"folder={cfg['SOUNDS_FOLDER']} | "
              f"interval={cfg['VOICE_SOUND_INTERVAL_BASE']}±{cfg['VOICE_SOUND_INTERVAL_VARIANCE']}s | "
              f"alone-timeout={cfg['VOICE_ALONE_DISCONNECT_SECONDS']}s")
    else:
        print(f"   Voice                : ❌ disabled")

    try:
        bot.run(cfg["TOKEN"])
    except discord.LoginFailure:
        print("❌ Login failed - check your TOKEN in config.txt.")
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
