"""
Events cog for Discord event handlers (on_ready, on_message, member join/leave, etc.)
"""
import discord
import random
import os
from discord.ext import commands
from config import config
from messages import MessageManager


class EventsCog(commands.Cog):
    """Cog for handling Discord events"""
    
    def __init__(self, bot, msg_manager: MessageManager):
        self.bot = bot
        self.msg_manager = msg_manager
        self.last_msg_reload = discord.utils.utcnow()
        self.recent_joins = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Bot ready event"""
        print(f'✅ {self.bot.user} is online and ready!')
        counts = self.msg_manager.get_counts()
        print(f'📊 Loaded: Default={counts["default"]}, Mention={counts["mention"]}')
        
        # Verify channels exist
        for channel_id, name in [
            (config['SUGGESTION_CHANNEL_ID'], "Suggestion"),
            (config['RAPE_CHANNEL_ID'], "Rape"),
            (config['SPECIAL_MESSAGE_CHANNEL_ID'], "Special"),
            (config['CHICKEN_OUT_CHANNEL_ID'], "Chicken out")
        ]:
            channel = self.bot.get_channel(channel_id)
            print(f"{'✅' if channel else '❌'} {name} channel: #{channel.name if channel else 'NOT FOUND'}")
        
        # Verify role exists
        for guild in self.bot.guilds:
            role = guild.get_role(config['SUGGESTION_PING_ROLE_ID'])
            if role:
                print(f"✅ Role found: @{role.name}")
                break
        else:
            print(f"❌ Suggestion role NOT FOUND")
        
        # Sync commands
        try:
            await self.bot.tree.sync()
            print('🔄 Commands synced')
        except Exception as e:
            print(f"❌ Sync error: {e}")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Message event handler"""
        if message.author == self.bot.user:
            return
        
        # Auto-reload message lists every N seconds
        now = discord.utils.utcnow()
        if (now - self.last_msg_reload).total_seconds() >= config['MESSAGE_RELOAD_INTERVAL']:
            self.msg_manager.reload()
            self.last_msg_reload = now
            counts = self.msg_manager.get_counts()
            print(f"🔄 Reloaded: {counts}")
        
        # Special channel: add reactions and create thread
        if config['ENABLE_SPECIAL_CHANNEL'] and message.channel.id == config['SPECIAL_MESSAGE_CHANNEL_ID']:
            try:
                yes_emoji = config['SPECIAL_CHANNEL_YES_EMOJI'] or '✅'
                no_emoji = config['SPECIAL_CHANNEL_NO_EMOJI'] or '❌'
                
                await message.add_reaction(yes_emoji)
                await message.add_reaction(no_emoji)
                
                thread_name = (message.content[:100] if message.content.strip() else "Discussion")
                await message.create_thread(name=thread_name)
            except Exception as e:
                print(f"❌ Special channel error: {e}")
        
        # Random message
        if config['ENABLE_RANDOM_MESSAGES'] and self.msg_manager.default:
            if random.randint(1, config['RANDOM_MESSAGE_CHANCE']) == 1:
                await self._send_msg(message.channel, random.choice(self.msg_manager.default))
        
        # Random audio message
        if config['ENABLE_RANDOM_AUDIO_MESSAGES'] and self.msg_manager.default_audio:
            if random.randint(1, config['RANDOM_AUDIO_MESSAGE_CHANCE']) == 1:
                await self._send_audio(message.channel, random.choice(self.msg_manager.default_audio))
        
        # Mention responses
        if config['ENABLE_MENTION_RESPONSES'] and self.bot.user.mentioned_in(message) and self.msg_manager.mention:
            await self._send_msg(message.channel, random.choice(self.msg_manager.mention))
        
        # Mention audio responses
        if config['ENABLE_MENTION_AUDIO_RESPONSES'] and self.bot.user.mentioned_in(message) and self.msg_manager.mention_audio:
            await self._send_audio(message.channel, random.choice(self.msg_manager.mention_audio))
    
    async def _send_msg(self, channel, msg):
        """Send a text message"""
        try:
            await channel.send(msg)
        except discord.Forbidden:
            print(f"❌ No permission in #{channel.name}")
        except Exception as e:
            print(f"❌ Error sending message: {e}")
    
    async def _send_audio(self, channel, audio_source):
        """Send an audio message (URL or file)"""
        try:
            if audio_source.startswith(('http://', 'https://')):
                await channel.send(audio_source)
            elif os.path.exists(audio_source):
                await channel.send(file=discord.File(audio_source))
            else:
                print(f"⚠️ Audio not found: {audio_source}")
        except discord.Forbidden:
            print(f"❌ No permission in #{channel.name}")
        except Exception as e:
            print(f"❌ Error sending audio: {e}")
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if config['ENABLE_CHICKEN_OUT']:
            self.recent_joins[member.id] = {"time": discord.utils.utcnow()}
        print(f"👋 {member.name} joined")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if config['ENABLE_CHICKEN_OUT'] and member.id in self.recent_joins:
            join_time = self.recent_joins[member.id]["time"]
            if (discord.utils.utcnow() - join_time).total_seconds() <= config['CHICKEN_OUT_TIMEOUT']:
                channel = self.bot.get_channel(config['CHICKEN_OUT_CHANNEL_ID'])
                if channel:
                    try:
                        await channel.send(f"{member.mention} chickened out\n{config['CHICKENED_OUT_MSG']}")
                        print(f"🐔 {member.name} chickened out")
                    except Exception as e:
                        print(f"❌ Error: {e}")
            del self.recent_joins[member.id]
    
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        print(f"❌ Command error: {error}")
        try:
            msg = f"❌ Error: {error}"
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except Exception as e:
            print(f"❌ Error handler failed: {e}")



async def setup(bot):
    """Setup function to load the cog"""
    msg_manager = MessageManager()
    await bot.add_cog(EventsCog(bot, msg_manager))
