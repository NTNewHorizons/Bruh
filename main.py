"""
Main entry point for the Discord bot
"""
import discord
import asyncio
import os
from discord.ext import commands
from config import config
from messages import load_msgs_from_file, initialize_msg_files

# Global message lists (shared with cogs)
default_msgs = []
mention_msgs = []


def initialize_bot():
    """Initialize bot with intents"""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    
    bot = commands.Bot(intents=intents)
    return bot


async def load_cogs(bot):
    """Load all cogs from the cogs directory"""
    cogs_dir = 'cogs'
    
    if not os.path.exists(cogs_dir):
        print(f"❌ Cogs directory '{cogs_dir}' not found!")
        return
    
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and not filename.startswith('_'):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f'cogs.{cog_name}')
                print(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                print(f"❌ Failed to load cog {cog_name}: {e}")


def main():
    """Main function to start the bot"""
    global default_msgs, mention_msgs
    
    print("🚀 Starting bot...")
    
    # Load message lists
    default_msgs = load_msgs_from_file(config['DEFAULT_MSGS_FILE'])
    mention_msgs = load_msgs_from_file(config['MENTION_MSGS_FILE'])
    
    # Initialize message files if empty
    try:
        initialize_msg_files(default_msgs, mention_msgs)
        # Reload after initialization
        default_msgs = load_msgs_from_file(config['DEFAULT_MSGS_FILE'])
        mention_msgs = load_msgs_from_file(config['MENTION_MSGS_FILE'])
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
    
    # Update global message lists in cogs
    import cogs.suggestions
    import cogs.commands
    import cogs.events
    cogs.suggestions.default_msgs = default_msgs
    cogs.suggestions.mention_msgs = mention_msgs
    cogs.commands.default_msgs = default_msgs
    cogs.commands.mention_msgs = mention_msgs
    cogs.events.default_msgs = default_msgs
    cogs.events.mention_msgs = mention_msgs
    
    # Initialize and run bot
    bot = initialize_bot()
    
    @bot.event
    async def on_ready_setup():
        """Setup cogs when bot is ready"""
        if not hasattr(bot, 'cogs_loaded'):
            await load_cogs(bot)
            bot.cogs_loaded = True
    
    # Load cogs before running
    asyncio.run(load_cogs(bot))
    
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
        print(f"\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
