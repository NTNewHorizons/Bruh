"""
Message management module for loading, saving, and managing message lists
"""
import os
from config import config


def load_msgs_from_file(filename):
    """Load messages from file with automatic creation if missing"""
    try:
        if not os.path.exists(filename):
            print(f"ℹ️  Creating new file: {filename}")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('')
        
        with open(filename, 'r', encoding='utf-8') as f:
            msgs = [line.strip() for line in f if line.strip()]
            print(f"✅ Loaded {len(msgs)} messages from {filename}")
            return msgs
    except IOError as e:
        print(f"❌ Error reading {filename}: {e}")
        return []


def save_msgs_to_file(filename, msgs):
    """Save messages to file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for msg in msgs:
                f.write(f"{msg}\n")
        print(f"✅ Saved {len(msgs)} messages to {filename}")
    except IOError as e:
        print(f"❌ Error writing to {filename}: {e}")


def initialize_msg_files(default_msgs, mention_msgs):
    """Initialize message files with default content if they're empty"""
    default_msgs_file = config['DEFAULT_MSGS_FILE']
    mention_msgs_file = config['MENTION_MSGS_FILE']
    
    if len(default_msgs) == 0:
        print("⚠️  Default messages file is empty, initializing with default messages...")
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
        try:
            save_msgs_to_file(default_msgs_file, default_template)
            print(f"✅ Initialized default messages file with {len(default_template)} messages")
        except Exception as e:
            print(f"❌ Error initializing default messages: {e}")
    
    if len(mention_msgs) == 0:
        print("⚠️  Mention messages file is empty, initializing with default messages...")
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
        try:
            save_msgs_to_file(mention_msgs_file, mention_template)
            print(f"✅ Initialized mention messages file with {len(mention_template)} messages")
        except Exception as e:
            print(f"❌ Error initializing mention messages: {e}")
