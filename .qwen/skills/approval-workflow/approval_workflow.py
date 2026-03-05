"""
Approval Workflow - Human-in-the-loop approval system

Creates approval requests, monitors for approvals, and executes actions.

Usage:
    python approval_workflow.py create --action "send_email" --to "client@example.com" ...
    python approval_workflow.py list
    python approval_workflow.py execute
"""

import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta


class ApprovalWorkflow:
    """Manage human-in-the-loop approvals"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).expanduser().resolve()
        self.pending_dir = self.vault_path / 'Pending_Approval'
        self.approved_dir = self.vault_path / 'Approved'
        self.rejected_dir = self.vault_path / 'Rejected'
        self.done_dir = self.vault_path / 'Done'
        self.logs_dir = self.vault_path / 'Logs' / 'approvals'
        
        for dir_path in [self.pending_dir, self.approved_dir, 
                         self.rejected_dir, self.done_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def create_request(self, action_type: str, details: dict, 
                       priority: str = 'normal', expires_in_hours: int = 24,
                       description: str = '') -> str:
        """
        Create an approval request
        
        Args:
            action_type: Type of action (send_email, payment, post, etc.)
            details: Action-specific details
            priority: low, normal, high, critical
            expires_in_hours: Hours until expiration
            description: Human-readable description
            
        Returns:
            str: Request ID
        """
        request_id = f"APR_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        created = datetime.now()
        expires = created + timedelta(hours=expires_in_hours)
        
        content = f'''---
type: approval_request
request_id: {request_id}
action: {action_type}
created: {created.isoformat()}
expires: {expires.isoformat()}
priority: {priority}
status: pending
---

# Approval Request: {action_type.replace('_', ' ').title()}

{description}

## Action Details
{self._format_details(details)}

## Instructions
- **To Approve**: Move this file to /Approved folder
- **To Reject**: Move this file to /Rejected folder
- **Expires**: {expires.strftime('%Y-%m-%d %H:%M:%S')}

## Notes
_Add any additional context here_
'''
        
        filename = f'{request_id}_{action_type}.md'
        filepath = self.pending_dir / filename
        filepath.write_text(content, encoding='utf-8')
        
        self._log_request(request_id, action_type, 'created', details)
        
        return request_id
    
    def check_pending(self) -> list:
        """Get list of pending approval requests"""
        pending = []
        for f in self.pending_dir.iterdir():
            if f.suffix == '.md' and not f.name.startswith('.'):
                content = f.read_text(encoding='utf-8')
                pending.append({
                    'file': f.name,
                    'path': str(f),
                    'content': content[:500]  # First 500 chars
                })
        return pending
    
    def check_approved(self) -> list:
        """Get list of approved actions ready for execution"""
        approved = []
        for f in self.approved_dir.iterdir():
            if f.suffix == '.md' and not f.name.startswith('.'):
                content = f.read_text(encoding='utf-8')
                approved.append({
                    'file': f.name,
                    'path': str(f),
                    'content': content
                })
        return approved
    
    def execute_approved_actions(self) -> list:
        """Execute all approved actions"""
        results = []
        approved = self.check_approved()
        
        for item in approved:
            try:
                result = self._execute_action(item)
                results.append(result)
                
                # Move to Done
                if result['status'] == 'success':
                    dest = self.done_dir / item['file']
                    shutil.move(item['path'], str(dest))
                    self._log_request(
                        item['file'].split('_')[1],
                        'executed',
                        'success',
                        {'dest': str(dest)}
                    )
                else:
                    results.append(result)
                    
            except Exception as e:
                results.append({
                    'file': item['file'],
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def _execute_action(self, item: dict) -> dict:
        """Execute a single approved action"""
        content = item['content']
        
        # Parse action type from content
        action_type = self._extract_field(content, 'action:')
        
        # Execute based on action type
        if action_type == 'send_email':
            return self._execute_email(item)
        elif action_type == 'payment':
            return self._execute_payment(item)
        elif action_type == 'social_post':
            return self._execute_post(item)
        else:
            return {
                'file': item['file'],
                'status': 'unknown_action',
                'action': action_type
            }
    
    def _execute_email(self, item: dict) -> dict:
        """Execute email send action"""
        content = item['content']
        
        # Extract email details
        to = self._extract_field(content, 'to:')
        subject = self._extract_field(content, 'subject:')
        body = self._extract_field(content, 'body:')
        
        # Log the action (actual sending would integrate with email-sender skill)
        self._log_request(
            item['file'].split('_')[1],
            'send_email',
            'executing',
            {'to': to, 'subject': subject}
        )
        
        return {
            'file': item['file'],
            'status': 'success',
            'action': 'send_email',
            'details': {'to': to, 'subject': subject}
        }
    
    def _execute_payment(self, item: dict) -> dict:
        """Execute payment action"""
        content = item['content']
        
        recipient = self._extract_field(content, 'recipient:')
        amount = self._extract_field(content, 'amount:')
        reason = self._extract_field(content, 'reason:')
        
        self._log_request(
            item['file'].split('_')[1],
            'payment',
            'executing',
            {'recipient': recipient, 'amount': amount}
        )
        
        return {
            'file': item['file'],
            'status': 'success',
            'action': 'payment',
            'details': {'recipient': recipient, 'amount': amount}
        }
    
    def _execute_post(self, item: dict) -> dict:
        """Execute social media post action"""
        content = item['content']
        
        platform = self._extract_field(content, 'platform:')
        post_content = self._extract_field(content, 'content:')
        
        self._log_request(
            item['file'].split('_')[1],
            'social_post',
            'executing',
            {'platform': platform}
        )
        
        return {
            'file': item['file'],
            'status': 'success',
            'action': 'social_post',
            'details': {'platform': platform, 'content': post_content[:100]}
        }
    
    def _extract_field(self, content: str, field: str) -> str:
        """Extract a field value from markdown content"""
        for line in content.split('\n'):
            if line.startswith(field):
                return line.replace(field, '').strip()
        return ''
    
    def _format_details(self, details: dict) -> str:
        """Format details as markdown"""
        lines = []
        for key, value in details.items():
            lines.append(f'- **{key.replace("_", " ").title()}:** {value}')
        return '\n'.join(lines)
    
    def _log_request(self, request_id: str, action_type: str, 
                     status: str, details: dict):
        """Log approval request"""
        log_file = self.logs_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'request_id': request_id,
            'action': action_type,
            'status': status,
            'details': details
        }
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


def main():
    parser = argparse.ArgumentParser(description='Approval Workflow System')
    parser.add_argument('command', choices=['create', 'list', 'execute', 'check'],
                        help='Command to run')
    parser.add_argument('--vault', default='.', help='Path to Obsidian vault')
    parser.add_argument('--action', help='Action type (send_email, payment, etc.)')
    parser.add_argument('--to', help='Email recipient')
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body')
    parser.add_argument('--priority', default='normal', 
                        choices=['low', 'normal', 'high', 'critical'])
    parser.add_argument('--expires', type=int, default=24, 
                        help='Expires in hours')
    
    args = parser.parse_args()
    
    workflow = ApprovalWorkflow(args.vault)
    
    if args.command == 'create':
        if not args.action:
            print('Error: --action required for create command')
            sys.exit(1)
        
        details = {}
        if args.to:
            details['to'] = args.to
        if args.subject:
            details['subject'] = args.subject
        if args.body:
            details['body'] = args.body
        
        request_id = workflow.create_request(
            action_type=args.action,
            details=details,
            priority=args.priority,
            expires_in_hours=args.expires
        )
        print(f'Created approval request: {request_id}')
        
    elif args.command == 'list':
        pending = workflow.check_pending()
        if pending:
            print(f'Pending approvals ({len(pending)}):')
            for item in pending:
                print(f"  - {item['file']}")
        else:
            print('No pending approvals')
        
    elif args.command == 'execute':
        results = workflow.execute_approved_actions()
        if results:
            print(f'Executed {len(results)} action(s):')
            for result in results:
                print(f"  - {result['file']}: {result['status']}")
        else:
            print('No approved actions to execute')
    
    elif args.command == 'check':
        pending = workflow.check_pending()
        approved = workflow.check_approved()
        print(f'Pending: {len(pending)}')
        print(f'Approved (ready to execute): {len(approved)}')


if __name__ == '__main__':
    main()
