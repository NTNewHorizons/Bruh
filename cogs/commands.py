"""
Commands cog for slash commands (reload messages, message counts, list messages)
"""
import discord
from discord.ext import commands
from discord import app_commands
from config import config
from messages import load_msgs_from_file, load_audio_msgs_from_file


# Global references (shared with main bot)
default_msgs = []
mention_msgs = []
default_audio_msgs = []
mention_audio_msgs = []


class CommandsCog(commands.Cog):
    """Cog for general bot commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @app_commands.command(name="reload-msgs", description="Manually reload message lists from files")
    @app_commands.default_permissions(administrator=True)
    async def reload_msgs(self, interaction: discord.Interaction):
        """Manually reload message lists from files"""
        global default_msgs, mention_msgs, default_audio_msgs, mention_audio_msgs
        default_msgs = load_msgs_from_file(config['DEFAULT_MSGS_FILE'])
        mention_msgs = load_msgs_from_file(config['MENTION_MSGS_FILE'])
        default_audio_msgs = load_audio_msgs_from_file(config['DEFAULT_AUDIO_MSGS_FILE'])
        mention_audio_msgs = load_audio_msgs_from_file(config['MENTION_AUDIO_MSGS_FILE'])
        await interaction.response.send_message(
            f"✅ Message lists manually reloaded!\n📊 Default messages: {len(default_msgs)}\n📊 Mention messages: {len(mention_msgs)}\n🎙️ Default audio: {len(default_audio_msgs)}\n🎙️ Mention audio: {len(mention_audio_msgs)}",
            ephemeral=True
        )
        print(f"🔄 Manual reload by {interaction.user.name}: Default={len(default_msgs)}, Mention={len(mention_msgs)}, Default Audio={len(default_audio_msgs)}, Mention Audio={len(mention_audio_msgs)}")
    
    @commands.command()
    @app_commands.command(name="msg-count", description="Show current message counts")
    async def msg_count(self, interaction: discord.Interaction):
        """Show current message counts"""
        await interaction.response.send_message(
            f"📊 Current message counts:\n🔹 Default messages: {len(default_msgs)}\n🔹 Mention messages: {len(mention_msgs)}\n🎙️ Default audio: {len(default_audio_msgs)}\n🎙️ Mention audio: {len(mention_audio_msgs)}",
            ephemeral=True
        )
    
    @commands.command()
    @app_commands.command(name="list-msgs", description="List messages from specified list")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(list_type="Which list to display: 'default' or 'mention'")
    async def list_msgs(self, interaction: discord.Interaction, list_type: str = "default"):
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
        
        chunk_size = 10
        chunks = [msgs[i:i + chunk_size] for i in range(0, len(msgs), chunk_size)]
        
        if chunks:
            embed = discord.Embed(
                title=f"{title} (Page 1/{len(chunks)})",
                color=discord.Color(int(config['SUCCESS_COLOR'], 16))
            )
            
            chunk = chunks[0]
            for j, msg in enumerate(chunk, 1):
                embed.add_field(
                    name=f"{j}. Message",
                    value=msg,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            for i, chunk in enumerate(chunks[1:], 1):
                embed = discord.Embed(
                    title=f"{title} (Page {i+1}/{len(chunks)})",
                    color=discord.Color(int(config['SUCCESS_COLOR'], 16))
                )
                
                for j, msg in enumerate(chunk, 1):
                    embed.add_field(
                        name=f"{j + i*chunk_size}. Message",
                        value=msg,
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    """Setup function to load the cog"""
    await bot.add_cog(CommandsCog(bot))
