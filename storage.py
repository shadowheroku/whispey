import json
import time
from typing import Dict, List, Any, Optional
from config import Config

class JSONStorage:
    def __init__(self, file_path: str = Config.DATA_FILE):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create the JSON file if it doesn't exist"""
        try:
            with open(self.file_path, 'r') as f:
                pass
        except FileNotFoundError:
            with open(self.file_path, 'w') as f:
                json.dump({
                    "users": {},
                    "whispers": {},
                    "next_whisper_id": 1
                }, f, indent=4)
    
    def _read_data(self) -> Dict:
        """Read data from JSON file"""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"users": {}, "whispers": {}, "next_whisper_id": 1}
    
    def _write_data(self, data: Dict):
        """Write data to JSON file"""
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        data = self._read_data()
        return data["users"].get(str(user_id))
    
    def save_user(self, user_id: int, user_data: Dict):
        """Save user data"""
        data = self._read_data()
        data["users"][str(user_id)] = user_data
        self._write_data(data)
    
    def get_whisper(self, whisper_id: int) -> Optional[Dict]:
        """Get whisper by ID"""
        data = self._read_data()
        return data["whispers"].get(str(whisper_id))
    
    def save_whisper(self, whisper_id: int, whisper_data: Dict):
        """Save whisper data"""
        data = self._read_data()
        data["whispers"][str(whisper_id)] = whisper_data
        self._write_data(data)
    
    def delete_whisper(self, whisper_id: int):
        """Delete whisper by ID"""
        data = self._read_data()
        if str(whisper_id) in data["whispers"]:
            del data["whispers"][str(whisper_id)]
            self._write_data(data)
    
    def get_user_whispers(self, user_id: int, as_sender: bool = True) -> List[Dict]:
        """Get all whispers for a user (as sender or recipient)"""
        data = self._read_data()
        whispers = []
        
        for whisper_id, whisper in data["whispers"].items():
            key = "sender_id" if as_sender else "recipient_id"
            if str(whisper.get(key)) == str(user_id):
                whispers.append({"id": whisper_id, **whisper})
        
        return whispers
    
    def get_next_whisper_id(self) -> int:
        """Get the next available whisper ID"""
        data = self._read_data()
        next_id = data.get("next_whisper_id", 1)
        
        # Update for next time
        data["next_whisper_id"] = next_id + 1
        self._write_data(data)
        
        return next_id
    
    def get_all_whispers(self) -> Dict:
        """Get all whispers"""
        data = self._read_data()
        return data["whispers"]
    
    def get_all_users(self) -> Dict:
        """Get all users"""
        data = self._read_data()
        return data["users"]

# Global storage instance
storage = JSONStorage()
