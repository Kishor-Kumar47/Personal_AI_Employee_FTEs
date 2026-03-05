"""
Plan Creator - Generate structured action plans from tasks

Analyzes items in Needs_Action and creates detailed Plan.md files.

Usage:
    python plan_creator.py "C:/Vault"
    python plan_creator.py create --vault "C:/Vault" --item "EMAIL_12345.md"
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


class PlanCreator:
    """Create structured action plans"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).expanduser().resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans_dir = self.vault_path / 'Plans'
        self.handbook = self.vault_path / 'Company_Handbook.md'
        self.logs_dir = self.vault_path / 'Logs' / 'plans'
        
        for dir_path in [self.plans_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Load approval thresholds from handbook
        self.thresholds = self._load_thresholds()
    
    def _load_thresholds(self) -> dict:
        """Load approval thresholds from Company Handbook"""
        thresholds = {
            'email_new_recipient': True,
            'payment_amount': 100,
            'payment_new_payee': True,
            'file_delete': True
        }
        
        if self.handbook.exists():
            content = self.handbook.read_text(encoding='utf-8')
            # Parse thresholds from handbook (simplified)
            if '$500' in content:
                thresholds['payment_amount'] = 500
            if '$100' in content:
                thresholds['payment_amount'] = 100
        
        return thresholds
    
    def create_plan(self, item_path: str) -> dict:
        """
        Create a plan from an item
        
        Args:
            item_path: Path to item in Needs_Action
            
        Returns:
            dict: Plan details
        """
        item_file = Path(item_path)
        if not item_file.exists():
            return {'error': f'Item not found: {item_path}'}
        
        # Read item content
        content = item_file.read_text(encoding='utf-8')
        
        # Parse item metadata
        metadata = self._parse_metadata(content)
        item_type = metadata.get('type', 'unknown')
        
        # Generate plan based on type
        if item_type == 'email' or 'EMAIL' in item_file.name:
            plan_content = self._create_email_plan(item_file, content, metadata)
        elif item_type == 'file_drop' or 'FILE' in item_file.name:
            plan_content = self._create_file_plan(item_file, content, metadata)
        else:
            plan_content = self._create_generic_plan(item_file, content, metadata)
        
        # Create plan file
        plan_name = f'PLAN_{item_file.stem}_{datetime.now().strftime("%Y%m%d%H%M%S")}.md'
        plan_path = self.plans_dir / plan_name
        plan_path.write_text(plan_content, encoding='utf-8')
        
        # Log
        self._log_plan(plan_name, item_file.name, plan_content)
        
        return {
            'id': plan_name,
            'path': str(plan_path),
            'source': item_file.name,
            'type': item_type
        }
    
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
    
    def _create_email_plan(self, item_file: Path, content: str, metadata: dict) -> str:
        """Create plan for email item"""
        subject = metadata.get('subject', 'Unknown')
        from_email = metadata.get('from', 'Unknown')
        priority = metadata.get('priority', 'normal')
        
        # Determine if approval needed
        requires_approval = self._check_email_approval(from_email, content)
        
        return f'''---
created: {datetime.now().isoformat()}
source: {item_file.name}
status: in_progress
priority: {priority}
requires_approval: {str(requires_approval).lower()}
---

# Plan: Process Email - {subject}

## Objective
Process incoming email and take appropriate action.

## Context
- **From:** {from_email}
- **Subject:** {subject}
- **Priority:** {priority}
- **Received:** {metadata.get('received', 'Unknown')}

## Steps
- [ ] Read and understand email content
- [ ] Check Company_Handbook.md for response rules
- [ ] Determine required action
- [ ] Draft response or take action
{('- [ ] Create approval request (required for this action)' if requires_approval else '')}
- [ ] Execute action
- [ ] Log action taken
- [ ] Move to Done when complete

## Approval Required
{"Yes - see /Pending_Approval/" if requires_approval else "No"}

## Resources
- Company_Handbook.md: Communication rules
- Business_Goals.md: Client information

## Notes
_Add notes during execution_
'''
    
    def _create_file_plan(self, item_file: Path, content: str, metadata: dict) -> str:
        """Create plan for file drop item"""
        original_name = metadata.get('original_name', 'Unknown')
        file_size = metadata.get('file_size', 'Unknown')
        
        return f'''---
created: {datetime.now().isoformat()}
source: {item_file.name}
status: in_progress
priority: normal
requires_approval: false
---

# Plan: Process File - {original_name}

## Objective
Process dropped file and take appropriate action.

## Context
- **Original File:** {original_name}
- **Size:** {file_size}
- **Detected:** {metadata.get('detected', 'Unknown')}

## Steps
- [ ] Review file content
- [ ] Understand what processing is needed
- [ ] Check Company_Handbook.md for file handling rules
- [ ] Process file as required
- [ ] Store or forward as needed
- [ ] Log action taken
- [ ] Move to Done when complete

## Approval Required
No

## Resources
- Company_Handbook.md: File operation rules

## Notes
_Add notes during execution_
'''
    
    def _create_generic_plan(self, item_file: Path, content: str, metadata: dict) -> str:
        """Create generic plan for unknown item type"""
        return f'''---
created: {datetime.now().isoformat()}
source: {item_file.name}
status: in_progress
priority: normal
requires_approval: false
---

# Plan: Process Item - {item_file.name}

## Objective
Analyze and process this item.

## Context
- **Source:** {item_file.name}
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Steps
- [ ] Read and understand item content
- [ ] Identify required actions
- [ ] Check Company_Handbook.md for relevant rules
- [ ] Execute required actions
- [ ] Log actions taken
- [ ] Move to Done when complete

## Approval Required
To be determined during processing

## Resources
- Company_Handbook.md: Rules of engagement

## Notes
_Add notes during execution_
'''
    
    def _check_email_approval(self, from_email: str, content: str) -> bool:
        """Check if email action requires approval"""
        # Check for known contact patterns
        known_domains = ['@client.com', '@company.com']  # Example
        
        for domain in known_domains:
            if domain in from_email.lower():
                return False
        
        # Check for payment/invoice keywords with amounts
        if 'invoice' in content.lower() or 'payment' in content.lower():
            return True
        
        # New contact requires approval
        return True
    
    def _log_plan(self, plan_name: str, source: str, content: str):
        """Log plan creation"""
        log_file = self.logs_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'plan': plan_name,
            'source': source,
            'status': 'created'
        }
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def list_plans(self) -> list:
        """List all plans"""
        plans = []
        for f in self.plans_dir.iterdir():
            if f.suffix == '.md' and not f.name.startswith('.'):
                content = f.read_text(encoding='utf-8')
                metadata = self._parse_metadata(content)
                plans.append({
                    'file': f.name,
                    'path': str(f),
                    'status': metadata.get('status', 'unknown'),
                    'source': metadata.get('source', 'unknown')
                })
        return plans
    
    def update_status(self, plan_name: str, status: str) -> bool:
        """Update plan status"""
        plan_path = self.plans_dir / plan_name
        if not plan_path.exists():
            return False
        
        content = plan_path.read_text(encoding='utf-8')
        
        # Update status in frontmatter
        import re
        content = re.sub(
            r'status: \w+',
            f'status: {status}',
            content
        )
        
        plan_path.write_text(content, encoding='utf-8')
        return True


def main():
    parser = argparse.ArgumentParser(description='Plan Creator')
    parser.add_argument('vault', nargs='?', default='.', help='Path to Obsidian vault')
    parser.add_argument('command', nargs='?', default='process', 
                        choices=['process', 'list', 'create', 'status'],
                        help='Command to run')
    parser.add_argument('--item', help='Item file to create plan for')
    parser.add_argument('--plan', help='Plan file for status command')
    parser.add_argument('--status', help='New status for plan')
    
    args = parser.parse_args()
    
    creator = PlanCreator(args.vault)
    
    if args.command == 'process':
        # Process all items in Needs_Action
        items = list(creator.needs_action.glob('*.md'))
        if items:
            print(f'Processing {len(items)} item(s)...')
            for item in items:
                result = creator.create_plan(str(item))
                print(f"  Created: {result.get('id', 'error')}")
        else:
            print('No items to process')
            
    elif args.command == 'create':
        if not args.item:
            print('Error: --item required')
            sys.exit(1)
        result = creator.create_plan(args.item)
        print(f"Created plan: {result.get('id')}")
        
    elif args.command == 'list':
        plans = creator.list_plans()
        if plans:
            print(f'Plans ({len(plans)}):')
            for plan in plans:
                print(f"  [{plan['status']}] {plan['file']}")
        else:
            print('No plans found')
            
    elif args.command == 'status':
        if not args.plan or not args.status:
            print('Error: --plan and --status required')
            sys.exit(1)
        if creator.update_status(args.plan, args.status):
            print(f'Updated {args.plan} to {args.status}')
        else:
            print(f'Plan not found: {args.plan}')


if __name__ == '__main__':
    main()
