"""
Message management module for loading, saving, and managing message lists
"""
import os
from config import config


class MessageManager:
    """Centralized manager for all message lists (text and audio)"""
    
    def __init__(self):
        self.default = []
        self.mention = []
        self.default_audio = []
        self.mention_audio = []
        self._load_all()
    
    def _load_file(self, filename):
        """Load messages from file with automatic creation if missing"""
        try:
            if not os.path.exists(filename):
                print(f"ℹ️  Creating new file: {filename}")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('')
            
            with open(filename, 'r', encoding='utf-8') as f:
                msgs = [line.strip() for line in f if line.strip()]
                return msgs
        except IOError as e:
            print(f"❌ Error reading {filename}: {e}")
            return []
    
    def _save_file(self, filename, msgs):
        """Save messages to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for msg in msgs:
                    f.write(f"{msg}\n")
            print(f"✅ Saved {len(msgs)} messages to {filename}")
        except IOError as e:
            print(f"❌ Error writing to {filename}: {e}")
    
    def _load_all(self):
        """Load all message lists from files"""
        self.default = self._load_file(config['DEFAULT_MSGS_FILE'])
        self.mention = self._load_file(config['MENTION_MSGS_FILE'])
        self.default_audio = self._load_file(config['DEFAULT_AUDIO_MSGS_FILE'])
        self.mention_audio = self._load_file(config['MENTION_AUDIO_MSGS_FILE'])
        print(f"✅ Loaded messages: Default={len(self.default)}, Mention={len(self.mention)}, Audio={len(self.default_audio) + len(self.mention_audio)}")
    
    def reload(self):
        """Reload all message lists from files"""
        self._load_all()
    
    def add_to_list(self, msg, list_type):
        """Add message to specified list (default/mention/default_audio/mention_audio)"""
        list_map = {
            'default': self.default,
            'mention': self.mention,
            'default_audio': self.default_audio,
            'mention_audio': self.mention_audio
        }
        
        msgs = list_map.get(list_type, [])
        if msg in msgs:
            return False
        msgs.append(msg)
        self._save_file(self._get_filename(list_type), msgs)
        return True
    
    def _get_filename(self, list_type):
        """Get filename for list type"""
        map_config = {
            'default': 'DEFAULT_MSGS_FILE',
            'mention': 'MENTION_MSGS_FILE',
            'default_audio': 'DEFAULT_AUDIO_MSGS_FILE',
            'mention_audio': 'MENTION_AUDIO_MSGS_FILE'
        }
        return config[map_config[list_type]]
    
    def get_counts(self):
        """Get message counts for all lists"""
        return {
            'default': len(self.default),
            'mention': len(self.mention),
            'default_audio': len(self.default_audio),
            'mention_audio': len(self.mention_audio)
        }


# Legacy function wrappers for backward compatibility
def load_msgs_from_file(filename):
    """Load messages from file with automatic creation if missing"""
    try:
        if not os.path.exists(filename):
            print(f"ℹ️  Creating new file: {filename}")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('')
        
        with open(filename, 'r', encoding='utf-8') as f:
            msgs = [line.strip() for line in f if line.strip()]
            return msgs
    except IOError as e:
        print(f"❌ Error reading {filename}: {e}")
        return []


def load_audio_msgs_from_file(filename):
    """Load audio messages from file with automatic creation if missing"""
    try:
        if not os.path.exists(filename):
            print(f"ℹ️  Creating new file: {filename}")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('')
        
        with open(filename, 'r', encoding='utf-8') as f:
            audio_msgs = [line.strip() for line in f if line.strip()]
            return audio_msgs
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


def save_audio_msgs_to_file(filename, msgs):
    """Save audio messages to file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for msg in msgs:
                f.write(f"{msg}\n")
        print(f"✅ Saved {len(msgs)} audio messages to {filename}")
    except IOError as e:
        print(f"❌ Error writing to {filename}: {e}")


def initialize_msg_files(default_msgs, mention_msgs, default_audio_msgs=None, mention_audio_msgs=None):
    """Initialize message files with default content if they're empty - Legacy function"""
    pass
