"""
Scheduler - Create and manage scheduled tasks for AI Employee

Supports Windows Task Scheduler and Linux/Mac cron.

Usage:
    python scheduler.py create --name "Task_Name" --command "qwen" --schedule "daily" --time "08:00"
    python scheduler.py list
    python scheduler.py run --name "Task_Name"
    python scheduler.py remove --name "Task_Name"
"""

import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timedelta


class TaskScheduler:
    """Manage scheduled tasks for AI Employee"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).expanduser().resolve()
        self.scheduler_dir = self.vault_path / 'scheduler'
        self.tasks_file = self.scheduler_dir / 'tasks.json'
        self.logs_dir = self.vault_path / 'Logs' / 'scheduler'
        
        for dir_path in [self.scheduler_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> dict:
        """Load tasks from file"""
        if self.tasks_file.exists():
            return json.loads(self.tasks_file.read_text(encoding='utf-8'))
        return {'tasks': []}
    
    def _save_tasks(self):
        """Save tasks to file"""
        self.tasks_file.write_text(json.dumps(self.tasks, indent=2), encoding='utf-8')
    
    def create_task(self, name: str, command: str, args: str = '',
                    schedule: str = 'daily', time: str = '08:00',
                    day: str = 'monday', date: str = None) -> dict:
        """
        Create a scheduled task
        
        Args:
            name: Task name
            command: Command to execute
            args: Command arguments
            schedule: daily, weekly, monthly, hourly, once
            time: Time to run (HH:MM)
            day: Day of week (for weekly) or day of month (for monthly)
            date: Specific date for one-time tasks (YYYY-MM-DD)
            
        Returns:
            dict: Task configuration
        """
        # Calculate next run time
        next_run = self._calculate_next_run(schedule, time, day, date)
        
        task = {
            'name': name,
            'command': command,
            'args': args,
            'schedule': schedule,
            'time': time,
            'day': day,
            'date': date,
            'enabled': True,
            'created': datetime.now().isoformat(),
            'last_run': None,
            'next_run': next_run.isoformat()
        }
        
        # Remove existing task with same name
        self.tasks['tasks'] = [t for t in self.tasks['tasks'] if t['name'] != name]
        self.tasks['tasks'].append(task)
        self._save_tasks()
        
        # Register with OS scheduler
        self._register_with_os(task)
        
        return task
    
    def _calculate_next_run(self, schedule: str, time: str, day: str, date: str) -> datetime:
        """Calculate next run time based on schedule"""
        now = datetime.now()
        hour, minute = map(int, time.split(':'))
        
        if schedule == 'once' and date:
            run_date = datetime.strptime(date, '%Y-%m-%d')
            return run_date.replace(hour=hour, minute=minute)
        
        if schedule == 'hourly':
            next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            return next_run
        
        if schedule == 'daily':
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
        
        if schedule == 'weekly':
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            target_day = days.index(day.lower()) if day.lower() in days else 0
            current_day = now.weekday()
            days_ahead = target_day - current_day
            if days_ahead < 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(weeks=1)
            return next_run
        
        if schedule == 'monthly':
            target_day = int(day) if day.isdigit() else 1
            next_run = now.replace(day=target_day, hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                # Move to next month
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)
            return next_run
        
        # Default: daily at specified time
        return self._calculate_next_run('daily', time, day, date)
    
    def _register_with_os(self, task: dict):
        """Register task with OS scheduler"""
        import platform
        system = platform.system()
        
        task_name = f"AI_Employee_{task['name']}"
        command = f'{task["command"]} {task["args"]}'.strip()
        
        if system == 'Windows':
            self._register_windows(task_name, command, task)
        else:
            self._register_cron(task_name, command, task)
    
    def _register_windows(self, task_name: str, command: str, task: dict):
        """Register with Windows Task Scheduler"""
        schedule_map = {
            'daily': '/sc DAILY',
            'weekly': f'/sc WEEKLY /d {task["day"][:3].upper()}',
            'monthly': f'/sc MONTHLY /d {task["day"]}',
            'once': f'/sc ONCE /st {task["time"].replace(":", "")} /sd {task["date"].replace("-", "/")}' if task.get("date") else '',
            'hourly': '/sc HOURLY'
        }
        
        time_arg = f'/st {task["time"]}' if task['schedule'] != 'hourly' else ''
        
        schtasks_cmd = (
            f'schtasks /create /tn "{task_name}" '
            f'/tr "{command}" '
            f'{schedule_map.get(task["schedule"], "")} '
            f'{time_arg} '
            f'/f'
        )
        
        try:
            subprocess.run(schtasks_cmd, shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not register with Task Scheduler: {e}")
    
    def _register_cron(self, task_name: str, command: str, task: dict):
        """Register with cron (Linux/Mac)"""
        cron_schedule = self._to_cron_schedule(task)
        cron_entry = f'{cron_schedule} # {task_name}: {command}'
        
        print(f"To register with cron, add this entry:")
        print(f"  {cron_entry}")
        print(f"Run: crontab -e")
    
    def _to_cron_schedule(self, task: dict) -> str:
        """Convert task to cron format"""
        minute, hour = task['time'].split(':')
        
        if task['schedule'] == 'hourly':
            return f'{minute} * * * *'
        elif task['schedule'] == 'daily':
            return f'{minute} {hour} * * *'
        elif task['schedule'] == 'weekly':
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            cron_day = (days.index(task['day'].lower()) + 1) % 7 if task['day'].lower() in days else '1'
            return f'{minute} {hour} * * {cron_day}'
        elif task['schedule'] == 'monthly':
            return f'{minute} {hour} {task["day"]} * *'
        else:
            return f'{minute} {hour} * * *'
    
    def list_tasks(self) -> list:
        """List all scheduled tasks"""
        return self.tasks['tasks']
    
    def run_task(self, name: str) -> dict:
        """Run a task immediately"""
        task = next((t for t in self.tasks['tasks'] if t['name'] == name), None)
        if not task:
            return {'status': 'error', 'message': f'Task not found: {name}'}
        
        command = f'{task["command"]} {task["args"]}'.strip()
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Update task
            task['last_run'] = datetime.now().isoformat()
            task['next_run'] = self._calculate_next_run(
                task['schedule'], task['time'], task.get('day', ''), task.get('date')
            ).isoformat()
            self._save_tasks()
            
            # Log
            self._log_task(name, 'success', duration, result.stdout[:500] if result.stdout else '')
            
            return {
                'status': 'success',
                'task': name,
                'duration_seconds': duration,
                'output': result.stdout[:500] if result.stdout else ''
            }
            
        except subprocess.TimeoutExpired:
            self._log_task(name, 'timeout', 300, '')
            return {'status': 'timeout', 'task': name}
        except Exception as e:
            self._log_task(name, 'error', 0, str(e))
            return {'status': 'error', 'task': name, 'error': str(e)}
    
    def remove_task(self, name: str) -> bool:
        """Remove a scheduled task"""
        task = next((t for t in self.tasks['tasks'] if t['name'] == name), None)
        if not task:
            return False
        
        self.tasks['tasks'] = [t for t in self.tasks['tasks'] if t['name'] != name]
        self._save_tasks()
        
        # Unregister from OS scheduler
        import platform
        system = platform.system()
        task_name = f"AI_Employee_{name}"
        
        if system == 'Windows':
            subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True)
        
        return True
    
    def _log_task(self, name: str, status: str, duration: float, output: str):
        """Log task execution"""
        log_file = self.logs_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'task': name,
            'status': status,
            'duration_seconds': duration,
            'output': output[:500]
        }
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


def main():
    parser = argparse.ArgumentParser(description='AI Employee Task Scheduler')
    parser.add_argument('command', choices=['create', 'list', 'run', 'remove'],
                        help='Command to run')
    parser.add_argument('--vault', default='.', help='Path to Obsidian vault')
    parser.add_argument('--name', help='Task name')
    parser.add_argument('--command', dest='cmd', help='Command to execute')
    parser.add_argument('--args', default='', help='Command arguments')
    parser.add_argument('--schedule', default='daily',
                        choices=['daily', 'weekly', 'monthly', 'hourly', 'once'],
                        help='Schedule type')
    parser.add_argument('--time', default='08:00', help='Time to run (HH:MM)')
    parser.add_argument('--day', default='monday', help='Day of week or month')
    parser.add_argument('--date', help='Specific date for one-time tasks (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    scheduler = TaskScheduler(args.vault)
    
    if args.command == 'create':
        if not args.name or not args.cmd:
            print('Error: --name and --command required for create')
            sys.exit(1)
        
        task = scheduler.create_task(
            name=args.name,
            command=args.cmd,
            args=args.args,
            schedule=args.schedule,
            time=args.time,
            day=args.day,
            date=args.date
        )
        print(f'Created task: {args.name}')
        print(f'Next run: {task["next_run"]}')
        
    elif args.command == 'list':
        tasks = scheduler.list_tasks()
        if tasks:
            print(f'Scheduled tasks ({len(tasks)}):')
            for task in tasks:
                status = '✓' if task['enabled'] else '✗'
                print(f"  {status} {task['name']}: {task['schedule']} at {task['time']}")
                print(f"      Command: {task['command']} {task['args']}")
                print(f"      Next run: {task['next_run']}")
        else:
            print('No scheduled tasks')
            
    elif args.command == 'run':
        if not args.name:
            print('Error: --name required for run')
            sys.exit(1)
        
        result = scheduler.run_task(args.name)
        print(f"Task: {args.name}")
        print(f"Status: {result['status']}")
        if result.get('duration_seconds'):
            print(f"Duration: {result['duration_seconds']:.1f}s")
        if result.get('output'):
            print(f"Output: {result['output'][:200]}")
            
    elif args.command == 'remove':
        if not args.name:
            print('Error: --name required for remove')
            sys.exit(1)
        
        if scheduler.remove_task(args.name):
            print(f'Removed task: {args.name}')
        else:
            print(f'Task not found: {args.name}')


if __name__ == '__main__':
    main()
