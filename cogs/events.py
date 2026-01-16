"""
Events cog for Discord event handlers (on_ready, on_message, member join/leave, etc.)
"""
import discord
import random
from discord.ext import commands
from config import config
from messages import load_msgs_from_file, save_msgs_to_file


# Global references (shared with main bot)
default_msgs = []
mention_msgs = []
recent_joins = {}


class EventsCog(commands.Cog):
    """Cog for handling Discord events"""
    
    def __init__(self, bot):
        self.bot = bot
        self.last_msg_reload = discord.utils.utcnow()
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Bot ready event"""
        print(f'✅ {self.bot.user} is online and ready!')
        print(f'📊 Initial message counts: Default={len(default_msgs)}, Mention={len(mention_msgs)}')
        
        if len(default_msgs) == 0:
            print(f"⚠️  Warning: No default messages loaded. The bot won't respond to random triggers.")
        if len(mention_msgs) == 0:
            print(f"⚠️  Warning: No mention messages loaded. The bot won't respond to mentions.")
        
        # Verify all configured channels exist
        channels_to_check = [
            (config['SUGGESTION_CHANNEL_ID'], "Suggestion channel"),
            (config['RAPE_CHANNEL_ID'], "Rape command channel"),
            (config['SPECIAL_MESSAGE_CHANNEL_ID'], "Special message channel"),
            (config['CHICKEN_OUT_CHANNEL_ID'], "Chicken out channel")
        ]
        
        for channel_id, channel_name in channels_to_check:
            channel = self.bot.get_channel(channel_id)
            if channel:
                print(f"✅ {channel_name} found: #{channel.name}")
            else:
                print(f"❌ {channel_name} NOT FOUND (ID: {channel_id}). Please check your config!")
        
        # Verify role exists
        suggestion_role = None
        for guild in self.bot.guilds:
            suggestion_role = guild.get_role(config['SUGGESTION_PING_ROLE_ID'])
            if suggestion_role:
                print(f"✅ Suggestion ping role found: @{suggestion_role.name}")
                break
        
        if not suggestion_role:
            print(f"❌ Suggestion ping role NOT FOUND (ID: {config['SUGGESTION_PING_ROLE_ID']}). Please check your config!")
        
        # Ensure files exist with current data
        try:
            save_msgs_to_file(config['DEFAULT_MSGS_FILE'], default_msgs)
            save_msgs_to_file(config['MENTION_MSGS_FILE'], mention_msgs)
        except Exception as e:
            print(f"❌ Error saving message files: {e}")
        
        # Sync command tree
        try:
            await self.bot.tree.sync()
            print('🔄 Command tree synced successfully')
        except Exception as e:
            print(f"❌ Error syncing command tree: {e}")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Message event handler"""
        if message.author == self.bot.user:
            return
        
        # Auto-reload message lists every configured interval
        now = discord.utils.utcnow()
        if (now - self.last_msg_reload).total_seconds() >= config['MESSAGE_RELOAD_INTERVAL']:
            global default_msgs, mention_msgs
            default_msgs = load_msgs_from_file(config['DEFAULT_MSGS_FILE'])
            mention_msgs = load_msgs_from_file(config['MENTION_MSGS_FILE'])
            self.last_msg_reload = now
            print(f"🔄 Periodic reload: Default={len(default_msgs)}, Mention={len(mention_msgs)}")
        
        # Special channel handling
        if config['ENABLE_SPECIAL_CHANNEL'] and message.channel.id == config['SPECIAL_MESSAGE_CHANNEL_ID']:
            try:
                yes_emoji = f"<:yes:{config['SPECIAL_CHANNEL_YES_EMOJI']}>" if config['SPECIAL_CHANNEL_YES_EMOJI'] else '✅'
                no_emoji = f"<:no:{config['SPECIAL_CHANNEL_NO_EMOJI']}>" if config['SPECIAL_CHANNEL_NO_EMOJI'] else '❌'
                
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
        
        # Send random message based on configured chance
        if config['ENABLE_RANDOM_MESSAGES'] and random.randint(1, config['RANDOM_MESSAGE_CHANCE']) == 1 and default_msgs:
            msg = random.choice(default_msgs)
            try:
                await message.channel.send(msg)
            except discord.Forbidden:
                print(f"❌ No permission to send messages in #{message.channel.name}")
            except Exception as e:
                print(f"❌ Error sending random message: {e}")
        
        # If bot is mentioned, send message from mention list
        if config['ENABLE_MENTION_RESPONSES'] and self.bot.user.mentioned_in(message) and mention_msgs:
            msg = random.choice(mention_msgs)
            try:
                await message.channel.send(msg)
            except discord.Forbidden:
                print(f"❌ No permission to send messages in #{message.channel.name}")
            except Exception as e:
                print(f"❌ Error sending mention message: {e}")
        
        await self.bot.process_commands(message)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Member join event"""
        try:
            if config['ENABLE_CHICKEN_OUT']:
                recent_joins[member.id] = {
                    "time": discord.utils.utcnow(),
                    "channel": member.guild.system_channel
                }
            print(f"👋 {member.name} joined the server")
        except Exception as e:
            print(f"❌ Error in on_member_join: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Member remove event"""
        try:
            if config['ENABLE_CHICKEN_OUT'] and member.id in recent_joins:
                join_time = recent_joins[member.id]["time"]
                leave_time = discord.utils.utcnow()
                if (leave_time - join_time).total_seconds() <= config['CHICKEN_OUT_TIMEOUT']:
                    channel = self.bot.get_channel(config['CHICKEN_OUT_CHANNEL_ID'])
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
    
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        """Slash command error handler"""
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


async def setup(bot):
    """Setup function to load the cog"""
    await bot.add_cog(EventsCog(bot))
