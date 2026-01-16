import discord
import random
import asyncio
import os
from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands

# Function to load configuration from config.txt
def load_config():
    config = {}
    config_file = 'config.txt'
    
    if not os.path.exists(config_file):
        print(f"❌ Config file '{config_file}' not found! Creating template...")
        create_config_template(config_file)
        print(f"✅ Template config file created. Please fill in your values and restart the bot.")
        exit(1)
    
    with open(config_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse key=value pairs
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Convert AUTHORIZED_USER_ID to integer
                if key == 'AUTHORIZED_USER_ID':
                    try:
                        config[key] = int(value)
                    except ValueError:
                        print(f"⚠️ Warning: AUTHORIZED_USER_ID must be a number. Using default.")
                        config[key] = 0
                else:
                    config[key] = value
    
    # Validate required fields
    required_fields = ['TOKEN', 'DEFAULT_MSGS_FILE', 'MENTION_MSGS_FILE', 
                      'CHICKENED_OUT_MSG', 'AUTHORIZED_USER_ID']
    
    missing_fields = [field for field in required_fields if field not in config]
    
    if missing_fields:
        print(f"❌ Missing required configuration fields: {', '.join(missing_fields)}")
        print(f"Please check your {config_file} file.")
        exit(1)
    
    return config

def create_config_template(filename):
    """Create a template config file with example values"""
    template = """# Discord Bot Configuration File
# Fill in the values below with your actual configuration

# Discord Bot Token (REQUIRED)
TOKEN=YOUR_BOT_TOKEN_HERE

# File path for default messages
DEFAULT_MSGS_FILE=default_msgs.txt

# File path for mention messages
MENTION_MSGS_FILE=mention_msgs.txt

# Message/URL to send when someone chickens out
CHICKENED_OUT_MSG=https://tenor.com/view/walk-away-gif-8390063  

# Authorized user ID for approving/declining suggestions (numeric ID)
AUTHORIZED_USER_ID=1209428799289032704
"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template)

# Load configuration
config = load_config()

TOKEN = config['TOKEN']
DEFAULT_MSGS_FILE = config['DEFAULT_MSGS_FILE']
MENTION_MSGS_FILE = config['MENTION_MSGS_FILE']
CHICKENED_OUT_MSG = config['CHICKENED_OUT_MSG']
AUTHORIZED_USER_ID = config['AUTHORIZED_USER_ID']

print(f"✅ Configuration loaded successfully!")
print(f"📁 Default messages file: {DEFAULT_MSGS_FILE}")
print(f"📁 Mention messages file: {MENTION_MSGS_FILE}")
print(f"👤 Authorized user ID: {AUTHORIZED_USER_ID}")

# Function to load messages from file with automatic creation if missing
def load_msgs_from_file(filename):
    if not os.path.exists(filename):
        print(f"Creating new file: {filename}")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('')
    
    with open(filename, 'r', encoding='utf-8') as f:
        msgs = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(msgs)} messages from {filename}")
        return msgs

# Function to save messages to file
def save_msgs_to_file(filename, msgs):
    with open(filename, 'w', encoding='utf-8') as f:
        for msg in msgs:
            f.write(f"{msg}\n")
    print(f"Saved {len(msgs)} messages to {filename}")

# Initialize message lists
default_msgs = load_msgs_from_file(DEFAULT_MSGS_FILE)
mention_msgs = load_msgs_from_file(MENTION_MSGS_FILE)

# Recent joins tracking for chicken out detection
recent_joins = {}

# Discord intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

class MsgSuggestionView(View):
    def __init__(self, author_id, msg_content, message_id):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.msg_content = msg_content
        self.message_id = message_id
        
    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red, emoji="🗑️")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user is authorized
        if interaction.user.id != AUTHORIZED_USER_ID:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return
            
        # Edit the original message to show rejection
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n❌ **Rejected by {interaction.user.mention}**",
            embed=None,
            view=None
        )
        await interaction.response.defer()
    
    @discord.ui.button(label="✅ Default", style=discord.ButtonStyle.green, emoji="📌")
    async def accept_default_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user is authorized
        if interaction.user.id != AUTHORIZED_USER_ID:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return
            
        global default_msgs
        
        # Reload messages to ensure we have the latest version
        default_msgs = load_msgs_from_file(DEFAULT_MSGS_FILE)
        
        if self.msg_content in default_msgs:
            await interaction.response.send_message("⚠️ This message is already in the default list!", ephemeral=True)
            return
            
        # Add to default list
        default_msgs.append(self.msg_content)
        save_msgs_to_file(DEFAULT_MSGS_FILE, default_msgs)
        
        # Auto-reload the message lists
        await self.reload_msg_lists()
        
        await interaction.response.send_message(f"✅ Message added to default list!", ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Default by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Mention", style=discord.ButtonStyle.green, emoji="👋")
    async def accept_mention_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user is authorized
        if interaction.user.id != AUTHORIZED_USER_ID:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return
            
        global mention_msgs
        
        # Reload messages to ensure we have the latest version
        mention_msgs = load_msgs_from_file(MENTION_MSGS_FILE)
        
        if self.msg_content in mention_msgs:
            await interaction.response.send_message("⚠️ This message is already in the mention list!", ephemeral=True)
            return
            
        # Add to mention list
        mention_msgs.append(self.msg_content)
        save_msgs_to_file(MENTION_MSGS_FILE, mention_msgs)
        
        # Auto-reload the message lists
        await self.reload_msg_lists()
        
        await interaction.response.send_message(f"✅ Message added to mention list!", ephemeral=True)
        await interaction.message.edit(
            content=f"~~{interaction.message.content}~~\n\n✅ **Accepted for Mention by {interaction.user.mention}**",
            embed=None,
            view=None
        )
    
    @discord.ui.button(label="✅ Both", style=discord.ButtonStyle.blurple, emoji="✨")
    async def accept_both_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user is authorized
        if interaction.user.id != AUTHORIZED_USER_ID:
            await interaction.response.send_message("❌ You are not authorized to use this button.", ephemeral=True)
            return
            
        global default_msgs, mention_msgs
        
        # Reload messages to ensure we have the latest versions
        default_msgs = load_msgs_from_file(DEFAULT_MSGS_FILE)
        mention_msgs = load_msgs_from_file(MENTION_MSGS_FILE)
        
        added_to_default = False
        added_to_mention = False
        
        if self.msg_content not in default_msgs:
            default_msgs.append(self.msg_content)
            added_to_default = True
            
        if self.msg_content not in mention_msgs:
            mention_msgs.append(self.msg_content)
            added_to_mention = True
            
        # Save both files
        save_msgs_to_file(DEFAULT_MSGS_FILE, default_msgs)
        save_msgs_to_file(MENTION_MSGS_FILE, mention_msgs)
        
        # Auto-reload the message lists
        await self.reload_msg_lists()
        
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
    
    async def reload_msg_lists(self):
        """Automatically reload message lists after modifications"""
        global default_msgs, mention_msgs
        default_msgs = load_msgs_from_file(DEFAULT_MSGS_FILE)
        mention_msgs = load_msgs_from_file(MENTION_MSGS_FILE)
        print(f"🔄 Auto-reloaded message lists: Default={len(default_msgs)}, Mention={len(mention_msgs)}")

# Context menu command to suggest a message
@bot.tree.context_menu(name="Suggest message")
async def suggest_message_context(interaction: discord.Interaction, message: discord.Message):
    """Context menu command to suggest a message for the bot"""
    
    # Check if message has content
    if not message.content:
        await interaction.response.send_message(
            "❌ This message has no text content to suggest!",
            ephemeral=True
        )
        return
    
    target_channel_id = 1365676297589624903
    target_role_id = 1365677261801521265
    
    target_channel = bot.get_channel(target_channel_id)
    if not target_channel:
        await interaction.response.send_message(
            "❌ Could not find the target channel. Please contact an administrator.",
            ephemeral=True
        )
        return
    
    msg_content = message.content
    
    try:
        # Create embed for better presentation
        embed = discord.Embed(
            title="New Proposed Message Suggestion",
            description=f"User {interaction.user.mention} suggests this message for the bot:",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="📝 Message Content", value=msg_content, inline=False)
        embed.add_field(name="📤 Original Author", value=f"{message.author.mention}", inline=True)
        embed.add_field(name="🔗 Message Link", value=f"[Jump to Message]({message.jump_url})", inline=True)
        embed.set_footer(text=f"Suggested by {interaction.user.name} | User ID: {interaction.user.id}")
        
        # Create view with buttons
        view = MsgSuggestionView(interaction.user.id, msg_content, message.id)
        
        # Send to target channel
        suggestion_message = await target_channel.send(
            content=f"<@&{target_role_id}> A new message suggestion has been submitted!",
            embed=embed,
            view=view
        )
        
        # Add confirmation reactions
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

# Context menu command for raping
@bot.tree.context_menu(name="Rape member")
async def rape_user(interaction: discord.Interaction, member: discord.Member):
    """Context menu command to rape a user"""
    # Get the target channel
    target_channel_id = 1420163750551617677
    target_channel = bot.get_channel(target_channel_id)
    
    if not target_channel:
        await interaction.response.send_message("❌ Could not find the target channel.", ephemeral=True)
        return
    
    # Send the rape message
    try:
        await target_channel.send(f"{interaction.user.mention} raped {member.mention}")
        await interaction.response.send_message(f"✅ Successfully raped {member.display_name}!", ephemeral=True)
    except Exception as e:
        print(f"Error sending rape message: {e}")
        await interaction.response.send_message("❌ An error occurred while sending the rape message.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online and ready!')
    print(f'📊 Initial message counts: Default={len(default_msgs)}, Mention={len(mention_msgs)}')
    
    # Ensure files exist with current data
    save_msgs_to_file(DEFAULT_MSGS_FILE, default_msgs)
    save_msgs_to_file(MENTION_MSGS_FILE, mention_msgs)
    
    # Sync command tree
    await bot.tree.sync()
    print('🔄 Command tree synced')

# Slash command for manual message suggestion
@bot.tree.command(name="suggest-msg", description="Suggest a message for the bot to use")
@app_commands.describe(message="The message content to suggest")
async def suggest_msg_slash(interaction: discord.Interaction, message: str):
    """Slash command to suggest a message for the bot to use"""
    
    target_channel_id = 1365676297589624903
    target_role_id = 1365677261801521265
    
    msg_content = message
    
    target_channel = bot.get_channel(target_channel_id)
    if not target_channel:
        await interaction.response.send_message(
            "❌ Could not find the target channel. Please contact an administrator.",
            ephemeral=True
        )
        return
    
    try:
        # Create embed for better presentation
        embed = discord.Embed(
            title="New Proposed Message Suggestion",
            description=f"User {interaction.user.mention} suggests this message for the bot:",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="📝 Message Content", value=msg_content, inline=False)
        embed.set_footer(text=f"Suggested by {interaction.user.name} | User ID: {interaction.user.id}")
        
        # Create view with buttons
        view = MsgSuggestionView(interaction.user.id, msg_content, interaction.id)
        
        # Send to target channel
        suggestion_message = await target_channel.send(
            content=f"<@&{target_role_id}> A new message suggestion has been submitted!",
            embed=embed,
            view=view
        )
        
        # Add confirmation reactions
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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Auto-reload message lists every 5 minutes to catch external changes
    if not hasattr(bot, 'last_msg_reload'):
        bot.last_msg_reload = discord.utils.utcnow()
    
    now = discord.utils.utcnow()
    if (now - bot.last_msg_reload).total_seconds() >= 300:  # 5 minutes
        global default_msgs, mention_msgs
        default_msgs = load_msgs_from_file(DEFAULT_MSGS_FILE)
        mention_msgs = load_msgs_from_file(MENTION_MSGS_FILE)
        bot.last_msg_reload = now
        print(f"🔄 Periodic reload: Default={len(default_msgs)}, Mention={len(mention_msgs)}")

    # Special channel handling
    target_channel_id = 1416584800457723965
    if message.channel.id == target_channel_id:
        try:
            await message.add_reaction('<:yes:1416494635660087467>')
            await message.add_reaction('<:no:1416494651195654277>')
            
            thread_name = message.content[:100] if message.content.strip() else "Discussion"
            thread = await message.create_thread(name=thread_name)
            
            ping_message = await thread.send(f"{message.author.mention}")
            await ping_message.delete()
            
        except Exception as e:
            print(f"Error processing message in channel {target_channel_id}: {e}")

    # 1% chance to send random message from default
    if random.randint(1, 100) == 1 and default_msgs:
        msg = random.choice(default_msgs)
        try:
            await message.channel.send(msg)
        except Exception as e:
            print(f"Error sending random message: {e}")

    # If bot is mentioned, send message from mention list
    if bot.user.mentioned_in(message) and mention_msgs:
        msg = random.choice(mention_msgs)
        try:
            await message.channel.send(msg)
        except Exception as e:
            print(f"Error sending mention message: {e}")

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    recent_joins[member.id] = {
        "time": discord.utils.utcnow(),
        "channel": member.guild.system_channel
    }
    print(f"👋 {member.name} joined the server")

@bot.event
async def on_member_remove(member):
    if member.id in recent_joins:
        join_time = recent_joins[member.id]["time"]
        leave_time = discord.utils.utcnow()
        if (leave_time - join_time).total_seconds() <= 900:  # 15 minutes
            channel_id = 1365834457864732732
            channel = bot.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(f"{member.mention} chickened out")
                    await channel.send(CHICKENED_OUT_MSG)
                    print(f"🐔 {member.name} chickened out")
                except Exception as e:
                    print(f"Error sending chicken out message: {e}")

        del recent_joins[member.id]

# Admin command to manually reload messages
@bot.command(name='reload-msgs')
@commands.has_permissions(administrator=True)
async def reload_msgs(ctx):
    """Manually reload message lists from files"""
    global default_msgs, mention_msgs
    default_msgs = load_msgs_from_file(DEFAULT_MSGS_FILE)
    mention_msgs = load_msgs_from_file(MENTION_MSGS_FILE)
    await ctx.send(f"✅ Message lists manually reloaded!\n📊 Default messages: {len(default_msgs)}\n📊 Mention messages: {len(mention_msgs)}")
    print(f"🔄 Manual reload by {ctx.author.name}: Default={len(default_msgs)}, Mention={len(mention_msgs)}")

# Command to show current message counts
@bot.command(name='msg-count')
async def msg_count(ctx):
    """Show current message counts"""
    await ctx.send(f"📊 Current message counts:\n🔹 Default messages: {len(default_msgs)}\n🔹 Mention messages: {len(mention_msgs)}")

# Command to list all messages (admin only for security)
@bot.command(name='list-msgs')
@commands.has_permissions(administrator=True)
async def list_msgs(ctx, list_type: str = "default"):
    """List messages from specified list (default/mention)"""
    if list_type.lower() == "default":
        msgs = default_msgs
        title = "Default messages"
    elif list_type.lower() == "mention":
        msgs = mention_msgs
        title = "Mention messages"
    else:
        await ctx.send("❌ Invalid list type. Use 'default' or 'mention'.")
        return
    
    if not msgs:
        await ctx.send(f"📭 No messages found in {title} list.")
        return
    
    # Create embed with pagination if needed
    chunk_size = 10
    chunks = [msgs[i:i + chunk_size] for i in range(0, len(msgs), chunk_size)]
    
    for i, chunk in enumerate(chunks):
        embed = discord.Embed(
            title=f"{title} (Page {i+1}/{len(chunks)})",
            color=discord.Color.green()
        )
        
        for j, msg in enumerate(chunk, 1):
            embed.add_field(
                name=f"{j + i*chunk_size}. Message",
                value=msg,
                inline=False
            )
        
        await ctx.send(embed=embed)

# Error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument! Please check the command syntax.")
    elif isinstance(error, commands.CommandNotFound):
        # Don't respond to unknown commands to avoid spam
        return
    else:
        print(f"Command error: {error}")
        await ctx.send("❌ An error occurred while executing the command.")

# Initialize files with default content if empty
def initialize_msg_files():
    """Initialize message files with default content if they're empty"""
    default_count = len(default_msgs)
    mention_count = len(mention_msgs)
    
    if default_count == 0:
        print("⚠️ Default messages file is empty, initializing with default messages...")
        default_template = [
            "https://tenor.com/view/jetstream-sam-my-beloved-gif-22029076  ",
            "https://tenor.com/view/team-fortress-есчипсы-gif-23573659",
            "https://tenor.com/view/komaru-cat-tiny-bunny-horror-japanese-gif-11150797129126961638  ",
            "https://media.discordapp.net/attachments/1015901608242065419/1021653518945366046/screw.gif?ex=68c651fc&is=68c5007c&hm=b4b1e407f4c2ed3f4fa712c9bf15c731ba566b263ec76d468e78438881c7df85&  ",
            "https://tenor.com/view/dance-dancing-gif-26353220  ",
            "https://tenor.com/view/frog-frog-laughing-gif-25708743  ",
            "https://tenor.com/view/dfg-gif-26011452  ",
            "https://media.discordapp.net/attachments/990895647949459456/1042076478348722186/doc_2022-11-07_22-02-32_1.gif?ex=68c6ca59&is=68c578d9&hm=527f0889fa6249bc5909ab96c781e534f1de57a58b0eb04679e09a8afd118e44&  ",
            "damn",
            ":wowzer:",
            "cool!",
            "nice one",
            "lmao"
        ]
        save_msgs_to_file(DEFAULT_MSGS_FILE, default_template)
        print(f"✅ Initialized default messages file with {len(default_template)} messages")
    
    if mention_count == 0:
        print("⚠️ Mention messages file is empty, initializing with default messages...")
        mention_template = [
            "https://tenor.com/view/komaru-cat-tiny-bunny-horror-japanese-gif-11150797129126961638  ",
            "https://media.discordapp.net/attachments/990895647949459456/1042076478348722186/doc_2022-11-07_22-02-32_1.gif?ex=68c6ca59&is=68c578d9&hm=527f0889fa6249bc5909ab96c781e534f1de57a58b0eb04679e09a8afd118e44&  ",
            "https://tenor.com/view/rock-one-eyebrow-raised-rock-staring-the-rock-gif-22113367  ",
            "https://tenor.com/view/кот-смешной-кот-кот-ест-корм-кота-снимает-камера-cat-gif-10642232306186810479",
            "https://tenor.com/view/cat-silly-boom-explosion-flabbergaster-gif-17414861278238654650  ",
            "what's up?",
            "hey there!",
            "hi"
        ]
        save_msgs_to_file(MENTION_MSGS_FILE, mention_template)
        print(f"✅ Initialized mention messages file with {len(mention_template)} messages")

# Run initialization
initialize_msg_files()

# Start the bot
print("🚀 Starting bot...")
bot.run(TOKEN)