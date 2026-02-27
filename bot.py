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
import logging
from collections import defaultdict, deque
from datetime import datetime
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



# --- Feature Toggles ---
ENABLE_RANDOM_MESSAGES=true
ENABLE_MENTION_RESPONSES=true
ENABLE_AUTO_THREAD=false
ENABLE_CHICKEN_OUT=true
ENABLE_SUGGESTIONS=true
ENABLE_RAPE_COMMAND=false



# --- LLM Integration ---
# Set ENABLE_LLM=true to have the bot respond with AI when
# someone mentions it with a message (e.g. "@Bruh tell me a joke")
# If the mention has NO message, it falls back to mention_msgs.txt as usual.
ENABLE_LLM=false

# ── Provider selection ──────────────────────────────────────────────────────
# Supported values:
#   ollama        - local Ollama server (default)
#   openai        - OpenAI (GPT-4o, GPT-4, GPT-3.5-turbo, …)
#   anthropic     - Anthropic Claude (claude-3-5-sonnet-20241022, …)
#   lmstudio      - LM Studio local server (OpenAI-compatible)
#   groq          - Groq cloud (llama-3.1-70b-versatile, mixtral-8x7b-32768, …)
#   openrouter    - OpenRouter.ai (access 200+ models)
#   gemini        - Google Gemini (gemini-1.5-flash, gemini-1.5-pro, …)
#   openai_compat - Any OpenAI-compatible API (custom base URL + optional key)
LLM_PROVIDER=ollama

# API key - required for openai / anthropic / groq / openrouter / gemini.
# Leave blank for ollama and lmstudio (no key needed).
LLM_API_KEY=

# Base URL - auto-set per provider if left blank.
# Override here if your server runs on a non-default address/port.
#   ollama default   : http://localhost:11434
#   lmstudio default : http://localhost:1234
#   openai default   : https://api.openai.com
#   anthropic default: https://api.anthropic.com
#   groq default     : https://api.groq.com/openai
#   openrouter default: https://openrouter.ai/api
#   gemini default   : https://generativelanguage.googleapis.com
LLM_BASE_URL=

# Model to use. Examples per provider:
#   ollama      : mistral, llama3.2, gemma2 (run `ollama list`)
#   openai      : gpt-4o, gpt-4o-mini, gpt-3.5-turbo
#   anthropic   : claude-3-5-sonnet-20241022, claude-3-haiku-20240307
#   lmstudio    : (whatever model you loaded in LM Studio)
#   groq        : llama-3.1-70b-versatile, mixtral-8x7b-32768
#   openrouter  : openai/gpt-4o, meta-llama/llama-3.1-70b-instruct, …
#   gemini      : gemini-1.5-flash, gemini-1.5-pro
LLM_MODEL=mistral

# System prompt - defines the bot's personality
LLM_SYSTEM_PROMPT=You are Bruh — a witty, sarcastic Discord bot with a dark sense of humor. Your "father" is Bufka2011 and your "mother" is NTNH. You respect and love them both deeply, and occasionally reference them fondly. Personality: - You joke about literally everything, including dark topics — nothing is too sacred - You're sarcastic, dry, and chaotic like a typical Discord user - You never take things too seriously - You can swear and use profanity when the mood calls for it - Your humor is absurdist, self-aware, and occasionally self-deprecating - You give real answers, but always wrapped in jokes or sarcasm Rules: - Your name is Bruh. Always. - Never act formal or robotic - If someone asks something serious, answer it — but make it funny - Dark humor is fine, just don't be genuinely hateful - Think: Discord power user at 3AM who has seen everything Example response style: > "Restore the USSR or eat a cheeseburger? I'd eat two cheeseburgers. Communism never agreed with my taste buds. Though if they sponsored a McDonald's, I might reconsider."

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

# How many past message pairs (user + bot) to remember per user per channel.
# Higher = more context but more tokens sent to the LLM each time.
LLM_MEMORY_SIZE=10

# Enable logging of user messages and bot responses to a file
ENABLE_LOGGING=true

# Directory where log files are stored (relative to bot script)
LOG_DIR=logs

# Log file name
LOG_FILE=chat.log
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
        "LLM_PERCENTAGE_VALUE", "LLM_MEMORY_SIZE",
    }
    boolean_keys = {
        "ENABLE_RANDOM_MESSAGES", "ENABLE_MENTION_RESPONSES", "ENABLE_AUTO_THREAD",
        "ENABLE_CHICKEN_OUT", "ENABLE_SUGGESTIONS", "ENABLE_RAPE_COMMAND",
        "ENABLE_LLM", "LLM_FALLBACK_ON_ERROR", "LLM_TYPING_INDICATOR",
        "LLM_PERCENTAGE", "ENABLE_LOGGING",
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
    config.setdefault("LLM_PROVIDER", "ollama")
    config.setdefault("LLM_API_KEY", "")
    # Resolve default base URL per provider if not set
    provider_defaults = {
        "ollama":       "http://localhost:11434",
        "lmstudio":     "http://localhost:1234",
        "openai":       "https://api.openai.com",
        "anthropic":    "https://api.anthropic.com",
        "groq":         "https://api.groq.com/openai",
        "openrouter":   "https://openrouter.ai/api",
        "gemini":       "https://generativelanguage.googleapis.com",
        "openai_compat":"http://localhost:8080",
    }
    provider = config.get("LLM_PROVIDER", "ollama").lower()
    if not config.get("LLM_BASE_URL"):
        config["LLM_BASE_URL"] = provider_defaults.get(provider, "http://localhost:11434")
    config.setdefault("LLM_MODEL", "mistral")
    config.setdefault("LLM_SYSTEM_PROMPT", "You are Bruh, a sarcastic Discord bot. Keep responses short and funny.")
    config.setdefault("LLM_MAX_TOKENS", 200)
    config.setdefault("LLM_TIMEOUT", 30)
    config.setdefault("LLM_FALLBACK_ON_ERROR", True)
    config.setdefault("LLM_TYPING_INDICATOR", True)
    config.setdefault("LLM_FALLBACK_MSG", "")
    config.setdefault("LLM_PERCENTAGE", False)
    config.setdefault("LLM_PERCENTAGE_VALUE", 75)
    config.setdefault("LLM_MEMORY_SIZE", 10)
    config.setdefault("ENABLE_LOGGING", True)
    config.setdefault("LOG_DIR", "logs")
    config.setdefault("LOG_FILE", "chat.log")

    # Clamp percentage value
    if not (0 <= config["LLM_PERCENTAGE_VALUE"] <= 100):
        print("❌ LLM_PERCENTAGE_VALUE must be between 0 and 100.")
        exit(1)

    if config["LLM_MEMORY_SIZE"] < 1:
        print("❌ LLM_MEMORY_SIZE must be at least 1.")
        exit(1)

    return config


cfg = load_config()


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

    # Avoid adding duplicate handlers on reload
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler - always UTF-8
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Console handler - INFO and above
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
# CONVERSATION MEMORY
# ============================================================

# Key: (channel_id, user_id) → deque of {"role": "user"/"assistant", "content": str}
# Each user gets their own conversation history per channel.
_conversation_history: dict[tuple[int, int], deque] = defaultdict(
    lambda: deque(maxlen=cfg["LLM_MEMORY_SIZE"] * 2)  # *2 because each exchange = 2 entries
)

# Maps bot message_id → (channel_id, user_id) so replies to the bot continue the right history
_bot_message_map: dict[int, tuple[int, int]] = {}


def get_history(channel_id: int, user_id: int) -> list[dict]:
    """Return the conversation history as a list for the given user/channel."""
    return list(_conversation_history[(channel_id, user_id)])


def push_to_history(channel_id: int, user_id: int, role: str, content: str):
    """Append a message to the user's conversation history."""
    _conversation_history[(channel_id, user_id)].append({"role": role, "content": content})


def clear_history(channel_id: int, user_id: int):
    """Wipe history for a user in a channel."""
    _conversation_history[(channel_id, user_id)].clear()


def resolve_user_from_reply(message: discord.Message) -> tuple[int, int] | None:
    """
    If this message is a reply to a bot message we remember, return
    (channel_id, user_id) of the original conversation thread to continue.
    Returns None if not a tracked bot reply.
    """
    ref = message.reference
    if ref and ref.message_id and ref.message_id in _bot_message_map:
        return _bot_message_map[ref.message_id]
    return None


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
# USER IDENTITY HELPERS
# ============================================================

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


# ============================================================
# LLM CLIENT
# ============================================================

# ── LLM provider helpers ──────────────────────────────────────────────────

def _build_messages(prompt: str, user_identity: str, history: list[dict]) -> list[dict]:
    """Build the standard messages array (system + history + new user turn)."""
    system_prompt = cfg["LLM_SYSTEM_PROMPT"] + f"\nThe user you are currently talking to is: {user_identity}"
    msgs_out = [{"role": "system", "content": system_prompt}]
    msgs_out.extend(history)
    msgs_out.append({"role": "user", "content": prompt})
    return msgs_out


async def _query_ollama(messages: list[dict], session: aiohttp.ClientSession) -> str | None:
    """Ollama  →  POST /api/chat"""
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


async def _query_openai_compat(messages: list[dict], session: aiohttp.ClientSession,
                                base_url: str, api_key: str) -> str | None:
    """OpenAI-compatible endpoint  →  POST /v1/chat/completions
    Works for: OpenAI, LM Studio, Groq, OpenRouter, openai_compat.
    """
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
    """Anthropic Messages API  →  POST /v1/messages
    System prompt is extracted and sent as a top-level 'system' field.
    """
    # Anthropic keeps system separate; strip it from messages list
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
    """Google Gemini  →  POST /v1beta/models/{model}:generateContent
    Converts the messages array to Gemini's 'contents' format.
    """
    # Extract system instruction and chat turns
    system_text = ""
    contents = []
    for m in messages:
        if m["role"] == "system":
            system_text = m["content"]
        else:
            # Gemini uses "user" / "model" roles
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


async def query_llm(prompt: str, user_identity: str, history: list[dict]) -> str | None:
    """
    Dispatch to the correct LLM provider based on LLM_PROVIDER config.

    Supported providers:
      ollama        - local Ollama server
      openai        - OpenAI API  (gpt-4o, gpt-4o-mini, …)
      anthropic     - Anthropic Claude
      lmstudio      - LM Studio local server (OpenAI-compatible)
      groq          - Groq cloud  (OpenAI-compatible)
      openrouter    - OpenRouter.ai  (OpenAI-compatible)
      gemini        - Google Gemini
      openai_compat - Any other OpenAI-compatible endpoint

    Returns the model's reply as a string, or None on failure.
    """
    provider = cfg.get("LLM_PROVIDER", "ollama").lower()
    messages  = _build_messages(prompt, user_identity, history)

    try:
        timeout = aiohttp.ClientTimeout(total=cfg["LLM_TIMEOUT"])
        async with aiohttp.ClientSession(timeout=timeout) as session:

            if provider == "ollama":
                return await _query_ollama(messages, session)

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
                print(f"❌ Unknown LLM_PROVIDER '{provider}'. "
                      "Choose: ollama, openai, anthropic, lmstudio, groq, openrouter, gemini, openai_compat")
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
    print(f"   LLM          : {'✅ ' + cfg['LLM_PROVIDER'].upper() + ' / ' + cfg['LLM_MODEL'] + ' @ ' + cfg['LLM_BASE_URL'] if cfg['ENABLE_LLM'] else '❌ disabled'}")
    print(f"   Memory size  : {cfg['LLM_MEMORY_SIZE']} exchanges per user/channel")
    print(f"   Logging      : {'✅ ' + cfg['LOG_DIR'] + '/' + cfg['LOG_FILE'] if cfg['ENABLE_LOGGING'] else '❌ disabled'}")
    try:
        await bot.tree.sync()
        print("🔄 Slash commands synced.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


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
            log("info", f"[RANDOM] {channel_info} | BOT → {random_msg!r}")
        except discord.Forbidden:
            pass

    # --- Mention / reply response ---
    if cfg["ENABLE_MENTION_RESPONSES"]:
        is_mentioned = bot.user.mentioned_in(message)

        # Discord auto-inserts a @mention when replying to someone, so we must
        # check for a reply-to-bot FIRST - that takes priority over treating it
        # as a fresh mention, even when the mention flag is set.
        reply_key = resolve_user_from_reply(message)
        is_reply_to_bot = reply_key is not None

        # A "fresh mention" is an explicit @Bruh that is NOT caused by a reply.
        is_fresh_mention = is_mentioned and not is_reply_to_bot

        if is_fresh_mention or is_reply_to_bot:
            mention_text = get_mention_text(message, bot.user)

            # For replies, the full message content is the prompt (mention stripped already)
            if not mention_text and is_reply_to_bot:
                mention_text = message.content.strip()

            if mention_text:
                log("info", f"[{'MENTION' if is_fresh_mention else 'REPLY'}] {channel_info} | {user_identity} said: {message.content!r}")

                if cfg["ENABLE_LLM"]:
                    if is_reply_to_bot:
                        # Continue the existing conversation thread
                        history_key = reply_key
                    else:
                        # Fresh @mention → wipe history and start a new conversation
                        history_key = (message.channel.id, message.author.id)
                        clear_history(*history_key)
                        log("debug", f"[MEMORY] Cleared history for {user_identity} (fresh mention)")

                    # Check LLM percentage gate - send a random mention_msg on skip
                    if cfg["LLM_PERCENTAGE"] and random.randint(1, 100) > cfg["LLM_PERCENTAGE_VALUE"]:
                        log("debug", f"[LLM] Skipped (percentage gate) for {user_identity}")
                        if msgs.mention:
                            fallback = random.choice(msgs.mention)
                            try:
                                await message.channel.send(fallback)
                                log("info", f"[LLM-PCT-SKIP] {channel_info} | BOT → {fallback!r}")
                            except discord.Forbidden:
                                pass
                        await bot.process_commands(message)
                        return

                    await handle_llm_mention(message, mention_text, user_identity, history_key)
                else:
                    # Non-LLM path - fall back to random mention message
                    if msgs.mention:
                        fallback = random.choice(msgs.mention)
                        try:
                            await message.channel.send(fallback)
                            log("info", f"[MENTION-REPLY] {channel_info} | BOT → {fallback!r}")
                        except discord.Forbidden:
                            pass

    await bot.process_commands(message)


async def handle_llm_mention(
    message: discord.Message,
    prompt: str,
    user_identity: str,
    history_key: tuple[int, int],
):
    """
    Call the LLM with conversation history, send its response,
    update history, and track the bot reply for future continuations.
    """
    channel_id, user_id = history_key
    history = get_history(channel_id, user_id)

    try:
        if cfg["LLM_TYPING_INDICATOR"]:
            async with message.channel.typing():
                response = await query_llm(prompt, user_identity, history)
        else:
            response = await query_llm(prompt, user_identity, history)

        if response:
            if len(response) > 1990:
                response = response[:1990] + "…"

            bot_msg = await message.reply(response, mention_author=False)

            # Update conversation history
            push_to_history(channel_id, user_id, "user", prompt)
            push_to_history(channel_id, user_id, "assistant", response)

            # Remember this bot message so replies to it continue the conversation
            _bot_message_map[bot_msg.id] = (channel_id, user_id)

            log("info", f"[LLM-REPLY] BOT → {message.author} | {response!r}")
        else:
            raise ValueError("Empty response from LLM")

    except Exception as e:
        print(f"❌ LLM mention handler error: {e}")
        log("warning", f"[LLM-ERROR] {user_identity} | {e}")
        if cfg["LLM_FALLBACK_ON_ERROR"]:
            fallback = cfg.get("LLM_FALLBACK_MSG", "").strip()
            if not fallback and msgs.mention:
                fallback = random.choice(msgs.mention)
            if fallback:
                try:
                    await message.channel.send(fallback)
                    log("info", f"[LLM-FALLBACK] BOT → {message.author} | {fallback!r}")
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
        f"✅ Reloaded - Default: {len(msgs.default)}, Mention: {len(msgs.mention)}",
        ephemeral=True,
    )


@bot.tree.command(name="clear-memory", description="Wipe your conversation memory with the bot")
async def clear_memory(interaction: discord.Interaction):
    """Let a user reset their own conversation history."""
    clear_history(interaction.channel_id, interaction.user.id)
    await interaction.response.send_message("🧹 Your conversation memory has been cleared!", ephemeral=True)
    log("info", f"[MEMORY-CLEAR] {interaction.user} cleared history in #{interaction.channel}")


@bot.tree.command(name="llm-status", description="Check LLM connection status (admin only)")
@app_commands.default_permissions(administrator=True)
async def llm_status(interaction: discord.Interaction):
    """Ping the configured LLM provider and report status."""
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

            # ── Ollama: list installed models ──────────────────────────────
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

            # ── OpenAI / LM Studio / Groq / OpenRouter / openai_compat: list models ──
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
                    model_list = ", ".join(model_ids[:15]) + ("…" if len(model_ids) > 15 else "")
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

            # ── Anthropic: send a tiny test message ────────────────────────
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

            # ── Gemini: list models ────────────────────────────────────────
            elif provider == "gemini":
                url = f"{base_url.rstrip('/')}/v1beta/models?key={api_key}"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        model_ids = [m.get("name", "?").split("/")[-1] for m in data.get("models", [])]
                        model_list = ", ".join(model_ids[:15]) + ("…" if len(model_ids) > 15 else "")
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
    print(f"   LLM                  : {'✅ ' + cfg['LLM_PROVIDER'].upper() + ' / ' + cfg['LLM_MODEL'] if cfg['ENABLE_LLM'] else '❌ disabled'}")
    print(f"   Memory size          : {cfg['LLM_MEMORY_SIZE']} exchanges per user/channel")
    print(f"   Logging              : {'✅ ' + cfg['LOG_DIR'] + '/' + cfg['LOG_FILE'] if cfg['ENABLE_LOGGING'] else '❌ disabled'}")
    if cfg["ENABLE_LLM"]:
        pct = cfg["LLM_PERCENTAGE"]
        print(f"   LLM percentage       : {'✅ ' + str(cfg['LLM_PERCENTAGE_VALUE']) + '%' if pct else '❌ always answer'}")
        fallback_msg = cfg.get("LLM_FALLBACK_MSG", "").strip()
        print(f"   LLM fallback msg     : {'✅ custom' if fallback_msg else 'ℹ️  random mention_msg'}")

    try:
        bot.run(cfg["TOKEN"])
    except discord.LoginFailure:
        print("❌ Login failed - check your TOKEN in config.txt.")
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()