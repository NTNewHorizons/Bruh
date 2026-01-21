# Bruh Bot

[![Discord bot](https://img.shields.io/badge/Discord-Bot-5865F2?logo=discord&logoColor=white)](https://discord.com/developers/applications)

A fun, feature-rich Discord bot designed to spice up your server with random responses, message suggestions, and community interactions. Bruh Bot combines humor with utility to create an engaging server experience!

## 🌟 Features

### Random Responses
- **Text Messages**: Sends random text messages/GIFs based on configurable chance
- **Audio Messages**: Plays random audio clips from URLs or local files
- **Mention Responses**: Special replies when the bot is mentioned
- **Audio Mention Responses**: Plays audio clips when mentioned

### Community Features
- **Message Suggestions**: Users can suggest new messages for the bot via context menu or slash command
- **Approval System**: Admins can approve/reject suggestions with one-click buttons
- **Four Categories**: Text messages, mention messages, audio messages, and mention audio messages
- **Auto-reloading**: Message lists reload automatically without restarting the bot

### Server Management
- **"Chicken Out" Detection**: Detects and notifies when members leave shortly after joining
- **Special Channel Handling**: Automatically creates discussion threads and adds reaction emojis
- **Member Tracking**: Logs join/leave events with detailed timestamps

### Admin Tools
- **Message Management**: View counts and list all messages in each category
- **Manual Reloading**: Force reload message files without restarting
- **Configurable Chances**: Fine-tune the probability of random responses
- **Permission Controls**: Restrict sensitive commands to authorized users

### Audio Support
- **URL Support**: Direct links to audio files (MP3, WAV, OGG)
- **Local Files**: Support for audio files stored on your server
- **File Size Checking**: Prevents Discord upload errors with 25MB limit check
- **Path Resolution**: Proper handling of relative and absolute file paths

## 🛠️ Prerequisites

- Python 3.8 or higher
- A Discord bot token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Basic command line knowledge
- A VPS or dedicated server (recommended for 24/7 uptime)

## 🚀 Installation & Deployment

### 1. Clone the Repository
```bash
git clone https://github.com/NTNewHorizons/Bruh.git
cd Bruh
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure the Bot
Run the bot once to generate the config template:
```bash
python bot.py
```

This will create a `config.txt` file with all configuration options. Fill in the required values:

```ini
# Core Settings
TOKEN=your_actual_bot_token_here
COMMAND_PREFIX=!

# Message Files
DEFAULT_MSGS_FILE=default_msgs.txt
MENTION_MSGS_FILE=mention_msgs.txt
DEFAULT_AUDIO_MSGS_FILE=default_audio_msgs.txt
MENTION_AUDIO_MSGS_FILE=mention_audio_msgs.txt

# Channel IDs (get these from Discord by enabling Developer Mode)
SUGGESTION_CHANNEL_ID=123456789012345678
RAPE_CHANNEL_ID=123456789012345678
SPECIAL_MESSAGE_CHANNEL_ID=123456789012345678
CHICKEN_OUT_CHANNEL_ID=123456789012345678

# Role IDs
SUGGESTION_PING_ROLE_ID=123456789012345678

# Bot Behaviors
RANDOM_MESSAGE_CHANCE=100  # 1% chance (1 in 100)
RANDOM_AUDIO_MESSAGE_CHANCE=200  # 0.5% chance
MESSAGE_RELOAD_INTERVAL=300  # 5 minutes
CHICKEN_OUT_TIMEOUT=900  # 15 minutes
CHICKENED_OUT_MSG=https://tenor.com/view/walk-away-gif-8390063

# Permissions
AUTHORIZED_USER_ID=123456789012345678  # Your Discord user ID

# Feature Toggles
ENABLE_RANDOM_MESSAGES=true
ENABLE_RANDOM_AUDIO_MESSAGES=false
ENABLE_MENTION_RESPONSES=true
ENABLE_MENTION_AUDIO_RESPONSES=false
ENABLE_SPECIAL_CHANNEL=false
ENABLE_CHICKEN_OUT=true
ENABLE_SUGGESTIONS=true
ENABLE_RAPE_COMMAND=false
```

### 4. Prepare Message Files
Add your messages to the appropriate files:

- **default_msgs.txt**: Random responses in any channel
- **mention_msgs.txt**: Responses when bot is mentioned
- **default_audio_msgs.txt**: Random audio responses
- **mention_audio_msgs.txt**: Audio responses when mentioned

Example content:
```txt
# default_msgs.txt
https://tenor.com/view/jetstream-sam-my-beloved-gif-22029076
lmao
nice one
```

```txt
# default_audio_msgs.txt
https://cdn.discordapp.com/attachments/123456/789012/sound.mp3
audio/laugh.wav
sounds/bruh.mp3
```

### 5. Run the Bot
For testing:
```bash
python bot.py
```

For production (Linux server):
```bash
# Create a systemd service file
sudo nano /etc/systemd/system/bruh-bot.service
```

Add this content (make sure to change `yourusername` and `/path/to/Bruh-Bot` to your actual username and path:
```ini
[Unit]
Description=Bruh Discord Bot
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/Bruh-Bot
ExecStart=/usr/bin/python3 /path/to/Bruh-Bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bruh-bot
sudo systemctl start bruh-bot
```

Check status:
```bash
sudo systemctl status bruh-bot
```

## 🎛️ Configuration Guide

### Getting Discord IDs
1. Enable Developer Mode in Discord (User Settings → Advanced)
2. Right-click on channels/roles/users to copy their IDs

### Audio File Setup
1. Create folders in your bot directory:
   ```bash
   mkdir audio sounds
   ```
2. Place your audio files in these folders (MP3, WAV, OGG formats)
3. Use relative paths in your audio message files:
   ```txt
   # default_audio_msgs.txt
   audio/bruh.mp3
   sounds/laugh.wav
   https://cdn.discordapp.com/attachments/123456/789012/funny.mp3
   ```

### File Permissions (Linux)
```bash
chmod +x bot.py
chown -R youruser:yourgroup /path/to/Bruh-Bot
```

## 🤖 Usage

### Slash Commands
- `/suggest-msg [message]` - Suggest a new message for the bot
- `/reload-msgs` - Manually reload all message files (admin only)
- `/msg-count` - Show current message counts in each category
- `/list-msgs [list_type]` - List messages from a specific category (admin only)

### Context Menu Commands
Right-click on any message or user to access:
- **"Suggest message"** - Submit the message content as a suggestion
- **"Rape member"** - Send a rape message to designated channel (if enabled)

### Bot Responses
- **Random Messages**: Bot will occasionally send random messages based on configured chance
- **Mentions**: Bot responds with special messages when mentioned
- **Audio**: Plays audio clips when configured to do so
- **Special Channel**: In designated channels, bot creates threads and adds reaction emojis

## 🔄 Updating the Bot

1. Pull the latest changes:
```bash
git pull origin main
```

2. Update dependencies if needed:
```bash
pip install -r requirements.txt --upgrade
```

3. Restart the bot:
```bash
# For systemd service
sudo systemctl restart bruh-bot

# For manual running
# Press Ctrl+C to stop, then run again
python bot.py
```

## 🚨 Troubleshooting

### Common Issues & Solutions

**"Login failed! Invalid TOKEN"**
- Verify your bot token in config.txt
- Get a new token from Discord Developer Portal

**"Channel not found" errors**
- Check that channel IDs are correct
- Ensure the bot has access to those channels
- Verify the bot is in the server

**Audio files not playing**
- Check file paths are correct relative to bot directory
- Ensure files have proper read permissions
- Verify file size is under 25MB
- Check bot has "Attach Files" permission in channels

**No random messages**
- Verify `ENABLE_RANDOM_MESSAGES=true`
- Check `RANDOM_MESSAGE_CHANCE` is set to a reasonable value
- Ensure default_msgs.txt has content
- Confirm bot has "Send Messages" permission

**Suggestions not working**
- Verify `ENABLE_SUGGESTIONS=true`
- Check all required channel/role IDs are set
- Ensure `AUTHORIZED_USER_ID` is correct for approval permissions

### Debugging Tips
- Check logs for detailed error messages
- Run bot in foreground mode to see real-time output
- Verify file permissions on message files
- Test with minimal configuration first

## 📜 License

This project is licensed under the [WTFPL License](http://www.wtfpl.net/) - Do What The Fuck You Want To Public License.

## 💬 Support

For questions or issues:
- Open an issue on the GitHub repository
- Check the logs for detailed error messages
- Consult the Discord.py documentation for API-specific issues

---

**Note**: This bot is intended for entertainment purposes. Use responsibly and ensure you have proper permissions in your Discord servers. The developer is not responsible for misuse of the bot or its features.