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
- **messages.py**: Handles loading/saving messages from files and initializing empty files with defaults

### Cogs (Discord.py Extension Pattern)

Cogs are Discord.py's extension system - each cog is a class that handles related commands/events:

#### `cogs/suggestions.py` - SuggestionsCog
- Context menu: "Suggest message" - suggest messages from message reactions
- Slash command: `/suggest-msg` - suggest messages via text input
- Context menu: "Rape member" - send rape notifications
- `MsgSuggestionView` - Interactive buttons for approving suggestions to different lists

#### `cogs/commands.py` - CommandsCog
- `/reload-msgs` - Manually reload message lists from files
- `/msg-count` - Display current message counts
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

Message lists are shared across cogs via direct assignment in `main.py`:
```python
cogs.suggestions.default_msgs = default_msgs
cogs.suggestions.mention_msgs = mention_msgs
# ... etc for all cogs
```

This allows cogs to read/update the same message lists.

## Configuration

All configuration is in `config.txt`. The `config.py` module loads it on startup and provides a `config` dictionary that all modules import:

```python
from config import config

# Use anywhere
CHANNEL_ID = config['SUGGESTION_CHANNEL_ID']
```
