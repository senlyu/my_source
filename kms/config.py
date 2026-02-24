import json
import os
from typing import List, Dict, Any

class KMSConfig:
    def __init__(self, config_path: str = "config.json"):
        # Check standard locations
        paths = [
            config_path,
            "../config.json",
            "/app/config.json"
        ]
        self.data = {}
        for p in paths:
            if os.path.exists(p):
                self.data = self._load_config(p)
                break

    def _load_config(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def get_gemini_keys(self) -> List[Dict[str, str]]:
        # Try to get from environment first (for Docker)
        env_keys = os.getenv("GEMINI_KEYS")
        if env_keys:
            try:
                return json.loads(env_keys)
            except json.JSONDecodeError:
                pass
        
        # Then try config file
        key_manager = self.data.get('key_manager', {})
        return key_manager.get('gemini', [])

    def get_rpm(self) -> int:
        return int(os.getenv("KMS_RPM", 1))

    def get_history_path(self) -> str:
        return os.getenv("KMS_HISTORY_PATH", "./history")

    def get_port(self) -> int:
        # Check environment first
        env_port = os.getenv("KMS_PORT")
        if env_port:
            return int(env_port)
        
        # Then check config .kms.port
        kms_config = self.data.get('kms')
        if isinstance(kms_config, dict):
            return int(kms_config.get('port', 4001))
        
        return 4001
