# Bruh Bot

A fun, modular Discord bot for silly interactions, random responses, and community message suggestions. Built with Discord.py for easy customization and deployment.

## Features

- **Random Messages**: Sends random GIFs, text, or audio messages in channels based on configurable chances.
- **Mention Responses**: Replies with specific messages when the bot is mentioned.
- **Audio Support**: Handles audio URLs or file paths for random or mention-based responses.
- **Message Suggestions**: Users can suggest new messages via context menus or slash commands; admins approve/reject them to add to lists.
- **Special Channel Handling**: Automatically creates threads in designated channels for certain messages.
- **Member Events**: Detects "chicken out" behavior (leaving shortly after joining) and sends notifications.
- **Admin Commands**: Slash commands for reloading messages, viewing counts, and listing messages.
- **Modular Architecture**: Organized into cogs for commands, events, and suggestions, making it easy to extend.
- **Configuration-Driven**: All settings managed via `config.txt` for easy setup without code changes.

## How It Works

The bot uses a modular structure inspired by Java classes:

- **Core Modules**:
  - `main.py`: Entry point that initializes the bot, loads cogs, and starts the event loop.
  - `config.py`: Loads and validates settings from `config.txt`.
  - `messages.py`: Manages loading/saving text and audio messages from files.

- **Cogs** (Discord.py extensions):
  - `cogs/events.py`: Handles Discord events like messages, member joins/leaves, and startup checks.
  - `cogs/commands.py`: Provides slash commands for admins.
  - `cogs/suggestions.py`: Manages the suggestion system with interactive buttons.

- **Utilities**:
  - `utils/embeds.py`: Creates formatted embeds for suggestions.

On startup, the bot validates configuration, loads messages, verifies Discord resources (channels/roles), syncs commands, and begins listening for events. It responds randomly or on triggers, with auto-reloading of messages at set intervals.

## Prerequisites

- Python 3.8+
- A Discord bot token (from [Discord Developer Portal](https://discord.com/developers/applications))
- VPS or server with Linux (Ubuntu/Debian recommended)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/NTNewHorizons/Bruh.git
   cd Bruh
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Bot**:
   - Edit `config.txt` with your settings (see Configuration section below).
   - Fill in required values like `TOKEN`, channel IDs, and role IDs from your Discord server.

4. **Prepare Message Files**:
   - Add messages to `default_msgs.txt`, `mention_msgs.txt`, `default_audio_msgs.txt`, and `mention_audio_msgs.txt`.
   - Messages can be text, GIF URLs (e.g., Tenor), or audio URLs/file paths.

## Configuration

All settings are in `config.txt`. Key sections:

- **Core**: `TOKEN` (your bot token).
- **Files**: Paths to message files (e.g., `DEFAULT_MSGS_FILE=default_msgs.txt`).
- **Channels/Roles**: IDs for suggestion channel, rape channel, etc.
- **Behaviors**: Chances for random messages (e.g., `RANDOM_MESSAGE_CHANCE=100` for 1% chance), timeouts, and messages.
- **Permissions**: `AUTHORIZED_USER_ID` for approving suggestions.
- **Toggles**: Enable/disable features like `ENABLE_RANDOM_MESSAGES=true`.

Run the bot once to validate config; it will report errors if channels/roles are missing.

## Deployment on VPS

1. **Set Up VPS**:
   - Choose a provider like DigitalOcean, Linode, or AWS EC2.
   - Use Ubuntu 20.04+ or Debian.
   - Update system: `sudo apt update && sudo apt upgrade`.

2. **Install Python and Git**:
   ```bash
   sudo apt install python3 python3-pip git
   ```

3. **Clone and Install**:
   ```bash
   git clone https://github.com/NTNewHorizons/Bruh.git
   cd Bruh
   pip3 install -r requirements.txt
   ```

4. **Configure**:
   - Edit `config.txt` with your Discord details.
   - Ensure the bot has necessary permissions in your server (e.g., send messages, manage channels).

5. **Run the Bot**:
   - For testing: `python3 main.py`
   - For production, use a process manager like `screen` or `systemd`:
     - With `screen`: `screen -S bruhbot python3 main.py` (detach with Ctrl+A+D)
     - With `systemd`: Create `/etc/systemd/system/bruhbot.service`:
       ```
       [Unit]
       Description=Bruh Discord Bot
       After=network.target

       [Service]
       Type=simple
       User=youruser
       WorkingDirectory=/path/to/Bruh
       ExecStart=/usr/bin/python3 main.py
       Restart=always

       [Install]
       WantedBy=multi-user.target
       ```
       Then: `sudo systemctl enable bruhbot && sudo systemctl start bruhbot`

6. **Monitor and Logs**:
   - Check logs with `sudo journalctl -u bruhbot -f` (for systemd).
   - Ensure firewall allows outbound connections (Discord uses ports 80/443).

7. **Updates**:
   - Pull changes: `git pull`
   - Restart: `sudo systemctl restart bruhbot`

## Usage

- Invite the bot to your server with the token.
- Use slash commands like `/reload-msgs` (admin), `/msg-count`, or `/suggest-msg`.
- Right-click messages to suggest them or use "Rape member".
- The bot will respond randomly or on mentions based on config.

## Troubleshooting

- **Login Failed**: Check `TOKEN` in `config.txt`.
- **Missing Channels/Roles**: Bot logs errors on startup; verify IDs.
- **No Responses**: Ensure features are enabled in config and bot has permissions.
- **File Errors**: Check file paths and permissions.

For issues, check console output or Discord logs.

## License

This project is open-source. Use at your own risk!
