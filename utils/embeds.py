"""
Utils module for embed creation and formatting
"""
import discord
from config import config


def create_suggestion_embed(interaction, msg_content, message_author=None, message_url=None):
    """Create an embed for message suggestion"""
    embed = discord.Embed(
        title="New Proposed Message Suggestion",
        description=f"User {interaction.user.mention} suggests this message for the bot:",
        color=discord.Color(int(config['SUGGESTION_EMBED_COLOR'], 16)),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="📝 Message Content", value=msg_content, inline=False)
    
    if message_author:
        embed.add_field(name="📤 Original Author", value=f"{message_author.mention}", inline=True)
    
    if message_url:
        embed.add_field(name="🔗 Message Link", value=f"[Jump to Message]({message_url})", inline=True)
    
    embed.set_footer(text=f"Suggested by {interaction.user.name} | User ID: {interaction.user.id}")
    return embed
