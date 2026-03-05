---
name: ralph-wiggum-loop
description: |
  Ralph Wiggum persistence loop for autonomous multi-step task completion.
  Keeps Qwen Code iterating until tasks are complete by intercepting exit
  and re-injecting prompts. Use for complex multi-step workflows.
---

# Ralph Wiggum Loop

Autonomous task completion through persistence.

## Overview

The Ralph Wiggum pattern keeps Qwen Code working until a task is complete:

1. Start task with completion criteria
2. Qwen processes and tries to exit
3. Loop checks: Is task complete?
4. NO → Block exit, re-inject prompt
5. YES → Allow exit
6. Repeat until done or max iterations

## Usage

### Start Ralph Loop

```bash
/ralph-loop "Process all files in Needs_Action and move to Done" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

### Completion Strategies

**1. Promise-based (Simple)**

Qwen outputs `<promise>TASK_COMPLETE</promise>` when done.

**2. File Movement (Advanced)**

Loop detects when files move to `/Done` folder.

## Python Implementation

```python
from ralph_wiggum import RalphLoop

loop = RalphLoop(
    vault_path="C:/Vault",
    max_iterations=10,
    completion_check="file_movement"
)

# Start loop
loop.run("Process all pending items")
```

## Integration with Orchestrator

```bash
# Create state file
python ralph_loop.py create \
  --vault "C:/Vault" \
  --prompt "Process all items in Needs_Action" \
  --max-iterations 10

# Start Qwen with loop
cd C:/Vault
qwen
```

## Example Flow

```
User: /ralph-loop "Process emails and draft responses"

[Iteration 1]
Qwen: Reads emails, creates 3 draft responses
Qwen: *tries to exit*
Loop: Tasks incomplete → Re-inject prompt

[Iteration 2]
Qwen: Reviews drafts, improves content
Qwen: *tries to exit*
Loop: Tasks incomplete → Re-inject prompt

[Iteration 3]
Qwen: Finalizes drafts, moves to Approved
Qwen: <promise>TASK_COMPLETE</promise>
Loop: Task complete → Allow exit
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| max_iterations | 10 | Maximum loop iterations |
| completion_check | promise | promise or file_movement |
| timeout_seconds | 3600 | Maximum total runtime |
| log_file | ralph_loop.log | Log file path |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Loop never exits | Check completion criteria is clear |
| Exits too early | Use file_movement instead of promise |
| Max iterations hit | Task too complex, break into smaller tasks |
