"""
Commands cog for slash commands (reload messages, message counts, list messages)
"""
import discord
from discord.ext import commands
from discord import app_commands
from config import config
from messages import MessageManager


class CommandsCog(commands.Cog):
    """Cog for general bot commands"""
    
    def __init__(self, bot, msg_manager: MessageManager):
        self.bot = bot
        self.msg_manager = msg_manager
    
    @app_commands.command(name="reload-msgs", description="Reload message lists from files")
    @app_commands.default_permissions(administrator=True)
    async def reload_msgs(self, interaction: discord.Interaction):
        """Reload all message lists from files"""
        self.msg_manager.reload()
        counts = self.msg_manager.get_counts()
        
        response = f"✅ Reloaded!\n📊 Default: {counts['default']}\n📊 Mention: {counts['mention']}\n🎙️ Audio: {counts['default_audio'] + counts['mention_audio']}"
        await interaction.response.send_message(response, ephemeral=True)
        print(f"🔄 Reloaded by {interaction.user.name}: {counts}")
    
    @app_commands.command(name="msg-count", description="Show current message counts")
    async def msg_count(self, interaction: discord.Interaction):
        """Show current message counts"""
        counts = self.msg_manager.get_counts()
        response = f"📊 Counts:\n🔹 Default: {counts['default']}\n🔹 Mention: {counts['mention']}\n🎙️ Default: {counts['default_audio']}\n🎙️ Mention: {counts['mention_audio']}"
        await interaction.response.send_message(response, ephemeral=True)
    
    @app_commands.command(name="list-msgs", description="List messages from a list")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(list_type="Which list: 'default' or 'mention'")
    async def list_msgs(self, interaction: discord.Interaction, list_type: str = "default"):
        """List messages from specified list"""
        list_map = {
            'default': (self.msg_manager.default, 'Default messages'),
            'mention': (self.msg_manager.mention, 'Mention messages'),
        }
        
        if list_type.lower() not in list_map:
            await interaction.response.send_message("❌ Use 'default' or 'mention'.", ephemeral=True)
            return
        
        msgs, title = list_map[list_type.lower()]
        
        if not msgs:
            await interaction.response.send_message(f"📭 {title} is empty.", ephemeral=True)
            return
        
        # Paginate in chunks of 10
        chunk_size = 10
        chunks = [msgs[i:i + chunk_size] for i in range(0, len(msgs), chunk_size)]
        
        for page, chunk in enumerate(chunks, 1):
            embed = discord.Embed(
                title=f"{title} (Page {page}/{len(chunks)})",
                color=discord.Color(int(config['SUCCESS_COLOR'], 16))
            )
            for i, msg in enumerate(chunk, 1):
                embed.add_field(name=f"{i}.", value=msg[:100], inline=False)
            
            if page == 1:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    """Setup function to load the cog"""
    msg_manager = MessageManager()
    await bot.add_cog(CommandsCog(bot, msg_manager))
