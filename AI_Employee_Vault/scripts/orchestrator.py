"""
Orchestrator - Main process that coordinates AI Employee operations (Silver Tier)

The orchestrator:
1. Monitors Needs_Action folder for new items
2. Triggers plan-creator to generate action plans
3. Updates Dashboard.md with status
4. Manages task completion workflow
5. Integrates with approval-workflow for sensitive actions

Usage:
    python orchestrator.py /path/to/vault
"""

import sys
import subprocess
import shutil
import io
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Fix Windows console encoding for Unicode emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Orchestrator:
    """Main orchestrator for AI Employee operations"""
    
    def __init__(self, vault_path: str):
        """
        Initialize the orchestrator
        
        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path).expanduser().resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.logs_dir = self.vault_path / 'Logs'
        self.handbook = self.vault_path / 'Company_Handbook.md'
        
        # Ensure directories exist
        for dir_path in [self.needs_action, self.plans, self.done, 
                         self.pending_approval, self.approved, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.log_file = self.logs_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        
        # Silver Tier: Track processed items
        self.processed_file = self.vault_path / '.processed_items.json'
        self.processed_ids = self._load_processed_ids()
    
    def _load_processed_ids(self) -> set:
        """Load previously processed item IDs"""
        if self.processed_file.exists():
            try:
                data = json.loads(self.processed_file.read_text())
                return set(data.get('ids', []))
            except:
                return set()
        return set()
    
    def _save_processed_ids(self):
        """Save processed item IDs"""
        try:
            ids = list(self.processed_ids)[-1000:]
            self.processed_file.write_text(json.dumps({'ids': ids, 'updated': datetime.now().isoformat()}))
        except:
            pass
    
    def log(self, message: str, level: str = 'INFO'):
        """Log a message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'{timestamp} - {level} - {message}'
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def get_pending_items(self) -> list:
        """Get list of pending items in Needs_Action"""
        if not self.needs_action.exists():
            return []
        
        items = []
        for f in self.needs_action.iterdir():
            if f.is_file() and f.suffix == '.md' and not f.name.startswith('.'):
                # Check if already processed
                if f.stem not in self.processed_ids:
                    items.append(f)
        
        return items
    
    def get_pending_approvals(self) -> list:
        """Get list of pending approval requests"""
        if not self.pending_approval.exists():
            return []
        
        return [f for f in self.pending_approval.iterdir() 
                if f.is_file() and f.suffix == '.md' and not f.name.startswith('.')]
    
    def get_approved_actions(self) -> list:
        """Get list of approved actions ready for execution"""
        if not self.approved.exists():
            return []
        
        return [f for f in self.approved.iterdir() 
                if f.is_file() and f.suffix == '.md' and not f.name.startswith('.')]
    
    def update_dashboard(self, pending_count: int, approved_count: int = 0, completed_today: int = 0):
        """Update the Dashboard.md with current status"""
        if not self.dashboard.exists():
            self.log('Dashboard.md not found, skipping update', 'WARNING')
            return
        
        try:
            content = self.dashboard.read_text(encoding='utf-8')
            
            # Update timestamp
            content = content.replace(
                'last_updated:', 
                f'last_updated: {datetime.now().isoformat()}'
            )
            
            # Update counts
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '| Pending Tasks |' in line:
                    lines[i] = f'| Pending Tasks | {pending_count} |'
                if '| Completed Today |' in line:
                    lines[i] = f'| Completed Today | {completed_today} |'
                if '| Awaiting Approval |' in line:
                    lines[i] = f'| Awaiting Approval | {approved_count} |'
            
            self.dashboard.write_text('\n'.join(lines), encoding='utf-8')
            self.log(f'Dashboard updated: {pending_count} pending, {approved_count} awaiting approval')
            
        except Exception as e:
            self.log(f'Error updating dashboard: {e}', 'ERROR')
    
    def create_plan(self, item_path: Path) -> Optional[Path]:
        """
        Create a plan for the item using plan-creator logic
        
        Args:
            item_path: Path to the item file
            
        Returns:
            Path: Path to created plan file
        """
        try:
            # Read item content
            content = item_path.read_text(encoding='utf-8')
            
            # Parse metadata
            metadata = self._parse_metadata(content)
            item_type = metadata.get('type', 'unknown')
            
            # Generate plan based on type
            plan_content = self._generate_plan(item_path, content, metadata, item_type)
            
            # Create plan file
            plan_name = f'PLAN_{item_path.stem}_{datetime.now().strftime("%Y%m%d%H%M%S")}.md'
            plan_path = self.plans / plan_name
            
            plan_path.write_text(plan_content, encoding='utf-8')
            self.log(f'Created plan: {plan_name}')
            
            return plan_path
            
        except Exception as e:
            self.log(f'Error creating plan: {e}', 'ERROR')
            return None
    
    def _parse_metadata(self, content: str) -> dict:
        """Parse YAML frontmatter from content"""
        metadata = {}
        in_frontmatter = False
        
        for line in content.split('\n'):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    break
            elif in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        return metadata
    
    def _generate_plan(self, item_path: Path, content: str, metadata: dict, item_type: str) -> str:
        """Generate plan content based on item type"""
        subject = metadata.get('subject', item_path.name)
        priority = metadata.get('priority', 'normal')
        source = metadata.get('from', metadata.get('source', 'unknown'))
        
        # Determine if approval needed
        requires_approval = self._check_requires_approval(item_type, content, metadata)
        
        return f'''---
created: {datetime.now().isoformat()}
source: {item_path.name}
status: in_progress
priority: {priority}
requires_approval: {str(requires_approval).lower()}
item_type: {item_type}
---

# Plan: Process {item_type.replace("_", " ").title()} - {subject[:50]}

## Objective
Process the item and complete required actions.

## Context
- **Type:** {item_type}
- **Source:** {source}
- **Priority:** {priority}
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Steps
- [ ] Review item content
- [ ] Check Company_Handbook.md for relevant rules
- [ ] Determine required actions
{('- [ ] Create approval request (required)' if requires_approval else '')}
- [ ] Execute actions (or request approval)
- [ ] Log all actions taken
- [ ] Update Dashboard
- [ ] Move to /Done when complete

## Approval Required
{"**Yes** - See /Pending_Approval/ for approval request" if requires_approval else "No"}

## Resources
- Company_Handbook.md: Rules of engagement
- Business_Goals.md: Objectives and metrics

## Actions Taken
_Add actions as you complete them_

## Notes
_Add any relevant notes_

---
*Generated by Orchestrator v2.0 (Silver Tier)*
'''
    
    def _check_requires_approval(self, item_type: str, content: str, metadata: dict) -> bool:
        """Check if action requires approval based on Company Handbook"""
        # Email from new sender
        if item_type == 'email':
            from_email = metadata.get('from', '').lower()
            # Check for known domains (add your known clients)
            known_domains = ['@client.com', '@company.com', '@gmail.com']
            if not any(d in from_email for d in known_domains):
                return True
        
        # Payment/invoice related
        if 'invoice' in content.lower() or 'payment' in content.lower():
            return True
        
        # LinkedIn messages
        if 'linkedin' in item_type:
            return True
        
        return False
    
    def process_item(self, item_path: Path) -> bool:
        """
        Process a single item - create plan and prepare for Qwen Code
        
        Args:
            item_path: Path to the item file
            
        Returns:
            bool: True if processing succeeded
        """
        self.log(f'Processing item: {item_path.name}')
        
        try:
            # Create plan
            plan_path = self.create_plan(item_path)
            
            if plan_path:
                self.log(f'Plan created: {plan_path.name}')
                
                # Mark as processed
                self.processed_ids.add(item_path.stem)
                self._save_processed_ids()
                
                # Ready for Qwen Code
                self.log(f'Item ready for Qwen Code: {item_path.name}')
                
                return True
            else:
                return False
                
        except Exception as e:
            self.log(f'Error processing item: {e}', 'ERROR')
            return False
    
    def execute_approved_actions(self):
        """Execute approved actions from /Approved folder"""
        approved = self.get_approved_actions()
        
        for item in approved:
            try:
                self.log(f'Executing approved action: {item.name}')
                
                # Move to Done
                dest = self.done / item.name
                shutil.move(str(item), str(dest))
                self.log(f'Moved to Done: {item.name}')
                
            except Exception as e:
                self.log(f'Error executing approved action: {e}', 'ERROR')
    
    def complete_item(self, item_path: Path, plan_path: Optional[Path] = None):
        """
        Mark an item as complete by moving to Done folder
        
        Args:
            item_path: Path to the item file
            plan_path: Optional path to associated plan file
        """
        try:
            # Move item to Done
            dest = self.done / item_path.name
            shutil.move(str(item_path), str(dest))
            self.log(f'Moved to Done: {item_path.name}')
            
            # Move plan file if exists
            if plan_path and plan_path.exists():
                plan_dest = self.done / plan_path.name
                shutil.move(str(plan_path), str(plan_dest))
                self.log(f'Moved plan to Done: {plan_path.name}')
            
            # Update dashboard
            pending = len(self.get_pending_items())
            approved = len(self.get_pending_approvals())
            self.update_dashboard(pending, approved)
            
        except Exception as e:
            self.log(f'Error completing item: {e}', 'ERROR')
    
    def run_once(self) -> dict:
        """
        Process all pending items once
        
        Returns:
            dict: Summary of processing
        """
        items = self.get_pending_items()
        approvals = self.get_pending_approvals()
        
        if not items and not approvals:
            self.log('No pending items or approvals')
            return {'processed': 0, 'approvals': 0}
        
        self.log(f'Found {len(items)} pending item(s), {len(approvals)} awaiting approval')
        
        processed = 0
        for item in items:
            if self.process_item(item):
                processed += 1
        
        # Execute any approved actions
        if approvals:
            self.execute_approved_actions()
        
        self.update_dashboard(len(items) - processed, len(approvals))
        
        return {'processed': processed, 'approvals': len(approvals)}
    
    def run_continuous(self, check_interval: int = 30):
        """
        Run orchestrator continuously
        
        Args:
            check_interval: Seconds between checks
        """
        import time
        
        self.log(f'Starting Orchestrator (check interval: {check_interval}s)')
        
        while True:
            try:
                self.run_once()
            except Exception as e:
                self.log(f'Error in orchestrator loop: {e}', 'ERROR')
            
            time.sleep(check_interval)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print('Usage: python orchestrator.py <vault_path>')
        print('Example: python orchestrator.py "C:/AI_Employee_Vault"')
        sys.exit(1)
    
    vault_path = Path(sys.argv[1]).expanduser().resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    orchestrator = Orchestrator(str(vault_path))
    
    print(f'🤖 AI Employee Orchestrator v2.0 (Silver Tier)')
    print(f'   Vault: {vault_path}')
    print(f'   Press Ctrl+C to stop')
    print()
    
    # Run once for Silver tier
    print('Running initial check...')
    result = orchestrator.run_once()
    print(f'Processed {result["processed"]} item(s)')
    print()
    print('💡 Silver Tier Features:')
    print('   - Gmail Watcher: python gmail_watcher.py "vault"')
    print('   - LinkedIn Watcher: python linkedin_watcher.py "vault"')
    print('   - Plan Creator: Automatic plan generation')
    print('   - Approval Workflow: Human-in-the-loop for sensitive actions')
    print()
    print('   To process new items, run: python orchestrator.py "{vault_path}"')


if __name__ == '__main__':
    main()
