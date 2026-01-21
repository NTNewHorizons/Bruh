"""
Bruh Bot - A fun Discord bot for random responses and community interactions
Single-file implementation with all features preserved
"""
import discord
import random
import asyncio
import os
import pathlib
import traceback
from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands

# ======================
# CONFIGURATION MANAGEMENT
# ======================

def create_config_template(filename):
    """Create a template config file with example values"""
    template = """# Bruh Bot Configuration File
# Fill in the values below with your actual configuration

# ===== CORE SETTINGS =====
# Discord Bot Token (REQUIRED)
TOKEN=YOUR_BOT_TOKEN_HERE

# ===== MESSAGE FILES =====
# File path for default messages
DEFAULT_MSGS_FILE=default_msgs.txt
# File path for mention messages
MENTION_MSGS_FILE=mention_msgs.txt
# File path for default audio messages (file paths or Discord attachment URLs)
DEFAULT_AUDIO_MSGS_FILE=default_audio_msgs.txt
# File path for mention audio messages (file paths or Discord attachment URLs)
MENTION_AUDIO_MSGS_FILE=mention_audio_msgs.txt

# ===== CHANNEL IDS =====
# Channel for message suggestions
SUGGESTION_CHANNEL_ID=
# Channel for the "rape" command
RAPE_CHANNEL_ID=
# Channel for special message handling (auto-thread creation)
SPECIAL_MESSAGE_CHANNEL_ID=
# Channel for "chicken out" notifications
CHICKEN_OUT_CHANNEL_ID=

# ===== ROLE IDS =====
# Role to mention when a message is suggested
SUGGESTION_PING_ROLE_ID=

# ===== BOT BEHAVIORS =====
# Chance (1 in X) to send a random default message (e.g., 100 = 1% chance)
RANDOM_MESSAGE_CHANCE=100
# Chance (1 in X) to send a random default audio message (e.g., 200 = 0.5% chance)
RANDOM_AUDIO_MESSAGE_CHANCE=200
# Time between auto-reloading messages from files (in seconds)
MESSAGE_RELOAD_INTERVAL=300
# Time window for "chicken out" detection after joining (in seconds)
CHICKEN_OUT_TIMEOUT=900
# Message to send when someone chickens out
CHICKENED_OUT_MSG=https://tenor.com/view/walk-away-gif-8390063

# ===== PERMISSIONS =====
# Authorized user ID for approving/declining suggestions (numeric ID)
AUTHORIZED_USER_ID=

# ===== FEATURE TOGGLES =====
# Enable/disable random message responses
ENABLE_RANDOM_MESSAGES=true
# Enable/disable random audio message responses
ENABLE_RANDOM_AUDIO_MESSAGES=false
# Enable/disable mention responses
ENABLE_MENTION_RESPONSES=true
# Enable/disable mention audio responses
ENABLE_MENTION_AUDIO_RESPONSES=false
# Enable/disable special channel auto-threading
ENABLE_SPECIAL_CHANNEL=false
# Enable/disable chicken out detection
ENABLE_CHICKEN_OUT=true
# Enable/disable message suggestion system
ENABLE_SUGGESTIONS=true
# Enable/disable rape command
ENABLE_RAPE_COMMAND=false

# ===== SUGGESTION BUTTON EMOJIS =====
# Emoji for reject button
REJECT_BUTTON_EMOJI=🗑️
REJECT_BUTTON_LABEL=❌ Reject
# Emoji for default list button
DEFAULT_BUTTON_EMOJI=📌
DEFAULT_BUTTON_LABEL=✅ Default
# Emoji for mention list button
MENTION_BUTTON_EMOJI=👋
MENTION_BUTTON_LABEL=✅ Mention
# Emoji for both lists button
BOTH_BUTTON_EMOJI=✨
BOTH_BUTTON_LABEL=✅ Both
# Emoji for default audio list button
DEFAULT_AUDIO_BUTTON_EMOJI=🎙️
DEFAULT_AUDIO_BUTTON_LABEL=✅ Default Audio
# Emoji for mention audio list button
MENTION_AUDIO_BUTTON_EMOJI=🎤
MENTION_AUDIO_BUTTON_LABEL=✅ Mention Audio
# Emoji for both audio lists button
BOTH_AUDIO_BUTTON_EMOJI=🎵
BOTH_AUDIO_BUTTON_LABEL=✅ Both Audio

# ===== SPECIAL CHANNEL REACTION EMOJIS =====
# Custom emoji for special channel reactions (use <:name:id> format or leave empty for standard reactions)
SPECIAL_CHANNEL_YES_EMOJI=
SPECIAL_CHANNEL_NO_EMOJI=

# ===== LOGGING MESSAGES =====
# Messages for various events (use {user}, {member}, {channel}, {role} as placeholders)
RANDOM_MESSAGE_LOG=Random message sent
MENTION_RESPONSE_LOG=Responded to mention
SUGGESTION_RECEIVED_LOG=Suggestion received
RAPE_LOG={user} raped {member}
CHICKEN_OUT_LOG={user} chickened out
MEMBER_JOIN_LOG={user} joined the server
MEMBER_LEAVE_LOG={user} left the server

# ===== COLORS (HEX format without #) =====
# Color for suggestion embed
SUGGESTION_EMBED_COLOR=0x0099ff
# Color for success messages
SUCCESS_COLOR=00aa00
# Color for error messages
ERROR_COLOR=ff0000
# Color for warning messages
WARNING_COLOR=ffaa00
"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template)

def load_config():
    """Load configuration from config.txt and validate all required fields"""
    config = {}
    config_file = 'config.txt'
    
    # Create template if config doesn't exist
    if not os.path.exists(config_file):
        print(f"❌ Config file '{config_file}' not found! Creating template...")
        create_config_template(config_file)
        print(f"✅ Template config file created. Please fill in your values and restart the bot.")
        exit(1)
    
    # Read config file
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Strip surrounding quotes if present
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    # Convert numeric fields to integers
                    numeric_fields = ['AUTHORIZED_USER_ID', 'SUGGESTION_CHANNEL_ID', 'RAPE_CHANNEL_ID',
                                      'SPECIAL_MESSAGE_CHANNEL_ID', 'CHICKEN_OUT_CHANNEL_ID',
                                      'SUGGESTION_PING_ROLE_ID', 'RANDOM_MESSAGE_CHANCE',
                                      'RANDOM_AUDIO_MESSAGE_CHANCE', 'MESSAGE_RELOAD_INTERVAL', 
                                      'CHICKEN_OUT_TIMEOUT']
                    
                    # Convert boolean fields
                    boolean_fields = ['ENABLE_RANDOM_MESSAGES', 'ENABLE_RANDOM_AUDIO_MESSAGES',
                                     'ENABLE_MENTION_RESPONSES', 'ENABLE_MENTION_AUDIO_RESPONSES',
                                     'ENABLE_SPECIAL_CHANNEL', 'ENABLE_CHICKEN_OUT',
                                     'ENABLE_SUGGESTIONS', 'ENABLE_RAPE_COMMAND']
                    
                    if key in numeric_fields:
                        try:
                            config[key] = int(value) if value else 0
                        except ValueError:
                            print(f"❌ Error: {key} must be a number, but got '{value}'")
                            print(f"Please fix this in {config_file}")
                            exit(1)
                    elif key in boolean_fields:
                        config[key] = value.lower() in ['true', '1', 'yes', 'on']
                    else:
                        config[key] = value
    except IOError as e:
        print(f"❌ Error reading {config_file}: {e}")
        exit(1)
    
    # Validate required fields
    required_fields = ['TOKEN', 'DEFAULT_MSGS_FILE', 'MENTION_MSGS_FILE',
                      'DEFAULT_AUDIO_MSGS_FILE', 'MENTION_AUDIO_MSGS_FILE',
                      'SUGGESTION_CHANNEL_ID', 'RAPE_CHANNEL_ID', 'SPECIAL_MESSAGE_CHANNEL_ID',
                      'CHICKEN_OUT_CHANNEL_ID', 'SUGGESTION_PING_ROLE_ID', 'RANDOM_MESSAGE_CHANCE',
                      'RANDOM_AUDIO_MESSAGE_CHANCE', 'MESSAGE_RELOAD_INTERVAL', 'CHICKEN_OUT_TIMEOUT', 
                      'CHICKENED_OUT_MSG', 'AUTHORIZED_USER_ID']
    
    missing_fields = [field for field in required_fields if field not in config]
    if missing_fields:
        print(f"❌ Missing required configuration fields:")
        for field in missing_fields:
            print(f"   - {field}")
        print(f"\nPlease check your {config_file} file and ensure all required fields are set.")
        print(f"Creating updated template...")
        create_config_template(config_file)
        exit(1)
    
    # Validate token
    if config['TOKEN'] == 'YOUR_BOT_TOKEN_HERE' or not config['TOKEN']:
        print(f"❌ Invalid TOKEN in {config_file}")
        print(f"Please set TOKEN to your actual Discord bot token.")
        print(f"Get your token from: https://discord.com/developers/applications")
        exit(1)
    
    # Validate numeric values are reasonable
    if config['RANDOM_MESSAGE_CHANCE'] < 1:
        print(f"❌ RANDOM_MESSAGE_CHANCE must be at least 1, got {config['RANDOM_MESSAGE_CHANCE']}")
        exit(1)
    if config['RANDOM_AUDIO_MESSAGE_CHANCE'] < 1:
        print(f"❌ RANDOM_AUDIO_MESSAGE_CHANCE must be at least 1, got {config['RANDOM_AUDIO_MESSAGE_CHANCE']}")
        exit(1)
    if config['MESSAGE_RELOAD_INTERVAL'] < 1:
        print(f"❌ MESSAGE_RELOAD_INTERVAL must be at least 1 second, got {config['MESSAGE_RELOAD_INTERVAL']}")
        exit(1)
    if config['CHICKEN_OUT_TIMEOUT'] < 1:
        print(f"❌ CHICKEN_OUT_TIMEOUT must be at least 1 second, got {config['CHICKEN_OUT_TIMEOUT']}")
        exit(1)
    
    if config['AUTHORIZED_USER_ID'] == 0:
        print(f"⚠️ Warning: AUTHORIZED_USER_ID is not set (0). No one will be able to approve suggestions!")
    
    # Set default values for optional fields
    optional_defaults = {
        'ENABLE_RANDOM_MESSAGES': True,
        'ENABLE_RANDOM_AUDIO_MESSAGES': False,
        'ENABLE_MENTION_RESPONSES': True,
        'ENABLE_MENTION_AUDIO_RESPONSES': False,
        'ENABLE_SPECIAL_CHANNEL': False,
        'ENABLE_CHICKEN_OUT': True,
        'ENABLE_SUGGESTIONS': True,
        'ENABLE_RAPE_COMMAND': False,
        'REJECT_BUTTON_EMOJI': '🗑️',
        'REJECT_BUTTON_LABEL': '❌ Reject',
        'DEFAULT_BUTTON_EMOJI': '📌',
        'DEFAULT_BUTTON_LABEL': '✅ Default',
        'MENTION_BUTTON_EMOJI': '👋',
        'MENTION_BUTTON_LABEL': '✅ Mention',
        'BOTH_BUTTON_EMOJI': '✨',
        'BOTH_BUTTON_LABEL': '✅ Both',
        'DEFAULT_AUDIO_BUTTON_EMOJI': '🎙️',
        'DEFAULT_AUDIO_BUTTON_LABEL': '✅ Default Audio',
        'MENTION_AUDIO_BUTTON_EMOJI': '🎤',
        'MENTION_AUDIO_BUTTON_LABEL': '✅ Mention Audio',
        'BOTH_AUDIO_BUTTON_EMOJI': '🎵',
        'BOTH_AUDIO_BUTTON_LABEL': '✅ Both Audio',
        'SPECIAL_CHANNEL_YES_EMOJI': '',
        'SPECIAL_CHANNEL_NO_EMOJI': '',
        'SUGGESTION_EMBED_COLOR': '0x0099ff',
        'SUCCESS_COLOR': '00aa00',
        'ERROR_COLOR': 'ff0000',
        'WARNING_COLOR': 'ffaa00',
    }
    
    for key, default_value in optional_defaults.items():
        if key not in config:
            config[key] = default_value
    
    return config

# Load configuration
config = load_config()

# ======================
# MESSAGE MANAGEMENT
# ======================

class MessageManager:
    """Centralized manager for all message lists (text and audio)"""
    
    def __init__(self):
        self.bot_root_dir = pathlib.Path(__file__).parent.resolve()
        self.default = []
        self.mention = []
        self.default_audio = []
        self.mention_audio = []
        self._load_all()
    
    def _load_file(self, filename):
        """Load messages from file with automatic creation if missing"""
        try:
            # Resolve path relative to bot directory
            file_path = self.bot_root_dir / filename
            
            if not file_path.exists():
                print(f"ℹ️  Creating new file: {file_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('')
            
            with open(file_path, 'r', encoding='utf-8') as f:
                # Filter out empty lines and comments starting with #
                msgs = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
                print(f"✅ Loaded {len(msgs)} messages from {file_path}")
                return msgs
        except IOError as e:
            print(f"❌ Error reading {filename}: {e}")
            return []
    
    def _save_file(self, filename, msgs):
        """Save messages to file"""
        try:
            # Resolve path relative to bot directory
            file_path = self.bot_root_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                for msg in msgs:
                    f.write(f"{msg}\n")
            print(f"✅ Saved {len(msgs)} messages to {file_path}")
        except IOError as e:
            print(f"❌ Error writing to {filename}: {e}")
    
    def _load_all(self):
        """Load all message lists from files"""
        self.default = self._load_file(config['DEFAULT_MSGS_FILE'])
        self.mention = self._load_file(config['MENTION_MSGS_FILE'])
        self.default_audio = self._load_file(config['DEFAULT_AUDIO_MSGS_FILE'])
        self.mention_audio = self._load_file(config['MENTION_AUDIO_MSGS_FILE'])
    
    def reload(self):
        """Reload all message lists from files"""
        self._load_all()
        counts = self.get_counts()
        print(f"🔄 Reloaded messages: Default={counts['default']}, Mention={counts['mention']}, "
              f"Default Audio={counts['default_audio']}, Mention Audio={counts['mention_audio']}")
    
    def add_to_list(self, msg, list_type):
        """Add message to specified list (default/mention/default_audio/mention_audio)"""
        list_map = {
            'default': self.default,
            'mention': self.mention,
            'default_audio': self.default_audio,
            'mention_audio': self.mention_audio
        }
        
        filename_map = {
            'default': config['DEFAULT_MSGS_FILE'],
            'mention': config['MENTION_MSGS_FILE'],
            'default_audio': config['DEFAULT_AUDIO_MSGS_FILE'],
            'mention_audio': config['MENTION_AUDIO_MSGS_FILE']
        }
        
        if list_type not in list_map:
            return False
        
        msgs = list_map[list_type]
        if msg in msgs:
            return False
        
        msgs.append(msg)
        self._save_file(filename_map[list_type], msgs)
        return True
    
    def get_counts(self):
        """Get message counts for all lists"""
        return {
            'default': len(self.default),
            'mention': len(self.mention),
            'default_audio': len(self.default_audio),
            'mention_audio': len(self.mention_audio)
        }

# Initialize message manager
msg_manager = MessageManager()

# ======================
# UTILITY FUNCTIONS
# ======================

def create_suggestion_embed(interaction, msg_content, message_author=None, message_url=None):
    """Create an embed for message suggestion"""
    embed = discord.Embed(
        title="New Proposed Message Suggestion",
        description=f"User {interaction.user.mention} suggests this message for the bot:",
        color=discord.Color(int(config['SUGGESTION_EMBED_COLOR'], 16)),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="📝 Message Content", value=msg_content, inline=False)
    
    if message_author:
        embed.add_field(name="📤 Original Author", value=f"{message_author.mention}", inline=True)
    if message_url:
        embed.add_field(name="🔗 Message Link", value=f"[Jump to Message]({message_url})", inline=True)
    
    embed.set_footer(text=f"Suggested by {interaction.user.name} | User ID: {interaction.user.id}")
    return embed

async def send_audio_message(channel, audio_source):
    """Send an audio message with proper path resolution"""
    try:
        # Handle URLs directly
        if audio_source.startswith(('http://', 'https://')):
            await channel.send(audio_source)
            return
        
        # Resolve relative paths properly
        audio_path = pathlib.Path(audio_source)
        
        # If it's not an absolute path, make it relative to bot directory
        if not audio_path.is_absolute():
            audio_path = msg_manager.bot_root_dir / audio_path
        
        # Convert to string for Discord.py
        audio_path_str = str(audio_path.resolve())
        
        # Check if file exists
        if not os.path.exists(audio_path_str):
            print(f"⚠️ Audio file not found at: {audio_path_str}")
            print(f"   Relative path was: {audio_source}")
            print(f"   Bot root directory: {msg_manager.bot_root_dir}")
            return
        
        # Get file size check (Discord has 25MB limit)
        file_size = os.path.getsize(audio_path_str)
        if file_size > 25 * 1024 * 1024:  # 25MB
            print(f"❌ Audio file too large ({file_size / 1024 / 1024:.1f}MB): {audio_path_str}")
            await channel.send(f"❌ Audio file too large to send (max 25MB): `{os.path.basename(audio_path_str)}`")
            return
        
        # Send the file
        await channel.send(file=discord.File(audio_path_str))
        print(f"✅ Sent audio file: {audio_path_str}")
        
    except discord.Forbidden:
        print(f"❌ No permission to send messages in #{channel.name}")
    except Exception as e:
        print(f"❌ Error sending audio message from {audio_source}: {e}")
        print(f"   Full path attempted: {audio_path_str if 'audio_path_str' in locals() else 'not resolved'}")

# ======================
# BOT SETUP AND COGS
# ======================

# Discord intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Recent joins tracking for chicken out detection
recent_joins = {}

bot = commands.Bot(command_prefix=config['COMMAND_PREFIX'], intents=intents)

# ======================
# SUGGESTION VIEW
# ======================

class MsgSuggestionView(View):
    """View with buttons for accepting/rejecting message suggestions"""
    
    def __init__(self, msg_content, message_id):
        super().__init__(timeout=None)
        self.msg_content = msg_content
        self.message_id = message_id
    
    async def _check_auth(self, interaction):
        """Check authorization and handle failure"""
        if interaction.user.id != config['AUTHORIZED_USER_ID']:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red, emoji="🗑️")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n❌ **Rejected by {interaction.user.mention}**",
            embed=None,
            view=None
        )
        await interaction.response.defer()
    
    @discord.ui.button(label="✅ Default", style=discord.ButtonStyle.green, emoji="📌")
    async def accept_default_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        
        added = msg_manager.add_to_list(self.msg_content, 'default')
        status = "✅ Message added to default list!" if added else "⚠️ This message is already in the default list!"
        
        await interaction.response.send_message(status, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n✅ **Accepted for Default by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Mention", style=discord.ButtonStyle.green, emoji="👋")
    async def accept_mention_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        
        added = msg_manager.add_to_list(self.msg_content, 'mention')
        status = "✅ Message added to mention list!" if added else "⚠️ This message is already in the mention list!"
        
        await interaction.response.send_message(status, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n✅ **Accepted for Mention by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Both", style=discord.ButtonStyle.blurple, emoji="✨")
    async def accept_both_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        
        added_default = msg_manager.add_to_list(self.msg_content, 'default')
        added_mention = msg_manager.add_to_list(self.msg_content, 'mention')
        
        if not added_default and not added_mention:
            status = "⚠️ This message was already in both lists!"
        elif added_default and added_mention:
            status = "✅ Message added to both lists!"
        elif added_default:
            status = "✅ Message added to default list! (Already in mention list)"
        else:
            status = "✅ Message added to mention list! (Already in default list)"
        
        await interaction.response.send_message(status, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n✅ **Accepted for Both by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Default Audio", style=discord.ButtonStyle.green, emoji="🎙️")
    async def accept_default_audio_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        
        added = msg_manager.add_to_list(self.msg_content, 'default_audio')
        status = "✅ Message added to default audio list!" if added else "⚠️ This message is already in the default audio list!"
        
        await interaction.response.send_message(status, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n✅ **Accepted for Default Audio by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Mention Audio", style=discord.ButtonStyle.green, emoji="🎤")
    async def accept_mention_audio_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        
        added = msg_manager.add_to_list(self.msg_content, 'mention_audio')
        status = "✅ Message added to mention audio list!" if added else "⚠️ This message is already in the mention audio list!"
        
        await interaction.response.send_message(status, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n✅ **Accepted for Mention Audio by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Both Audio", style=discord.ButtonStyle.blurple, emoji="🎵")
    async def accept_both_audio_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        
        added_default = msg_manager.add_to_list(self.msg_content, 'default_audio')
        added_mention = msg_manager.add_to_list(self.msg_content, 'mention_audio')
        
        if not added_default and not added_mention:
            status = "⚠️ This message was already in both audio lists!"
        elif added_default and added_mention:
            status = "✅ Message added to both audio lists!"
        elif added_default:
            status = "✅ Message added to default audio list! (Already in mention audio list)"
        else:
            status = "✅ Message added to mention audio list! (Already in default audio list)"
        
        await interaction.response.send_message(status, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n✅ **Accepted for Both Audio by {interaction.user.mention}**",
            embed=None,
            view=None
        )

# ======================
# EVENT HANDLERS
# ======================

@bot.event
async def on_ready():
    """Bot ready event"""
    print(f'✅ {bot.user.name} (Bruh) is online and ready!')
    
    counts = msg_manager.get_counts()
    print(f'📊 Initial message counts: Default={counts["default"]}, Mention={counts["mention"]}, '
          f'Default Audio={counts["default_audio"]}, Mention Audio={counts["mention_audio"]}')
    
    if counts['default'] == 0 and config['ENABLE_RANDOM_MESSAGES']:
        print(f"⚠️  Warning: No default messages loaded, but random messages are enabled.")
    if counts['mention'] == 0 and config['ENABLE_MENTION_RESPONSES']:
        print(f"⚠️  Warning: No mention messages loaded, but mention responses are enabled.")
    if counts['default_audio'] == 0 and config['ENABLE_RANDOM_AUDIO_MESSAGES']:
        print(f"⚠️  Warning: No default audio messages loaded, but random audio messages are enabled.")
    if counts['mention_audio'] == 0 and config['ENABLE_MENTION_AUDIO_RESPONSES']:
        print(f"⚠️  Warning: No mention audio messages loaded, but mention audio responses are enabled.")
    
    # Verify all configured channels exist
    channels_to_check = [
        (config['SUGGESTION_CHANNEL_ID'], "Suggestion channel"),
        (config['RAPE_CHANNEL_ID'], "Rape command channel"),
        (config['SPECIAL_MESSAGE_CHANNEL_ID'], "Special message channel"),
        (config['CHICKEN_OUT_CHANNEL_ID'], "Chicken out channel")
    ]
    
    for channel_id, channel_name in channels_to_check:
        channel = bot.get_channel(channel_id)
        if channel:
            print(f"✅ {channel_name} found: #{channel.name}")
        else:
            print(f"❌ {channel_name} NOT FOUND (ID: {channel_id}). Please check your config!")
    
    # Verify role exists
    suggestion_role = None
    for guild in bot.guilds:
        suggestion_role = guild.get_role(config['SUGGESTION_PING_ROLE_ID'])
        if suggestion_role:
            print(f"✅ Suggestion ping role found: @{suggestion_role.name}")
            break
    
    if not suggestion_role:
        print(f"❌ Suggestion ping role NOT FOUND (ID: {config['SUGGESTION_PING_ROLE_ID']}). Please check your config!")
    
    # Sync command tree
    try:
        await bot.tree.sync()
        print('🔄 Command tree synced successfully')
    except Exception as e:
        print(f"❌ Error syncing command tree: {e}")

@bot.event
async def on_message(message):
    """Message event handler"""
    if message.author == bot.user:
        return
    
    # Auto-reload message lists every configured interval
    if not hasattr(bot, 'last_msg_reload'):
        bot.last_msg_reload = discord.utils.utcnow()
    
    now = discord.utils.utcnow()
    if (now - bot.last_msg_reload).total_seconds() >= config['MESSAGE_RELOAD_INTERVAL']:
        msg_manager.reload()
        bot.last_msg_reload = now
    
    # Special channel handling
    if config['ENABLE_SPECIAL_CHANNEL'] and message.channel.id == config['SPECIAL_MESSAGE_CHANNEL_ID']:
        try:
            # Use custom emojis if provided, otherwise use standard ones
            yes_emoji = f"<{config['SPECIAL_CHANNEL_YES_EMOJI']}>" if config['SPECIAL_CHANNEL_YES_EMOJI'] else '✅'
            no_emoji = f"<{config['SPECIAL_CHANNEL_NO_EMOJI']}>" if config['SPECIAL_CHANNEL_NO_EMOJI'] else '❌'
            
            await message.add_reaction(yes_emoji)
            await message.add_reaction(no_emoji)
            
            thread_name = message.content[:100] if message.content.strip() else "Discussion"
            thread = await message.create_thread(name=thread_name)
            ping_message = await thread.send(f"{message.author.mention}")
            await ping_message.delete()
            
        except discord.Forbidden:
            print(f"❌ Missing permissions in special message channel. Check bot permissions!")
        except Exception as e:
            print(f"❌ Error processing message in channel {config['SPECIAL_MESSAGE_CHANNEL_ID']}: {e}")
    
    # Send random text message based on configured chance and config toggle
    if config['ENABLE_RANDOM_MESSAGES'] and random.randint(1, config['RANDOM_MESSAGE_CHANCE']) == 1 and msg_manager.default:
        msg = random.choice(msg_manager.default)
        try:
            await message.channel.send(msg)
        except discord.Forbidden:
            print(f"❌ No permission to send messages in #{message.channel.name}")
        except Exception as e:
            print(f"❌ Error sending random message: {e}")
    
    # Send random audio message based on configured chance and config toggle
    if config['ENABLE_RANDOM_AUDIO_MESSAGES'] and random.randint(1, config['RANDOM_AUDIO_MESSAGE_CHANCE']) == 1 and msg_manager.default_audio:
        audio_source = random.choice(msg_manager.default_audio)
        await send_audio_message(message.channel, audio_source)
    
    # Handle mention responses - randomly choose between text or audio
    if bot.user.mentioned_in(message):
        available_responses = []
        
        # Check if text responses are enabled and available
        if config['ENABLE_MENTION_RESPONSES'] and msg_manager.mention:
            available_responses.append(('text', msg_manager.mention))
        
        # Check if audio responses are enabled and available
        if config['ENABLE_MENTION_AUDIO_RESPONSES'] and msg_manager.mention_audio:
            available_responses.append(('audio', msg_manager.mention_audio))
        
        # If we have available responses, randomly pick one type and send it
        if available_responses:
            response_type, message_list = random.choice(available_responses)
            
            try:
                if response_type == 'text':
                    msg = random.choice(message_list)
                    await message.channel.send(msg)
                    print(f"💬 Sent text mention response: {msg[:50]}...")
                else:  # audio
                    audio_source = random.choice(message_list)
                    await send_audio_message(message.channel, audio_source)
                    print(f"🎵 Sent audio mention response: {audio_source}")
            except discord.Forbidden:
                print(f"❌ No permission to send messages in #{message.channel.name}")
            except Exception as e:
                print(f"❌ Error sending mention response: {e}")
    
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    """Member join event handler"""
    try:
        if config['ENABLE_CHICKEN_OUT']:
            recent_joins[member.id] = {
                "time": discord.utils.utcnow(),
                "channel": member.guild.system_channel
            }
        print(f"👋 {member.name} joined the server")
    except Exception as e:
        print(f"❌ Error in on_member_join: {e}")

@bot.event
async def on_member_remove(member):
    """Member remove event handler"""
    try:
        if config['ENABLE_CHICKEN_OUT'] and member.id in recent_joins:
            join_time = recent_joins[member.id]["time"]
            leave_time = discord.utils.utcnow()
            
            if (leave_time - join_time).total_seconds() <= config['CHICKEN_OUT_TIMEOUT']:
                channel = bot.get_channel(config['CHICKEN_OUT_CHANNEL_ID'])
                if channel:
                    try:
                        await channel.send(f"{member.mention} chickened out")
                        await channel.send(config['CHICKENED_OUT_MSG'])
                        print(f"🐔 {member.name} chickened out")
                    except discord.Forbidden:
                        print(f"❌ No permission to send messages in chicken out channel")
                    except Exception as e:
                        print(f"❌ Error sending chicken out message: {e}")
                else:
                    print(f"❌ Chicken out channel not found (ID: {config['CHICKEN_OUT_CHANNEL_ID']})")
            
            del recent_joins[member.id]
    except Exception as e:
        print(f"❌ Error in on_member_remove: {e}")

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Handle slash command errors"""
    error_message = f"❌ Error: {error}"
    print(f"❌ Slash command error: {error}")
    print(f"   Command: {interaction.command.name if interaction.command else 'Unknown'}")
    print(f"   User: {interaction.user}")
    
    try:
        if interaction.response.is_done():
            await interaction.followup.send(error_message, ephemeral=True)
        else:
            await interaction.response.send_message(error_message, ephemeral=True)
    except Exception as e:
        print(f"❌ Error sending error message: {e}")

# ======================
# CONTEXT MENU COMMANDS
# ======================

@bot.tree.context_menu(name="Suggest message")
async def suggest_message_context(interaction: discord.Interaction, message: discord.Message):
    """Context menu command to suggest a message for the bot"""
    if not config['ENABLE_SUGGESTIONS']:
        await interaction.response.send_message("❌ Message suggestions are currently disabled.", ephemeral=True)
        return
    
    # Check if message has content
    if not message.content:
        await interaction.response.send_message("❌ This message has no text content to suggest!", ephemeral=True)
        return
    
    target_channel = bot.get_channel(config['SUGGESTION_CHANNEL_ID'])
    if not target_channel:
        await interaction.response.send_message("❌ Could not find the target channel. Please contact an administrator.", ephemeral=True)
        return
    
    msg_content = message.content
    
    try:
        # Create embed for better presentation
        embed = create_suggestion_embed(interaction, msg_content, message.author, message.jump_url)
        
        # Create view with buttons
        view = MsgSuggestionView(msg_content, message.id)
        
        # Send to target channel
        suggestion_message = await target_channel.send(
            content=f"<@&{config['SUGGESTION_PING_ROLE_ID']}> A new message suggestion has been submitted!",
            embed=embed,
            view=view
        )
        
        # Add confirmation reactions
        await suggestion_message.add_reaction('✅')
        await suggestion_message.add_reaction('❌')
        
        await interaction.response.send_message(
            "✅ Message suggestion submitted successfully! The moderators will review it shortly.",
            ephemeral=True
        )
    except Exception as e:
        print(f"Error sending message suggestion: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while submitting your suggestion. Please try again later.",
            ephemeral=True
        )

@bot.tree.context_menu(name="Rape member")
async def rape_user(interaction: discord.Interaction, member: discord.Member):
    """Context menu command to rape a user"""
    if not config['ENABLE_RAPE_COMMAND']:
        await interaction.response.send_message("❌ Rape command is currently disabled.", ephemeral=True)
        return
    
    # Get the target channel
    target_channel = bot.get_channel(config['RAPE_CHANNEL_ID'])
    if not target_channel:
        await interaction.response.send_message("❌ Could not find the target channel.", ephemeral=True)
        return
    
    # Send the rape message
    try:
        await target_channel.send(f"{interaction.user.mention} raped {member.mention}")
        await interaction.response.send_message(f"✅ Successfully raped {member.display_name}!", ephemeral=True)
    except Exception as e:
        print(f"Error sending rape message: {e}")
        await interaction.response.send_message("❌ An error occurred while sending the rape message.", ephemeral=True)

# ======================
# SLASH COMMANDS
# ======================

@bot.tree.command(name="suggest-msg", description="Suggest a message for the bot to use")
@app_commands.describe(message="The message content to suggest")
async def suggest_msg_slash(interaction: discord.Interaction, message: str):
    """Slash command to suggest a message for the bot to use"""
    if not config['ENABLE_SUGGESTIONS']:
        await interaction.response.send_message("❌ Message suggestions are currently disabled.", ephemeral=True)
        return
    
    msg_content = message
    target_channel = bot.get_channel(config['SUGGESTION_CHANNEL_ID'])
    if not target_channel:
        await interaction.response.send_message("❌ Could not find the target channel. Please contact an administrator.", ephemeral=True)
        return
    
    try:
        # Create embed for better presentation
        embed = create_suggestion_embed(interaction, msg_content)
        
        # Create view with buttons
        view = MsgSuggestionView(msg_content, interaction.id)
        
        # Send to target channel
        suggestion_message = await target_channel.send(
            content=f"<@&{config['SUGGESTION_PING_ROLE_ID']}> A new message suggestion has been submitted!",
            embed=embed,
            view=view
        )
        
        # Add confirmation reactions
        await suggestion_message.add_reaction('✅')
        await suggestion_message.add_reaction('❌')
        
        await interaction.response.send_message(
            "✅ Message suggestion submitted successfully! The moderators will review it shortly.",
            ephemeral=True
        )
    except Exception as e:
        print(f"Error sending message suggestion: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while submitting your suggestion. Please try again later.",
            ephemeral=True
        )

@bot.tree.command(name="reload-msgs", description="Manually reload message lists from files")
@app_commands.default_permissions(administrator=True)
async def reload_msgs(interaction: discord.Interaction):
    """Manually reload message lists from files"""
    msg_manager.reload()
    counts = msg_manager.get_counts()
    
    await interaction.response.send_message(
        f"✅ Message lists manually reloaded!\n"
        f"📊 Default messages: {counts['default']}\n"
        f"📊 Mention messages: {counts['mention']}\n"
        f"🎙️ Default audio: {counts['default_audio']}\n"
        f"🎙️ Mention audio: {counts['mention_audio']}",
        ephemeral=True
    )
    
    print(f"🔄 Manual reload by {interaction.user.name}: "
          f"Default={counts['default']}, Mention={counts['mention']}, "
          f"Default Audio={counts['default_audio']}, Mention Audio={counts['mention_audio']}")

@bot.tree.command(name="msg-count", description="Show current message counts")
async def msg_count(interaction: discord.Interaction):
    """Show current message counts"""
    counts = msg_manager.get_counts()
    
    await interaction.response.send_message(
        f"📊 Current message counts:\n"
        f"🔹 Default messages: {counts['default']}\n"
        f"🔹 Mention messages: {counts['mention']}\n"
        f"🎙️ Default audio messages: {counts['default_audio']}\n"
        f"🎙️ Mention audio messages: {counts['mention_audio']}",
        ephemeral=True
    )

@bot.tree.command(name="list-msgs", description="List messages from specified list")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(list_type="Which list to display: 'default', 'mention', 'default_audio', or 'mention_audio'")
async def list_msgs(interaction: discord.Interaction, list_type: str = "default"):
    """List messages from specified list"""
    list_type = list_type.lower()
    
    list_map = {
        'default': (msg_manager.default, 'Default messages'),
        'mention': (msg_manager.mention, 'Mention messages'),
        'default_audio': (msg_manager.default_audio, 'Default audio messages'),
        'mention_audio': (msg_manager.mention_audio, 'Mention audio messages')
    }
    
    if list_type not in list_map:
        await interaction.response.send_message(
            "❌ Invalid list type. Use 'default', 'mention', 'default_audio', or 'mention_audio'.", 
            ephemeral=True
        )
        return
    
    msgs, title = list_map[list_type]
    
    if not msgs:
        await interaction.response.send_message(f"📭 No messages found in {title} list.", ephemeral=True)
        return
    
    # Create embed with pagination if needed
    chunk_size = 10
    chunks = [msgs[i:i + chunk_size] for i in range(0, len(msgs), chunk_size)]
    
    # Send first chunk with interaction response
    if chunks:
        embed = discord.Embed(
            title=f"{title} (Page 1/{len(chunks)})",
            color=discord.Color(int(config['SUCCESS_COLOR'], 16))
        )
        
        chunk = chunks[0]
        for j, msg in enumerate(chunk, 1):
            embed.add_field(
                name=f"{j}. Message",
                value=msg[:100] + "..." if len(msg) > 100 else msg,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Send remaining pages as follow-ups
        for i, chunk in enumerate(chunks[1:], 1):
            embed = discord.Embed(
                title=f"{title} (Page {i+1}/{len(chunks)})",
                color=discord.Color(int(config['SUCCESS_COLOR'], 16))
            )
            
            for j, msg in enumerate(chunk, 1):
                embed.add_field(
                    name=f"{j + i*chunk_size}. Message",
                    value=msg[:100] + "..." if len(msg) > 100 else msg,
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)

# ======================
# MAIN EXECUTION
# ======================

if __name__ == "__main__":
    print("🚀 Starting Bruh Bot...")
    print(f"✅ Configuration loaded successfully!")
    print(f"📁 Default messages file: {config['DEFAULT_MSGS_FILE']}")
    print(f"📁 Mention messages file: {config['MENTION_MSGS_FILE']}")
    print(f"📁 Default audio messages file: {config['DEFAULT_AUDIO_MSGS_FILE']}")
    print(f"📁 Mention audio messages file: {config['MENTION_AUDIO_MSGS_FILE']}")
    print(f"📊 Random message chance: 1 in {config['RANDOM_MESSAGE_CHANCE']}")
    print(f"📊 Random audio message chance: 1 in {config['RANDOM_AUDIO_MESSAGE_CHANCE']}")
    print(f"⏱️  Reload interval: {config['MESSAGE_RELOAD_INTERVAL']}s")
    print(f"👤 Authorized user ID: {config['AUTHORIZED_USER_ID']}")
    print(f"🔧 Feature flags:")
    print(f"   ├─ Random messages: {'✅' if config['ENABLE_RANDOM_MESSAGES'] else '❌'}")
    print(f"   ├─ Random audio messages: {'✅' if config['ENABLE_RANDOM_AUDIO_MESSAGES'] else '❌'}")
    print(f"   ├─ Mention responses: {'✅' if config['ENABLE_MENTION_RESPONSES'] else '❌'}")
    print(f"   ├─ Mention audio responses: {'✅' if config['ENABLE_MENTION_AUDIO_RESPONSES'] else '❌'}")
    print(f"   ├─ Special channel: {'✅' if config['ENABLE_SPECIAL_CHANNEL'] else '❌'}")
    print(f"   ├─ Chicken out: {'✅' if config['ENABLE_CHICKEN_OUT'] else '❌'}")
    print(f"   ├─ Suggestions: {'✅' if config['ENABLE_SUGGESTIONS'] else '❌'}")
    print(f"   └─ Rape command: {'✅' if config['ENABLE_RAPE_COMMAND'] else '❌'}")
    
    # Start the bot
    try:
        bot.run(config['TOKEN'])
    except discord.LoginFailure:
        print(f"❌ Login failed! Your TOKEN in config.txt is invalid.")
        print(f"   Make sure you've set a valid bot token.")
        print(f"   Get your token from: https://discord.com/developers/applications")
    except discord.HTTPException as e:
        print(f"❌ Network error while connecting: {e}")
    except KeyboardInterrupt:
        print(f"\n👋 Bruh Bot stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
