"""
Main entry point for the Discord bot
"""
import discord
import asyncio
import os
from discord.ext import commands
from config import config


def setup_bot():
    """Initialize bot with intents"""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    return commands.Bot(intents=intents)


async def load_cogs(bot):
    """Load all cogs from the cogs directory"""
    cogs_dir = 'cogs'
    if not os.path.exists(cogs_dir):
        print(f"❌ Cogs directory not found!")
        return
    
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and not filename.startswith('_'):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f'cogs.{cog_name}')
                print(f"✅ Loaded: {cog_name}")
            except Exception as e:
                print(f"❌ Failed to load {cog_name}: {e}")


async def main():
    """Start the bot"""
    bot = setup_bot()
    
    print("🚀 Starting bot...")
    await load_cogs(bot)
    
    try:
        await bot.start(config['TOKEN'])
    except discord.LoginFailure:
        print("❌ Login failed! Invalid TOKEN in config.txt")
        print("   Get it from: https://discord.com/developers/applications")
    except discord.HTTPException as e:
        print(f"❌ Network error: {e}")
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
