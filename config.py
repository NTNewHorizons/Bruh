"""
Configuration module for loading and validating bot settings from config.txt
"""
import os


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
AUTHORIZED_USER_ID=1209428799289032704

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


def load_config():
    """Load configuration from config.txt and validate all required fields"""
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
                                     'MESSAGE_RELOAD_INTERVAL', 'CHICKEN_OUT_TIMEOUT']
                    
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


# Load config on module import
config = load_config()

# Print loaded configuration
print(f"✅ Configuration loaded successfully!")
print(f"📁 Default messages file: {config['DEFAULT_MSGS_FILE']}")
print(f"📁 Mention messages file: {config['MENTION_MSGS_FILE']}")
print(f"📊 Random message chance: 1 in {config['RANDOM_MESSAGE_CHANCE']}")
print(f"⏱️  Reload interval: {config['MESSAGE_RELOAD_INTERVAL']}s")
print(f"👤 Authorized user ID: {config['AUTHORIZED_USER_ID']}")
print(f"🔧 Feature flags:")
print(f"   ├─ Random messages: {'✅' if config['ENABLE_RANDOM_MESSAGES'] else '❌'}")
print(f"   ├─ Mention responses: {'✅' if config['ENABLE_MENTION_RESPONSES'] else '❌'}")
print(f"   ├─ Special channel: {'✅' if config['ENABLE_SPECIAL_CHANNEL'] else '❌'}")
print(f"   ├─ Chicken out: {'✅' if config['ENABLE_CHICKEN_OUT'] else '❌'}")
print(f"   ├─ Suggestions: {'✅' if config['ENABLE_SUGGESTIONS'] else '❌'}")
print(f"   └─ Rape command: {'✅' if config['ENABLE_RAPE_COMMAND'] else '❌'}")
