"""
File System Watcher - Monitors a drop folder for new files

This watcher monitors a specified folder and creates action files
when new files are detected. Perfect for Bronze tier implementation.

Usage:
    python filesystem_watcher.py /path/to/vault /path/to/watch
"""

import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from base_watcher import BaseWatcher


class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events in the drop folder"""
    
    def __init__(self, watcher):
        self.watcher = watcher
    
    def on_created(self, event):
        """Called when a file or directory is created"""
        if event.is_directory:
            return
        
        try:
            source_path = Path(event.src_path)
            
            # Skip hidden files and temporary files
            if source_path.name.startswith('.') or source_path.suffix == '.tmp':
                return
            
            self.watcher.process_new_file(source_path)
        except Exception as e:
            self.watcher.logger.error(f'Error processing file {event.src_path}: {e}')


class FileSystemWatcher(BaseWatcher):
    """Watches a folder for new files and creates action files"""
    
    def __init__(self, vault_path: str, watch_folder: str, check_interval: int = 5):
        """
        Initialize the file system watcher
        
        Args:
            vault_path: Path to the Obsidian vault
            watch_folder: Path to the folder to monitor
            check_interval: Check interval (default: 5s for responsive file watching)
        """
        super().__init__(vault_path, check_interval)
        self.watch_folder = Path(watch_folder)
        self.watch_folder.mkdir(parents=True, exist_ok=True)
        
        # Track file hashes to detect changes
        self.file_hashes = {}
    
    def get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            self.logger.error(f'Error hashing file {file_path}: {e}')
            return ''
    
    def check_for_updates(self) -> list:
        """
        Check for new files in the watch folder
        
        Returns:
            list: List of new file paths
        """
        new_files = []
        
        if not self.watch_folder.exists():
            return new_files
        
        for file_path in self.watch_folder.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                file_hash = self.get_file_hash(file_path)
                file_key = str(file_path)
                
                # Check if this is a new file or changed file
                if file_key not in self.file_hashes:
                    self.logger.info(f'New file detected: {file_path.name}')
                    new_files.append(file_path)
                    self.file_hashes[file_key] = file_hash
                elif self.file_hashes[file_key] != file_hash:
                    self.logger.info(f'File modified: {file_path.name}')
                    new_files.append(file_path)
                    self.file_hashes[file_key] = file_hash
        
        return new_files
    
    def process_new_file(self, file_path: Path):
        """Process a newly detected file"""
        self.logger.info(f'Processing new file: {file_path.name}')
        self.create_action_file(file_path)
    
    def create_action_file(self, file_path: Path) -> Path:
        """
        Create an action file for the detected file
        
        Args:
            file_path: Path to the detected file
            
        Returns:
            Path: Path to the created action file
        """
        try:
            # Generate unique ID from file hash
            file_hash = self.get_file_hash(file_path)
            file_id = file_hash[:8] if file_hash else datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Create action file content
            content = f'''---
type: file_drop
source: filesystem
original_name: {file_path.name}
file_size: {file_path.stat().st_size} bytes
detected: {datetime.now().isoformat()}
priority: normal
status: pending
---

# File Drop for Processing

## Source File
- **Name:** {file_path.name}
- **Size:** {file_path.stat().st_size} bytes
- **Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## File Content
```
{self._read_file_content(file_path)}
```

## Suggested Actions
- [ ] Review file content
- [ ] Categorize file
- [ ] Take appropriate action
- [ ] Move to /Done when complete

## Notes
_Add your notes here_
'''
            
            # Create action file path
            action_file_name = f'FILE_{file_id}_{file_path.name}.md'
            action_file_path = self.needs_action / action_file_name
            
            # Write action file
            action_file_path.write_text(content, encoding='utf-8')
            
            self.logger.info(f'Created action file: {action_file_path}')
            return action_file_path
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise
    
    def _read_file_content(self, file_path: Path, max_lines: int = 50) -> str:
        """Read file content (limited for large files)"""
        try:
            # Only read text files
            text_extensions = {'.txt', '.md', '.csv', '.json', '.xml', '.log', '.py', '.js'}
            if file_path.suffix.lower() not in text_extensions:
                return '[Binary file - content not displayed]'
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                if len(lines) > max_lines:
                    return ''.join(lines[:max_lines]) + f'\n\n... ({len(lines) - max_lines} more lines)'
                return ''.join(lines)
        except Exception as e:
            return f'[Error reading file: {e}]'
    
    def run(self):
        """Run the watcher using watchdog for real-time monitoring"""
        self.logger.info(f'Starting FileSystemWatcher')
        self.logger.info(f'Watching folder: {self.watch_folder}')
        
        # Use watchdog Observer for real-time monitoring
        event_handler = DropFolderHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.watch_folder), recursive=False)
        observer.start()
        
        self.logger.info('File watcher started (real-time monitoring)')
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        
        observer.join()
        self.logger.info('File watcher stopped')


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print('Usage: python filesystem_watcher.py <vault_path> <watch_folder>')
        print('Example: python filesystem_watcher.py "C:/Vault" "C:/DropFolder"')
        sys.exit(1)
    
    vault_path = Path(sys.argv[1]).expanduser().resolve()
    watch_folder = Path(sys.argv[2]).expanduser().resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    # Create watch folder if it doesn't exist
    watch_folder.mkdir(parents=True, exist_ok=True)
    
    watcher = FileSystemWatcher(str(vault_path), str(watch_folder))
    
    print(f'📁 File System Watcher started')
    print(f'   Vault: {vault_path}')
    print(f'   Watching: {watch_folder}')
    print(f'   Press Ctrl+C to stop')
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        print('\n👋 Stopping watcher...')


if __name__ == '__main__':
    main()
