"""
Suggestions cog for message suggestion functionality
"""
import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
from config import config
from messages import load_msgs_from_file, save_msgs_to_file
from utils.embeds import create_suggestion_embed


# Global references (shared with main bot)
default_msgs = []
mention_msgs = []


class MsgSuggestionView(View):
    """View with buttons for accepting/rejecting message suggestions"""
    def __init__(self, author_id, msg_content, message_id):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.msg_content = msg_content
        self.message_id = message_id
    
    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red, emoji="🗑️")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Reject button handler"""
        if interaction.user.id != config['AUTHORIZED_USER_ID']:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return
        
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n❌ **Rejected by {interaction.user.mention}**",
            embed=None,
            view=None
        )
        await interaction.response.defer()
    
    @discord.ui.button(label="✅ Default", style=discord.ButtonStyle.green, emoji="📌")
    async def accept_default_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Accept to default list button handler"""
        if interaction.user.id != config['AUTHORIZED_USER_ID']:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return
        
        global default_msgs
        
        default_msgs = load_msgs_from_file(config['DEFAULT_MSGS_FILE'])
        
        if self.msg_content in default_msgs:
            await interaction.response.send_message("⚠️ This message is already in the default list!", ephemeral=True)
            return
        
        default_msgs.append(self.msg_content)
        save_msgs_to_file(config['DEFAULT_MSGS_FILE'], default_msgs)
        
        await interaction.response.send_message(f"✅ Message added to default list!", ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Default by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Mention", style=discord.ButtonStyle.green, emoji="👋")
    async def accept_mention_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Accept to mention list button handler"""
        if interaction.user.id != config['AUTHORIZED_USER_ID']:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return
        
        global mention_msgs
        
        mention_msgs = load_msgs_from_file(config['MENTION_MSGS_FILE'])
        
        if self.msg_content in mention_msgs:
            await interaction.response.send_message("⚠️ This message is already in the mention list!", ephemeral=True)
            return
        
        mention_msgs.append(self.msg_content)
        save_msgs_to_file(config['MENTION_MSGS_FILE'], mention_msgs)
        
        await interaction.response.send_message(f"✅ Message added to mention list!", ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Mention by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Both", style=discord.ButtonStyle.blurple, emoji="✨")
    async def accept_both_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Accept to both lists button handler"""
        if interaction.user.id != config['AUTHORIZED_USER_ID']:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return
        
        global default_msgs, mention_msgs
        
        default_msgs = load_msgs_from_file(config['DEFAULT_MSGS_FILE'])
        mention_msgs = load_msgs_from_file(config['MENTION_MSGS_FILE'])
        
        added_to_default = False
        added_to_mention = False
        
        if self.msg_content not in default_msgs:
            default_msgs.append(self.msg_content)
            added_to_default = True
        
        if self.msg_content not in mention_msgs:
            mention_msgs.append(self.msg_content)
            added_to_mention = True
        
        save_msgs_to_file(config['DEFAULT_MSGS_FILE'], default_msgs)
        save_msgs_to_file(config['MENTION_MSGS_FILE'], mention_msgs)
        
        status_message = ""
        if not added_to_default and not added_to_mention:
            status_message = "⚠️ This message was already in both lists!"
        elif added_to_default and added_to_mention:
            status_message = "✅ Message added to both lists!"
        elif added_to_default:
            status_message = "✅ Message added to default list! (Already in mention list)"
        elif added_to_mention:
            status_message = "✅ Message added to mention list! (Already in default list)"
        
        await interaction.response.send_message(status_message, ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Both by {interaction.user.mention}**",
            embed=None,
            view=None
        )


class SuggestionsCog(commands.Cog):
    """Cog for message suggestion commands and context menus"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @bot.tree.context_menu(name="Suggest message")
    async def suggest_message_context(self, interaction: discord.Interaction, message: discord.Message):
        """Context menu command to suggest a message for the bot"""
        
        if not config['ENABLE_SUGGESTIONS']:
            await interaction.response.send_message(
                "❌ Message suggestions are currently disabled.",
                ephemeral=True
            )
            return
        
        if not message.content:
            await interaction.response.send_message(
                "❌ This message has no text content to suggest!",
                ephemeral=True
            )
            return
        
        target_channel = self.bot.get_channel(config['SUGGESTION_CHANNEL_ID'])
        if not target_channel:
            await interaction.response.send_message(
                "❌ Could not find the target channel. Please contact an administrator.",
                ephemeral=True
            )
            return
        
        msg_content = message.content
        
        try:
            embed = create_suggestion_embed(interaction, msg_content, message.author, message.jump_url)
            view = MsgSuggestionView(interaction.user.id, msg_content, message.id)
            
            suggestion_message = await target_channel.send(
                content=f"<@&{config['SUGGESTION_PING_ROLE_ID']}> A new message suggestion has been submitted!",
                embed=embed,
                view=view
            )
            
            await suggestion_message.add_reaction('✅')
            await suggestion_message.add_reaction('❌')
            
            await interaction.response.send_message(
                "✅ Message suggestion submitted successfully! The moderators will review it shortly.",
                ephemeral=True
            )
            
        except Exception as e:
            print(f"Error sending message suggestion: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while submitting your suggestion. Please try again later.",
                ephemeral=True
            )
    
    @bot.tree.command(name="suggest-msg", description="Suggest a message for the bot to use")
    @app_commands.describe(message="The message content to suggest")
    async def suggest_msg_slash(self, interaction: discord.Interaction, message: str):
        """Slash command to suggest a message for the bot to use"""
        
        if not config['ENABLE_SUGGESTIONS']:
            await interaction.response.send_message(
                "❌ Message suggestions are currently disabled.",
                ephemeral=True
            )
            return
        
        target_channel = self.bot.get_channel(config['SUGGESTION_CHANNEL_ID'])
        if not target_channel:
            await interaction.response.send_message(
                "❌ Could not find the target channel. Please contact an administrator.",
                ephemeral=True
            )
            return
        
        try:
            embed = create_suggestion_embed(interaction, message)
            view = MsgSuggestionView(interaction.user.id, message, interaction.id)
            
            suggestion_message = await target_channel.send(
                content=f"<@&{config['SUGGESTION_PING_ROLE_ID']}> A new message suggestion has been submitted!",
                embed=embed,
                view=view
            )
            
            await suggestion_message.add_reaction('✅')
            await suggestion_message.add_reaction('❌')
            
            await interaction.response.send_message(
                "✅ Message suggestion submitted successfully! The moderators will review it shortly.",
                ephemeral=True
            )
            
        except Exception as e:
            print(f"Error sending message suggestion: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while submitting your suggestion. Please try again later.",
                ephemeral=True
            )
    
    @bot.tree.context_menu(name="Rape member")
    async def rape_user(self, interaction: discord.Interaction, member: discord.Member):
        """Context menu command to rape a user"""
        
        if not config['ENABLE_RAPE_COMMAND']:
            await interaction.response.send_message("❌ Rape command is currently disabled.", ephemeral=True)
            return
        
        target_channel = self.bot.get_channel(config['RAPE_CHANNEL_ID'])
        
        if not target_channel:
            await interaction.response.send_message("❌ Could not find the target channel.", ephemeral=True)
            return
        
        try:
            await target_channel.send(f"{interaction.user.mention} raped {member.mention}")
            await interaction.response.send_message(f"✅ Successfully raped {member.display_name}!", ephemeral=True)
        except Exception as e:
            print(f"Error sending rape message: {e}")
            await interaction.response.send_message("❌ An error occurred while sending the rape message.", ephemeral=True)


async def setup(bot):
    """Setup function to load the cog"""
    await bot.add_cog(SuggestionsCog(bot))
