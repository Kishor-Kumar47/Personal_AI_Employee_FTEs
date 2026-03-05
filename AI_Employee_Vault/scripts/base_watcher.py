"""
Base Watcher Class - Template for all AI Employee watchers

All watchers inherit from this base class and implement:
- check_for_updates(): Return list of new items to process
- create_action_file(): Create .md file in Needs_Action folder
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """Abstract base class for all watcher implementations"""
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        
        # Ensure Needs_Action folder exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Track processed items to avoid duplicates
        self.processed_ids = set()
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process
        
        Returns:
            list: List of new items that need processing
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create an action file in Needs_Action folder
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path: Path to the created file
        """
        pass
    
    def run(self):
        """Main run loop - continuously checks for updates"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    try:
                        self.create_action_file(item)
                    except Exception as e:
                        self.logger.error(f'Error creating action file: {e}')
            except Exception as e:
                self.logger.error(f'Error checking for updates: {e}')
            
            time.sleep(self.check_interval)
    
    def run_once(self) -> int:
        """
        Run a single check (useful for testing or scheduled tasks)
        
        Returns:
            int: Number of items processed
        """
        items = self.check_for_updates()
        for item in items:
            self.create_action_file(item)
        return len(items)
