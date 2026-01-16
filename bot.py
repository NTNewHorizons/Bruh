import discord
import random
import asyncio
import os
from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands

# Function to load configuration from config.txt
def load_config():
    config = {}
    config_file = 'config.txt'
    
    if not os.path.exists(config_file):
        print(f"❌ Config file '{config_file}' not found! Creating template...")
        create_config_template(config_file)
        print(f"✅ Template config file created. Please fill in your values and restart the bot.")
        exit(1)
    
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
                    
                    # Convert numeric fields to integers
                    numeric_fields = ['AUTHORIZED_USER_ID', 'SUGGESTION_CHANNEL_ID', 'RAPE_CHANNEL_ID',
                                     'SPECIAL_MESSAGE_CHANNEL_ID', 'CHICKEN_OUT_CHANNEL_ID',
                                     'SUGGESTION_PING_ROLE_ID', 'RANDOM_MESSAGE_CHANCE',
                                     'MESSAGE_RELOAD_INTERVAL', 'CHICKEN_OUT_TIMEOUT',
                                     'SPECIAL_CHANNEL_YES_EMOJI', 'SPECIAL_CHANNEL_NO_EMOJI']
                    
                    # Convert boolean fields
                    boolean_fields = ['ENABLE_RANDOM_MESSAGES', 'ENABLE_MENTION_RESPONSES',
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
                      'SUGGESTION_CHANNEL_ID', 'RAPE_CHANNEL_ID', 'SPECIAL_MESSAGE_CHANNEL_ID',
                      'CHICKEN_OUT_CHANNEL_ID', 'SUGGESTION_PING_ROLE_ID', 'RANDOM_MESSAGE_CHANCE',
                      'MESSAGE_RELOAD_INTERVAL', 'CHICKEN_OUT_TIMEOUT', 'CHICKENED_OUT_MSG',
                      'AUTHORIZED_USER_ID']
    
    missing_fields = [field for field in required_fields if field not in config]
    
    if missing_fields:
        print(f"❌ Missing required configuration fields:")
        for field in missing_fields:
            print(f"   - {field}")
        print(f"\nPlease check your {config_file} file and ensure all required fields are set.")
        exit(1)
    
    # Validate token is not placeholder
    if config['TOKEN'] == 'YOUR_BOT_TOKEN_HERE' or not config['TOKEN']:
        print(f"❌ Invalid TOKEN in {config_file}")
        print(f"Please set TOKEN to your actual Discord bot token.")
        print(f"Get your token from: https://discord.com/developers/applications")
        exit(1)
    
    # Validate numeric values are reasonable
    if config['RANDOM_MESSAGE_CHANCE'] < 1:
        print(f"❌ RANDOM_MESSAGE_CHANCE must be at least 1, got {config['RANDOM_MESSAGE_CHANCE']}")
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
        'ENABLE_MENTION_RESPONSES': True,
        'ENABLE_SPECIAL_CHANNEL': True,
        'ENABLE_CHICKEN_OUT': True,
        'ENABLE_SUGGESTIONS': True,
        'ENABLE_RAPE_COMMAND': True,
        'REJECT_BUTTON_EMOJI': '🗑️',
        'REJECT_BUTTON_LABEL': '❌ Reject',
        'DEFAULT_BUTTON_EMOJI': '📌',
        'DEFAULT_BUTTON_LABEL': '✅ Default',
        'MENTION_BUTTON_EMOJI': '👋',
        'MENTION_BUTTON_LABEL': '✅ Mention',
        'BOTH_BUTTON_EMOJI': '✨',
        'BOTH_BUTTON_LABEL': '✅ Both',
        'SPECIAL_CHANNEL_YES_EMOJI': '1416494635660087467',
        'SPECIAL_CHANNEL_NO_EMOJI': '1416494651195654277',
        'SUGGESTION_EMBED_COLOR': '0x0099ff',
        'SUCCESS_COLOR': '00aa00',
        'ERROR_COLOR': 'ff0000',
        'WARNING_COLOR': 'ffaa00',
    }
    
    for key, default_value in optional_defaults.items():
        if key not in config:
            config[key] = default_value
    
    return config

def create_config_template(filename):
    """Create a template config file with example values"""
    template = """# Discord Bot Configuration File
# Fill in the values below with your actual configuration

# ===== CORE SETTINGS =====
# Discord Bot Token (REQUIRED)
TOKEN=YOUR_BOT_TOKEN_HERE

# Bot command prefix
COMMAND_PREFIX=!

# ===== MESSAGE FILES =====
# File path for default messages
DEFAULT_MSGS_FILE=default_msgs.txt

# File path for mention messages
MENTION_MSGS_FILE=mention_msgs.txt

# ===== CHANNEL IDS =====
# Channel for message suggestions
SUGGESTION_CHANNEL_ID=1365676297589624903

# Channel for the "rape" command
RAPE_CHANNEL_ID=1420163750551617677

# Channel for special message handling (auto-thread creation)
SPECIAL_MESSAGE_CHANNEL_ID=1416584800457723965

# Channel for "chicken out" notifications
CHICKEN_OUT_CHANNEL_ID=1365834457864732732

# ===== ROLE IDS =====
# Role to mention when a message is suggested
SUGGESTION_PING_ROLE_ID=1365677261801521265

# ===== BOT BEHAVIORS =====
# Chance (1 in X) to send a random default message (e.g., 100 = 1% chance)
RANDOM_MESSAGE_CHANCE=100

# Time between auto-reloading messages from files (in seconds)
MESSAGE_RELOAD_INTERVAL=300

# Time window for "chicken out" detection after joining (in seconds)
CHICKEN_OUT_TIMEOUT=900

# Message to send when someone chickens out
CHICKENED_OUT_MSG=https://tenor.com/view/walk-away-gif-8390063

# ===== PERMISSIONS =====
# Authorized user ID for approving/declining suggestions (numeric ID)
AUTHORIZED_USER_ID=1209428799289032704

# ===== FEATURE TOGGLES =====
# Enable/disable random message responses
ENABLE_RANDOM_MESSAGES=true

# Enable/disable mention responses
ENABLE_MENTION_RESPONSES=true

# Enable/disable special channel auto-threading
ENABLE_SPECIAL_CHANNEL=true

# Enable/disable chicken out detection
ENABLE_CHICKEN_OUT=true

# Enable/disable message suggestion system
ENABLE_SUGGESTIONS=true

# Enable/disable rape command
ENABLE_RAPE_COMMAND=true

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

# ===== SPECIAL CHANNEL REACTION EMOJIS =====
# Custom emoji IDs for special channel reactions (leave empty for standard reactions)
SPECIAL_CHANNEL_YES_EMOJI=1416494635660087467
SPECIAL_CHANNEL_NO_EMOJI=1416494651195654277

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

# Load configuration
config = load_config()

# Core settings
TOKEN = config['TOKEN']

# Message files
DEFAULT_MSGS_FILE = config['DEFAULT_MSGS_FILE']
MENTION_MSGS_FILE = config['MENTION_MSGS_FILE']

# Channel IDs
SUGGESTION_CHANNEL_ID = config['SUGGESTION_CHANNEL_ID']
RAPE_CHANNEL_ID = config['RAPE_CHANNEL_ID']
SPECIAL_MESSAGE_CHANNEL_ID = config['SPECIAL_MESSAGE_CHANNEL_ID']
CHICKEN_OUT_CHANNEL_ID = config['CHICKEN_OUT_CHANNEL_ID']

# Role IDs
SUGGESTION_PING_ROLE_ID = config['SUGGESTION_PING_ROLE_ID']

# Bot behaviors
RANDOM_MESSAGE_CHANCE = config['RANDOM_MESSAGE_CHANCE']
MESSAGE_RELOAD_INTERVAL = config['MESSAGE_RELOAD_INTERVAL']
CHICKEN_OUT_TIMEOUT = config['CHICKEN_OUT_TIMEOUT']
CHICKENED_OUT_MSG = config['CHICKENED_OUT_MSG']

# Permissions
AUTHORIZED_USER_ID = config['AUTHORIZED_USER_ID']

# Feature toggles
ENABLE_RANDOM_MESSAGES = config['ENABLE_RANDOM_MESSAGES']
ENABLE_MENTION_RESPONSES = config['ENABLE_MENTION_RESPONSES']
ENABLE_SPECIAL_CHANNEL = config['ENABLE_SPECIAL_CHANNEL']
ENABLE_CHICKEN_OUT = config['ENABLE_CHICKEN_OUT']
ENABLE_SUGGESTIONS = config['ENABLE_SUGGESTIONS']
ENABLE_RAPE_COMMAND = config['ENABLE_RAPE_COMMAND']

# Button emojis and labels
REJECT_BUTTON_EMOJI = config['REJECT_BUTTON_EMOJI']
REJECT_BUTTON_LABEL = config['REJECT_BUTTON_LABEL']
DEFAULT_BUTTON_EMOJI = config['DEFAULT_BUTTON_EMOJI']
DEFAULT_BUTTON_LABEL = config['DEFAULT_BUTTON_LABEL']
MENTION_BUTTON_EMOJI = config['MENTION_BUTTON_EMOJI']
MENTION_BUTTON_LABEL = config['MENTION_BUTTON_LABEL']
BOTH_BUTTON_EMOJI = config['BOTH_BUTTON_EMOJI']
BOTH_BUTTON_LABEL = config['BOTH_BUTTON_LABEL']

# Special channel emojis
SPECIAL_CHANNEL_YES_EMOJI = config['SPECIAL_CHANNEL_YES_EMOJI']
SPECIAL_CHANNEL_NO_EMOJI = config['SPECIAL_CHANNEL_NO_EMOJI']

# Colors
SUGGESTION_EMBED_COLOR = config['SUGGESTION_EMBED_COLOR']
SUCCESS_COLOR = config['SUCCESS_COLOR']
ERROR_COLOR = config['ERROR_COLOR']
WARNING_COLOR = config['WARNING_COLOR']

print(f"✅ Configuration loaded successfully!")
print(f"📁 Default messages file: {DEFAULT_MSGS_FILE}")
print(f"📁 Mention messages file: {MENTION_MSGS_FILE}")
print(f"📊 Random message chance: 1 in {RANDOM_MESSAGE_CHANCE}")
print(f"⏱️  Reload interval: {MESSAGE_RELOAD_INTERVAL}s")
print(f"👤 Authorized user ID: {AUTHORIZED_USER_ID}")
print(f"🔧 Feature flags:")
print(f"   ├─ Random messages: {'✅' if ENABLE_RANDOM_MESSAGES else '❌'}")
print(f"   ├─ Mention responses: {'✅' if ENABLE_MENTION_RESPONSES else '❌'}")
print(f"   ├─ Special channel: {'✅' if ENABLE_SPECIAL_CHANNEL else '❌'}")
print(f"   ├─ Chicken out: {'✅' if ENABLE_CHICKEN_OUT else '❌'}")
print(f"   ├─ Suggestions: {'✅' if ENABLE_SUGGESTIONS else '❌'}")
print(f"   └─ Rape command: {'✅' if ENABLE_RAPE_COMMAND else '❌'}")

# Function to load messages from file with automatic creation if missing
def load_msgs_from_file(filename):
    try:
        if not os.path.exists(filename):
            print(f"ℹ️  Creating new file: {filename}")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('')
        
        with open(filename, 'r', encoding='utf-8') as f:
            msgs = [line.strip() for line in f if line.strip()]
            print(f"✅ Loaded {len(msgs)} messages from {filename}")
            return msgs
    except IOError as e:
        print(f"❌ Error reading {filename}: {e}")
        return []

# Function to save messages to file
def save_msgs_to_file(filename, msgs):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for msg in msgs:
                f.write(f"{msg}\n")
        print(f"✅ Saved {len(msgs)} messages to {filename}")
    except IOError as e:
        print(f"❌ Error writing to {filename}: {e}")

# Initialize message lists
default_msgs = load_msgs_from_file(DEFAULT_MSGS_FILE)
mention_msgs = load_msgs_from_file(MENTION_MSGS_FILE)

# Recent joins tracking for chicken out detection
recent_joins = {}

# Discord intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(intents=intents)

class MsgSuggestionView(View):
    def __init__(self, author_id, msg_content, message_id):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.msg_content = msg_content
        self.message_id = message_id
        
    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red, emoji="🗑️")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user is authorized
        if interaction.user.id != AUTHORIZED_USER_ID:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return
            
        # Edit the original message to show rejection
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n❌ **Rejected by {interaction.user.mention}**",
            embed=None,
            view=None
        )
        await interaction.response.defer()
    
    @discord.ui.button(label="✅ Default", style=discord.ButtonStyle.green, emoji="📌")
    async def accept_default_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user is authorized
        if interaction.user.id != AUTHORIZED_USER_ID:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return
            
        global default_msgs
        
        # Reload messages to ensure we have the latest version
        default_msgs = load_msgs_from_file(DEFAULT_MSGS_FILE)
        
        if self.msg_content in default_msgs:
            await interaction.response.send_message("⚠️ This message is already in the default list!", ephemeral=True)
            return
            
        # Add to default list
        default_msgs.append(self.msg_content)
        save_msgs_to_file(DEFAULT_MSGS_FILE, default_msgs)
        
        # Auto-reload the message lists
        await self.reload_msg_lists()
        
        await interaction.response.send_message(f"✅ Message added to default list!", ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Default by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Mention", style=discord.ButtonStyle.green, emoji="👋")
    async def accept_mention_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user is authorized
        if interaction.user.id != AUTHORIZED_USER_ID:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return
            
        global mention_msgs
        
        # Reload messages to ensure we have the latest version
        mention_msgs = load_msgs_from_file(MENTION_MSGS_FILE)
        
        if self.msg_content in mention_msgs:
            await interaction.response.send_message("⚠️ This message is already in the mention list!", ephemeral=True)
            return
            
        # Add to mention list
        mention_msgs.append(self.msg_content)
        save_msgs_to_file(MENTION_MSGS_FILE, mention_msgs)
        
        # Auto-reload the message lists
        await self.reload_msg_lists()
        
        await interaction.response.send_message(f"✅ Message added to mention list!", ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Mention by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Both", style=discord.ButtonStyle.blurple, emoji="✨")
    async def accept_both_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user is authorized
        if interaction.user.id != AUTHORIZED_USER_ID:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return
            
        global default_msgs, mention_msgs
        
        # Reload messages to ensure we have the latest versions
        default_msgs = load_msgs_from_file(DEFAULT_MSGS_FILE)
        mention_msgs = load_msgs_from_file(MENTION_MSGS_FILE)
        
        added_to_default = False
        added_to_mention = False
        
        if self.msg_content not in default_msgs:
            default_msgs.append(self.msg_content)
            added_to_default = True
            
        if self.msg_content not in mention_msgs:
            mention_msgs.append(self.msg_content)
            added_to_mention = True
            
        # Save both files
        save_msgs_to_file(DEFAULT_MSGS_FILE, default_msgs)
        save_msgs_to_file(MENTION_MSGS_FILE, mention_msgs)
        
        # Auto-reload the message lists
        await self.reload_msg_lists()
        
        status_message = ""
        if not added_to_default and not added_to_mention:
            status_message = "⚠️ This message was already in both lists!"
        elif added_to_default and added_to_mention:
            status_message = "✅ Message added to both lists!"
        elif added_to_default:
            status_message = "✅ Message added to default list! (Already in mention list)"
        elif added_to_mention:
            status_message = "✅ Message added to mention list! (Already in default list)"
            
        await interaction.response.send_message(status_message, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Both by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    async def reload_msg_lists(self):
        """Automatically reload message lists after modifications"""
        global default_msgs, mention_msgs
        default_msgs = load_msgs_from_file(DEFAULT_MSGS_FILE)
        mention_msgs = load_msgs_from_file(MENTION_MSGS_FILE)
        print(f"🔄 Auto-reloaded message lists: Default={len(default_msgs)}, Mention={len(mention_msgs)}")

# Context menu command to suggest a message
@bot.tree.context_menu(name="Suggest message")
async def suggest_message_context(interaction: discord.Interaction, message: discord.Message):
    """Context menu command to suggest a message for the bot"""
    
    if not ENABLE_SUGGESTIONS:
        await interaction.response.send_message(
            "❌ Message suggestions are currently disabled.",
            ephemeral=True
        )
        return
    
    # Check if message has content
    if not message.content:
        await interaction.response.send_message(
            "❌ This message has no text content to suggest!",
            ephemeral=True
        )
        return
    
    target_channel = bot.get_channel(SUGGESTION_CHANNEL_ID)
    if not target_channel:
        await interaction.response.send_message(
            "❌ Could not find the target channel. Please contact an administrator.",
            ephemeral=True
        )
        return
    
    msg_content = message.content
    
    try:
        # Create embed for better presentation
        embed = discord.Embed(
            title="New Proposed Message Suggestion",
            description=f"User {interaction.user.mention} suggests this message for the bot:",
            color=discord.Color(int(SUGGESTION_EMBED_COLOR, 16)),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="📝 Message Content", value=msg_content, inline=False)
        embed.add_field(name="📤 Original Author", value=f"{message.author.mention}", inline=True)
        embed.add_field(name="🔗 Message Link", value=f"[Jump to Message]({message.jump_url})", inline=True)
        embed.set_footer(text=f"Suggested by {interaction.user.name} | User ID: {interaction.user.id}")
        
        # Create view with buttons
        view = MsgSuggestionView(interaction.user.id, msg_content, message.id)
        
        # Send to target channel
        suggestion_message = await target_channel.send(
            content=f"<@&{SUGGESTION_PING_ROLE_ID}> A new message suggestion has been submitted!",
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

# Context menu command for raping
@bot.tree.context_menu(name="Rape member")
async def rape_user(interaction: discord.Interaction, member: discord.Member):
    """Context menu command to rape a user"""
    
    if not ENABLE_RAPE_COMMAND:
        await interaction.response.send_message("❌ Rape command is currently disabled.", ephemeral=True)
        return
    
    # Get the target channel
    target_channel = bot.get_channel(RAPE_CHANNEL_ID)
    
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

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online and ready!')
    print(f'📊 Initial message counts: Default={len(default_msgs)}, Mention={len(mention_msgs)}')
    
    if len(default_msgs) == 0:
        print(f"⚠️  Warning: No default messages loaded. The bot won't respond to random triggers.")
    if len(mention_msgs) == 0:
        print(f"⚠️  Warning: No mention messages loaded. The bot won't respond to mentions.")
    
    # Verify all configured channels exist
    channels_to_check = [
        (SUGGESTION_CHANNEL_ID, "Suggestion channel"),
        (RAPE_CHANNEL_ID, "Rape command channel"),
        (SPECIAL_MESSAGE_CHANNEL_ID, "Special message channel"),
        (CHICKEN_OUT_CHANNEL_ID, "Chicken out channel")
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
        suggestion_role = guild.get_role(SUGGESTION_PING_ROLE_ID)
        if suggestion_role:
            print(f"✅ Suggestion ping role found: @{suggestion_role.name}")
            break
    
    if not suggestion_role:
        print(f"❌ Suggestion ping role NOT FOUND (ID: {SUGGESTION_PING_ROLE_ID}). Please check your config!")
    
    # Ensure files exist with current data
    try:
        save_msgs_to_file(DEFAULT_MSGS_FILE, default_msgs)
        save_msgs_to_file(MENTION_MSGS_FILE, mention_msgs)
    except Exception as e:
        print(f"❌ Error saving message files: {e}")
    
    # Sync command tree
    try:
        await bot.tree.sync()
        print('🔄 Command tree synced successfully')
    except Exception as e:
        print(f"❌ Error syncing command tree: {e}")

# Slash command for manual message suggestion
@bot.tree.command(name="suggest-msg", description="Suggest a message for the bot to use")
@app_commands.describe(message="The message content to suggest")
async def suggest_msg_slash(interaction: discord.Interaction, message: str):
    """Slash command to suggest a message for the bot to use"""
    
    if not ENABLE_SUGGESTIONS:
        await interaction.response.send_message(
            "❌ Message suggestions are currently disabled.",
            ephemeral=True
        )
        return
    
    msg_content = message
    
    target_channel = bot.get_channel(SUGGESTION_CHANNEL_ID)
    if not target_channel:
        await interaction.response.send_message(
            "❌ Could not find the target channel. Please contact an administrator.",
            ephemeral=True
        )
        return
    
    try:
        # Create embed for better presentation
        embed = discord.Embed(
            title="New Proposed Message Suggestion",
            description=f"User {interaction.user.mention} suggests this message for the bot:",
            color=discord.Color(int(SUGGESTION_EMBED_COLOR, 16)),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="📝 Message Content", value=msg_content, inline=False)
        embed.set_footer(text=f"Suggested by {interaction.user.name} | User ID: {interaction.user.id}")
        
        # Create view with buttons
        view = MsgSuggestionView(interaction.user.id, msg_content, interaction.id)
        
        # Send to target channel
        suggestion_message = await target_channel.send(
            content=f"<@&{SUGGESTION_PING_ROLE_ID}> A new message suggestion has been submitted!",
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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Auto-reload message lists every configured interval
    if not hasattr(bot, 'last_msg_reload'):
        bot.last_msg_reload = discord.utils.utcnow()
    
    now = discord.utils.utcnow()
    if (now - bot.last_msg_reload).total_seconds() >= MESSAGE_RELOAD_INTERVAL:
        global default_msgs, mention_msgs
        default_msgs = load_msgs_from_file(DEFAULT_MSGS_FILE)
        mention_msgs = load_msgs_from_file(MENTION_MSGS_FILE)
        bot.last_msg_reload = now
        print(f"🔄 Periodic reload: Default={len(default_msgs)}, Mention={len(mention_msgs)}")

    # Special channel handling
    if ENABLE_SPECIAL_CHANNEL and message.channel.id == SPECIAL_MESSAGE_CHANNEL_ID:
        try:
            # Use custom emojis if provided, otherwise use standard ones
            yes_emoji = f"<:yes:{SPECIAL_CHANNEL_YES_EMOJI}>" if SPECIAL_CHANNEL_YES_EMOJI else '✅'
            no_emoji = f"<:no:{SPECIAL_CHANNEL_NO_EMOJI}>" if SPECIAL_CHANNEL_NO_EMOJI else '❌'
            
            await message.add_reaction(yes_emoji)
            await message.add_reaction(no_emoji)
            
            thread_name = message.content[:100] if message.content.strip() else "Discussion"
            thread = await message.create_thread(name=thread_name)
            
            ping_message = await thread.send(f"{message.author.mention}")
            await ping_message.delete()
            
        except discord.Forbidden:
            print(f"❌ Missing permissions in special message channel. Check bot permissions!")
        except Exception as e:
            print(f"❌ Error processing message in channel {SPECIAL_MESSAGE_CHANNEL_ID}: {e}")

    # Send random message based on configured chance
    if ENABLE_RANDOM_MESSAGES and random.randint(1, RANDOM_MESSAGE_CHANCE) == 1 and default_msgs:
        msg = random.choice(default_msgs)
        try:
            await message.channel.send(msg)
        except discord.Forbidden:
            print(f"❌ No permission to send messages in #{message.channel.name}")
        except Exception as e:
            print(f"❌ Error sending random message: {e}")

    # If bot is mentioned, send message from mention list
    if ENABLE_MENTION_RESPONSES and bot.user.mentioned_in(message) and mention_msgs:
        msg = random.choice(mention_msgs)
        try:
            await message.channel.send(msg)
        except discord.Forbidden:
            print(f"❌ No permission to send messages in #{message.channel.name}")
        except Exception as e:
            print(f"❌ Error sending mention message: {e}")

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    try:
        if ENABLE_CHICKEN_OUT:
            recent_joins[member.id] = {
                "time": discord.utils.utcnow(),
                "channel": member.guild.system_channel
            }
        print(f"👋 {member.name} joined the server")
    except Exception as e:
        print(f"❌ Error in on_member_join: {e}")

@bot.event
async def on_member_remove(member):
    try:
        if ENABLE_CHICKEN_OUT and member.id in recent_joins:
            join_time = recent_joins[member.id]["time"]
            leave_time = discord.utils.utcnow()
            if (leave_time - join_time).total_seconds() <= CHICKEN_OUT_TIMEOUT:
                channel = bot.get_channel(CHICKEN_OUT_CHANNEL_ID)
                if channel:
                    try:
                        await channel.send(f"{member.mention} chickened out")
                        await channel.send(CHICKENED_OUT_MSG)
                        print(f"🐔 {member.name} chickened out")
                    except discord.Forbidden:
                        print(f"❌ No permission to send messages in chicken out channel")
                    except Exception as e:
                        print(f"❌ Error sending chicken out message: {e}")
                else:
                    print(f"❌ Chicken out channel not found (ID: {CHICKEN_OUT_CHANNEL_ID})")

            del recent_joins[member.id]
    except Exception as e:
        print(f"❌ Error in on_member_remove: {e}")

# Slash command to manually reload messages
@bot.tree.command(name="reload-msgs", description="Manually reload message lists from files")
@app_commands.default_permissions(administrator=True)
async def reload_msgs(interaction: discord.Interaction):
    """Manually reload message lists from files"""
    global default_msgs, mention_msgs
    default_msgs = load_msgs_from_file(DEFAULT_MSGS_FILE)
    mention_msgs = load_msgs_from_file(MENTION_MSGS_FILE)
    await interaction.response.send_message(f"✅ Message lists manually reloaded!\n📊 Default messages: {len(default_msgs)}\n📊 Mention messages: {len(mention_msgs)}", ephemeral=True)
    print(f"🔄 Manual reload by {interaction.user.name}: Default={len(default_msgs)}, Mention={len(mention_msgs)}")

# Slash command to show current message counts
@bot.tree.command(name="msg-count", description="Show current message counts")
async def msg_count(interaction: discord.Interaction):
    """Show current message counts"""
    await interaction.response.send_message(f"📊 Current message counts:\n🔹 Default messages: {len(default_msgs)}\n🔹 Mention messages: {len(mention_msgs)}", ephemeral=True)

# Slash command to list all messages
@bot.tree.command(name="list-msgs", description="List messages from specified list")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(list_type="Which list to display: 'default' or 'mention'")
async def list_msgs(interaction: discord.Interaction, list_type: str = "default"):
    """List messages from specified list (default/mention)"""
    if list_type.lower() == "default":
        msgs = default_msgs
        title = "Default messages"
    elif list_type.lower() == "mention":
        msgs = mention_msgs
        title = "Mention messages"
    else:
        await interaction.response.send_message("❌ Invalid list type. Use 'default' or 'mention'.", ephemeral=True)
        return
    
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
            color=discord.Color(int(SUCCESS_COLOR, 16))
        )
        
        chunk = chunks[0]
        for j, msg in enumerate(chunk, 1):
            embed.add_field(
                name=f"{j}. Message",
                value=msg,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Send remaining pages as follow-ups
        for i, chunk in enumerate(chunks[1:], 1):
            embed = discord.Embed(
                title=f"{title} (Page {i+1}/{len(chunks)})",
                color=discord.Color(int(SUCCESS_COLOR, 16))
            )
            
            for j, msg in enumerate(chunk, 1):
                embed.add_field(
                    name=f"{j + i*chunk_size}. Message",
                    value=msg,
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)

# Error handler for slash commands
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

# Initialize files with default content if empty
def initialize_msg_files():
    """Initialize message files with default content if they're empty"""
    default_count = len(default_msgs)
    mention_count = len(mention_msgs)
    
    if default_count == 0:
        print("⚠️  Default messages file is empty, initializing with default messages...")
        default_template = [
            "https://tenor.com/view/jetstream-sam-my-beloved-gif-22029076  ",
            "https://tenor.com/view/team-fortress-есчипсы-gif-23573659",
            "https://tenor.com/view/komaru-cat-tiny-bunny-horror-japanese-gif-11150797129126961638  ",
            "https://media.discordapp.net/attachments/1015901608242065419/1021653518945366046/screw.gif?ex=68c651fc&is=68c5007c&hm=b4b1e407f4c2ed3f4fa712c9bf15c731ba566b263ec76d468e78438881c7df85&  ",
            "https://tenor.com/view/dance-dancing-gif-26353220  ",
            "https://tenor.com/view/frog-frog-laughing-gif-25708743  ",
            "https://tenor.com/view/dfg-gif-26011452  ",
            "https://media.discordapp.net/attachments/990895647949459456/1042076478348722186/doc_2022-11-07_22-02-32_1.gif?ex=68c6ca59&is=68c578d9&hm=527f0889fa6249bc5909ab96c781e534f1de57a58b0eb04679e09a8afd118e44&  ",
            "damn",
            ":wowzer:",
            "cool!",
            "nice one",
            "lmao"
        ]
        try:
            save_msgs_to_file(DEFAULT_MSGS_FILE, default_template)
            print(f"✅ Initialized default messages file with {len(default_template)} messages")
        except Exception as e:
            print(f"❌ Error initializing default messages: {e}")
    
    if mention_count == 0:
        print("⚠️  Mention messages file is empty, initializing with default messages...")
        mention_template = [
            "https://tenor.com/view/komaru-cat-tiny-bunny-horror-japanese-gif-11150797129126961638  ",
            "https://media.discordapp.net/attachments/990895647949459456/1042076478348722186/doc_2022-11-07_22-02-32_1.gif?ex=68c6ca59&is=68c578d9&hm=527f0889fa6249bc5909ab96c781e534f1de57a58b0eb04679e09a8afd118e44&  ",
            "https://tenor.com/view/rock-one-eyebrow-raised-rock-staring-the-rock-gif-22113367  ",
            "https://tenor.com/view/кот-смешной-кот-кот-ест-корм-кота-снимает-камера-cat-gif-10642232306186810479",
            "https://tenor.com/view/cat-silly-boom-explosion-flabbergaster-gif-17414861278238654650  ",
            "what's up?",
            "hey there!",
            "hi"
        ]
        try:
            save_msgs_to_file(MENTION_MSGS_FILE, mention_template)
            print(f"✅ Initialized mention messages file with {len(mention_template)} messages")
        except Exception as e:
            print(f"❌ Error initializing mention messages: {e}")

# Run initialization
try:
    initialize_msg_files()
except Exception as e:
    print(f"❌ Error during initialization: {e}")

# Start the bot
print("🚀 Starting bot...")
try:
    bot.run(TOKEN)
except discord.LoginFailure:
    print(f"❌ Login failed! Your TOKEN in config.txt is invalid.")
    print(f"   Make sure you've set a valid bot token.")
    print(f"   Get your token from: https://discord.com/developers/applications")
except discord.HTTPException as e:
    print(f"❌ Network error while connecting: {e}")
except KeyboardInterrupt:
    print(f"\n👋 Bot stopped by user")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()