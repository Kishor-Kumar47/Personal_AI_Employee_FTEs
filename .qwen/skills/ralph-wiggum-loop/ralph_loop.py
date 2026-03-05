"""
Ralph Wiggum Loop - Autonomous Task Completion

Keeps Qwen Code working until tasks are complete by:
1. Intercepting exit attempts
2. Checking completion criteria
3. Re-injecting prompts if incomplete

Usage:
    python ralph_loop.py create --vault "C:/Vault" --prompt "Process all items" --max-iterations 10
"""

import sys
import io
import json
import argparse
from pathlib import Path
from datetime import datetime


# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class RalphLoop:
    """Ralph Wiggum persistence loop"""
    
    def __init__(self, vault_path: str, max_iterations: int = 10):
        self.vault_path = Path(vault_path).expanduser().resolve()
        self.max_iterations = max_iterations
        self.state_dir = self.vault_path / '.ralph_state'
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.state_dir / 'state.json'
        self.log_file = self.vault_path / 'Logs' / 'ralph_loop.log'
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def create_task(self, prompt: str, completion_criteria: str = "TASK_COMPLETE") -> str:
        """Create a new Ralph loop task"""
        task_id = f"RALPH_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        state = {
            'task_id': task_id,
            'prompt': prompt,
            'completion_criteria': completion_criteria,
            'iteration': 0,
            'max_iterations': self.max_iterations,
            'status': 'pending',
            'created': datetime.now().isoformat(),
            'history': []
        }
        
        self.state_file.write_text(json.dumps(state, indent=2), encoding='utf-8')
        
        self._log(f"Created task: {task_id}")
        
        return task_id
    
    def check_completion(self, criteria: str) -> bool:
        """Check if task is complete"""
        if criteria == "TASK_COMPLETE":
            # Check for completion marker
            marker_file = self.state_dir / 'complete.marker'
            return marker_file.exists()
        
        elif criteria == "file_movement":
            # Check if Needs_Action is empty
            needs_action = self.vault_path / 'Needs_Action'
            if needs_action.exists():
                items = list(needs_action.glob('*.md'))
                return len(items) == 0
            return True
        
        elif criteria == "all_plans_done":
            # Check if all plans are in Done
            plans_dir = self.vault_path / 'Plans'
            if plans_dir.exists():
                plans = list(plans_dir.glob('*.md'))
                return len(plans) == 0
            return True
        
        return False
    
    def mark_complete(self):
        """Mark task as complete"""
        marker_file = self.state_dir / 'complete.marker'
        marker_file.write_text(f"Completed at {datetime.now().isoformat()}")
        
        state = self._load_state()
        if state:
            state['status'] = 'completed'
            state['completed'] = datetime.now().isoformat()
            self.state_file.write_text(json.dumps(state, indent=2), encoding='utf-8')
        
        self._log("Task marked as complete")
    
    def next_iteration(self) -> dict:
        """Move to next iteration"""
        state = self._load_state()
        
        if not state:
            return {'error': 'No state found'}
        
        state['iteration'] += 1
        state['history'].append({
            'iteration': state['iteration'],
            'timestamp': datetime.now().isoformat()
        })
        
        if state['iteration'] >= state['max_iterations']:
            state['status'] = 'max_iterations_reached'
            self._log(f"Max iterations ({state['max_iterations']}) reached")
        
        self.state_file.write_text(json.dumps(state, indent=2), encoding='utf-8')
        
        return state
    
    def _load_state(self) -> dict:
        """Load current state"""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text(encoding='utf-8'))
        return None
    
    def _log(self, message: str):
        """Log message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} - {message}\n")
    
    def get_status(self) -> dict:
        """Get current loop status"""
        return self._load_state() or {'status': 'no_active_loop'}


def main():
    parser = argparse.ArgumentParser(description='Ralph Wiggum Loop')
    parser.add_argument('command', choices=['create', 'check', 'complete', 'status', 'next'],
                        help='Command to run')
    parser.add_argument('--vault', '-v', default='.', help='Path to vault')
    parser.add_argument('--prompt', '-p', help='Task prompt (for create)')
    parser.add_argument('--max-iterations', '-m', type=int, default=10,
                        help='Maximum iterations')
    parser.add_argument('--criteria', '-c', default='TASK_COMPLETE',
                        choices=['TASK_COMPLETE', 'file_movement', 'all_plans_done'],
                        help='Completion criteria')
    
    args = parser.parse_args()
    
    loop = RalphLoop(args.vault, args.max_iterations)
    
    if args.command == 'create':
        if not args.prompt:
            print('Error: --prompt required for create')
            sys.exit(1)
        
        task_id = loop.create_task(args.prompt, args.criteria)
        
        print(f'✅ Ralph Loop created: {task_id}')
        print()
        print(f'Prompt: {args.prompt}')
        print(f'Max iterations: {args.max_iterations}')
        print(f'Completion criteria: {args.criteria}')
        print()
        print('Next steps:')
        print('1. Start Qwen Code in the vault directory')
        print('2. Process the task')
        print('3. Output "<promise>TASK_COMPLETE</promise>" when done')
        print('   OR move files to /Done (if using file_movement)')
        
    elif args.command == 'check':
        state = loop.get_status()
        is_complete = loop.check_completion(args.criteria)
        
        print(f'Task: {state.get("task_id", "none")}')
        print(f'Iteration: {state.get("iteration", 0)}/{state.get("max_iterations", 10)}')
        print(f'Status: {state.get("status", "unknown")}')
        print(f'Complete: {"✅ Yes" if is_complete else "❌ No"}')
        
    elif args.command == 'complete':
        loop.mark_complete()
        print('✅ Task marked as complete')
        
    elif args.command == 'status':
        state = loop.get_status()
        print(json.dumps(state, indent=2))
        
    elif args.command == 'next':
        state = loop.next_iteration()
        print(f'Iteration: {state.get("iteration", 0)}')
        print(f'Status: {state.get("status", "unknown")}')
        if state.get('status') == 'max_iterations_reached':
            print('⚠️ Max iterations reached!')


if __name__ == '__main__':
    main()
