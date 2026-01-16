"""
Suggestions cog for message suggestion functionality
"""
import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
from config import config
from messages import MessageManager
from utils.embeds import create_suggestion_embed


class MsgSuggestionView(View):
    """View with buttons for accepting/rejecting message suggestions"""
    
    def __init__(self, msg_manager, author_id, msg_content, message_id):
        super().__init__(timeout=None)
        self.msg_manager = msg_manager
        self.author_id = author_id
        self.msg_content = msg_content
        self.message_id = message_id
    
    async def _check_auth(self, interaction):
        """Check authorization and handle failure"""
        if interaction.user.id != config['AUTHORIZED_USER_ID']:
            await interaction.response.send_message("❌ Not authorized.", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red, emoji="🗑️")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n❌ **Rejected by {interaction.user.mention}**",
            embed=None,
            view=None
        )
        await interaction.response.defer()
    
    @discord.ui.button(label="✅ Default", style=discord.ButtonStyle.green, emoji="📌")
    async def accept_default_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        added = self.msg_manager.add_to_list(self.msg_content, 'default')
        status = "✅ Added!" if added else "⚠️ Already in list!"
        await interaction.response.send_message(status, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Default by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Mention", style=discord.ButtonStyle.green, emoji="👋")
    async def accept_mention_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        added = self.msg_manager.add_to_list(self.msg_content, 'mention')
        status = "✅ Added!" if added else "⚠️ Already in list!"
        await interaction.response.send_message(status, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Mention by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Both", style=discord.ButtonStyle.blurple, emoji="✨")
    async def accept_both_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        d = self.msg_manager.add_to_list(self.msg_content, 'default')
        m = self.msg_manager.add_to_list(self.msg_content, 'mention')
        status = "✅ Added!" if (d or m) else "⚠️ Already in both!"
        await interaction.response.send_message(status, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Both by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Default Audio", style=discord.ButtonStyle.green, emoji="🎙️")
    async def accept_default_audio_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        added = self.msg_manager.add_to_list(self.msg_content, 'default_audio')
        status = "✅ Added!" if added else "⚠️ Already in list!"
        await interaction.response.send_message(status, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Default Audio by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Mention Audio", style=discord.ButtonStyle.green, emoji="🎤")
    async def accept_mention_audio_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        added = self.msg_manager.add_to_list(self.msg_content, 'mention_audio')
        status = "✅ Added!" if added else "⚠️ Already in list!"
        await interaction.response.send_message(status, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Mention Audio by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Both Audio", style=discord.ButtonStyle.blurple, emoji="🎵")
    async def accept_both_audio_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_auth(interaction):
            return
        d = self.msg_manager.add_to_list(self.msg_content, 'default_audio')
        m = self.msg_manager.add_to_list(self.msg_content, 'mention_audio')
        status = "✅ Added!" if (d or m) else "⚠️ Already in both!"
        await interaction.response.send_message(status, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Both Audio by {interaction.user.mention}**",
            embed=None,
            view=None
        )


class SuggestionsCog(commands.Cog):
    """Cog for message suggestion commands and context menus"""
    
    def __init__(self, bot, msg_manager: MessageManager):
        self.bot = bot
        self.msg_manager = msg_manager
    
    async def _submit_suggestion(self, interaction: discord.Interaction, msg_content: str, author=None, url=None):
        """Helper to submit suggestion"""
        if not config['ENABLE_SUGGESTIONS']:
            await interaction.response.send_message("❌ Suggestions disabled.", ephemeral=True)
            return
        
        target_channel = self.bot.get_channel(config['SUGGESTION_CHANNEL_ID'])
        if not target_channel:
            await interaction.response.send_message("❌ Channel not found.", ephemeral=True)
            return
        
        try:
            embed = create_suggestion_embed(interaction, msg_content, author, url)
            view = MsgSuggestionView(self.msg_manager, interaction.user.id, msg_content, interaction.id)
            
            await target_channel.send(
                content=f"<@&{config['SUGGESTION_PING_ROLE_ID']}> New suggestion!",
                embed=embed,
                view=view
            )
            await interaction.response.send_message("✅ Submitted!", ephemeral=True)
        except Exception as e:
            print(f"❌ Error: {e}")
            await interaction.response.send_message("❌ Error submitting.", ephemeral=True)
    
    @app_commands.context_menu(name="Suggest message")
    async def suggest_message_context(self, interaction: discord.Interaction, message: discord.Message):
        if not message.content:
            await interaction.response.send_message("❌ No text content!", ephemeral=True)
            return
        await self._submit_suggestion(interaction, message.content, message.author, message.jump_url)
    
    @app_commands.command(name="suggest-msg", description="Suggest a message")
    @app_commands.describe(message="Message to suggest")
    async def suggest_msg_slash(self, interaction: discord.Interaction, message: str):
        await self._submit_suggestion(interaction, message)
    
    @app_commands.context_menu(name="Rape member")
    async def rape_user(self, interaction: discord.Interaction, member: discord.Member):
        if not config['ENABLE_RAPE_COMMAND']:
            await interaction.response.send_message("❌ Disabled.", ephemeral=True)
            return
        
        target_channel = self.bot.get_channel(config['RAPE_CHANNEL_ID'])
        if not target_channel:
            await interaction.response.send_message("❌ Channel not found.", ephemeral=True)
            return
        
        try:
            await target_channel.send(f"{interaction.user.mention} raped {member.mention}")
            await interaction.response.send_message(f"✅ Done!", ephemeral=True)
        except Exception as e:
            print(f"❌ Error: {e}")
            await interaction.response.send_message("❌ Error.", ephemeral=True)


async def setup(bot):
    """Setup function to load the cog"""
    msg_manager = MessageManager()
    await bot.add_cog(SuggestionsCog(bot, msg_manager))
