# Bruh Bot - Modular Architecture

The bot has been refactored from a single `bot.py` file into a modular structure similar to Java classes. Each module has a specific responsibility.

## Project Structure

```
/workspaces/Bruh/
├── main.py              # Entry point - starts the bot and loads cogs
├── config.py            # Configuration loading and validation
├── messages.py          # Message file handling (load, save, initialize)
├── config.txt           # Configuration file (user-editable)
├── default_msgs.txt     # Default messages list
├── mention_msgs.txt     # Mention messages list
├── default_audio_msgs.txt     # Default audio messages list (URLs or file paths)
├── mention_audio_msgs.txt     # Mention audio messages list (URLs or file paths)
│
├── cogs/                # Discord.py Cogs (modular command/event handlers)
│   ├── suggestions.py   # Suggestion system, context menus, approval buttons
│   ├── commands.py      # Slash commands (reload, count, list)
│   └── events.py        # Event handlers (on_ready, on_message, member events)
│
├── utils/               # Utility modules
│   └── embeds.py        # Embed creation helpers
│
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Module Descriptions

### Core Modules

- **main.py**: Entry point that initializes the bot, loads all cogs, and starts the event loop
- **config.py**: Loads `config.txt`, validates configuration, and provides config dictionary to other modules
- **messages.py**: Handles loading/saving messages and audio messages from files and initializing empty files with defaults

### Cogs (Discord.py Extension Pattern)

Cogs are Discord.py's extension system - each cog is a class that handles related commands/events:

#### `cogs/suggestions.py` - SuggestionsCog
- Context menu: "Suggest message" - suggest messages from message reactions
- Slash command: `/suggest-msg` - suggest messages via text input
- Context menu: "Rape member" - send rape notifications
- `MsgSuggestionView` - Interactive buttons for approving suggestions to different lists (text and audio)
  - Text buttons: Reject, Default, Mention, Both
  - Audio buttons: Reject, Default Audio, Mention Audio, Both Audio

#### `cogs/commands.py` - CommandsCog
- `/reload-msgs` - Manually reload message lists (including audio) from files
- `/msg-count` - Display current message counts (including audio)
- `/list-msgs` - List all messages in a list (paginated)

#### `cogs/events.py` - EventsCog
- `on_ready()` - Verify channels/roles exist, sync command tree
- `on_message()` - Handle random messages, mentions, special channel threads
- `on_member_join()` - Track joins for chicken out detection
- `on_member_remove()` - Detect chicken outs
- `on_app_command_error()` - Handle command errors

### Utils

#### `utils/embeds.py`
- `create_suggestion_embed()` - Helper to create formatted embeds for suggestions

## How to Run

### Old Way (Deprecated)
```bash
python bot.py
```

### New Way (Modular)
```bash
python main.py
```

## Key Benefits of Modular Structure

1. **Separation of Concerns**: Each module has one clear responsibility
   - Configuration is separate from commands
   - Message handling is separate from events
   - Commands are grouped by function

2. **Easier Maintenance**: 
   - Bug in suggestions? Check `cogs/suggestions.py`
   - Bug in message handling? Check `messages.py`
   - Configuration issue? Check `config.py`

3. **Scalability**: Easy to add new features
   - New command set? Create `cogs/moderation.py`
   - New utility? Add to `utils/`
   - Cogs are auto-discovered and loaded

4. **Testability**: Each module can be tested independently

5. **Code Reuse**: Shared utilities in `utils/` can be used by multiple cogs

## Adding New Cogs

Create a new file in `cogs/` with a `Setup` function:

```python
# cogs/newfeature.py
from discord.ext import commands

class NewFeatureCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def mycommand(self, ctx):
        await ctx.send("Hello!")

async def setup(bot):
    await bot.add_cog(NewFeatureCog(bot))
```

The cog will be automatically loaded when the bot starts.

## Shared State

Message lists (both text and audio) are shared across cogs via direct assignment in `main.py`:
```python
cogs.suggestions.default_msgs = default_msgs
cogs.suggestions.mention_msgs = mention_msgs
cogs.suggestions.default_audio_msgs = default_audio_msgs
cogs.suggestions.mention_audio_msgs = mention_audio_msgs
# ... etc for all cogs
```

This allows cogs to read/update the same message lists.

## Audio Message System

The bot now supports sending audio messages just like text messages. Audio messages can be:
- **Local files**: File paths to audio files (e.g., `./audio/hello.mp3`)
- **Discord URLs**: Direct links to Discord CDN attachments
- **External URLs**: Links to audio hosted externally

### Configuration for Audio Messages

In `config.txt`:
- `DEFAULT_AUDIO_MSGS_FILE` - File containing default audio messages
- `MENTION_AUDIO_MSGS_FILE` - File containing mention audio messages
- `RANDOM_AUDIO_MESSAGE_CHANCE` - Chance to send random audio (e.g., `200` = 1 in 200)
- `ENABLE_RANDOM_AUDIO_MESSAGES` - Enable/disable random audio messages
- `ENABLE_MENTION_AUDIO_RESPONSES` - Enable/disable audio responses to mentions

### How to Use Audio Messages

1. Add audio file paths or URLs to `default_audio_msgs.txt` or `mention_audio_msgs.txt`
2. One audio per line
3. Audio will be sent randomly or in response to mentions based on configuration
4. Use the suggestion system to propose audio messages - approvers can accept them to either list

## Configuration

All configuration is in `config.txt`. The `config.py` module loads it on startup and provides a `config` dictionary that all modules import:

```python
from config import config

# Use anywhere
CHANNEL_ID = config['SUGGESTION_CHANNEL_ID']
```
