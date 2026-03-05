# Personal AI Employee FTEs - Project Context

## Project Overview

This is a **hackathon project** focused on building **Autonomous AI Employees** (Digital FTEs - Full-Time Equivalents). The project creates a local-first, agent-driven system where AI agents proactively manage personal and business affairs 24/7 using **Claude Code** as the reasoning engine and **Obsidian** as the management dashboard.

### Core Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine for decision-making |
| **Memory/GUI** | Obsidian (Markdown) | Local dashboard and knowledge base |
| **Senses** | Python Watcher Scripts | Monitor Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | External actions (email, browser, payments) |

### Key Concepts

- **Watcher Pattern**: Lightweight Python scripts monitor inputs and create `.md` files in `/Needs_Action` folder
- **Ralph Wiggum Loop**: A Stop hook pattern that keeps Claude iterating until tasks are complete
- **Human-in-the-Loop**: Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Agent Skills**: All AI functionality implemented as [Claude Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

## Directory Structure

```
Personal_AI_Employee_FTEs/
├── .qwen/skills/           # Qwen Code skills (browsing-with-playwright)
├── .claude/                # Claude Code configuration (plugins, settings)
├── *.md                    # Documentation and hackathon guide
└── skills-lock.json        # Skill version tracking
```

### Expected Vault Structure (to be created)

```
Vault/
├── Inbox/                  # Raw incoming items
├── Needs_Action/           # Items requiring processing
├── In_Progress/<agent>/    # Claimed items (prevents double-work)
├── Pending_Approval/       # Awaiting human approval
├── Approved/               # Approved actions ready for execution
├── Done/                   # Completed tasks
├── Plans/                  # Generated action plans
├── Briefings/              # CEO briefing reports
├── Accounting/             # Financial records
├── Business_Goals.md       # Objectives and metrics
├── Dashboard.md            # Real-time status summary
└── Company_Handbook.md     # Rules of engagement
```

## Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts & orchestration |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control |

## Available Skills

### browsing-with-playwright

Browser automation using Playwright MCP for web scraping, form submission, and UI automation.

**Server Management:**
```bash
# Start server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Stop server
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh

# Verify server
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py
```

**Key Operations:**
- Navigate websites, fill forms, click elements
- Take screenshots and extract data
- Execute JavaScript via `browser_evaluate`
- Run multi-step code via `browser_run_code`

See `.qwen/skills/browsing-with-playwright/SKILL.md` for detailed usage.

## Hackathon Tiers

| Tier | Focus | Estimated Time |
|------|-------|----------------|
| **Bronze** | Foundation (1 Watcher, Obsidian vault, basic Claude integration) | 8-12 hours |
| **Silver** | Functional Assistant (2+ Watchers, MCP server, approval workflow) | 20-30 hours |
| **Gold** | Autonomous Employee (Full integration, Odoo accounting, Ralph Wiggum loop) | 40+ hours |
| **Platinum** | Cloud + Local Executive (24/7 deployment, dual-agent sync) | 60+ hours |

## Development Conventions

1. **Local-First**: All data stored locally in Obsidian Markdown
2. **File-Based Communication**: Agents communicate via file movements between folders
3. **Claim-by-Move Rule**: First agent to move item to `/In_Progress/<agent>/` owns it
4. **Single-Writer Rule**: Only Local agent writes to `Dashboard.md`
5. **Security**: Secrets never sync (`.env`, tokens, banking credentials stay local)

## Key Commands

### Claude Code Operations
```bash
# Check version
claude --version

# Start Ralph Wiggum loop (persistence pattern)
/ralph-loop "Process all files in /Needs_Action" --completion-promise "TASK_COMPLETE" --max-iterations 10
```

### MCP Server Configuration
Configure in `~/.config/claude-code/mcp.json`:
```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"]
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@anthropic/browser-mcp"],
      "env": { "HEADLESS": "true" }
    }
  ]
}
```

## Resources

- **Main Documentation**: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Playwright Tools Reference**: `.qwen/skills/browsing-with-playwright/references/playwright-tools.md`
- **Ralph Wiggum Pattern**: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- **Agent Skills Docs**: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

## Meeting Schedule

**Research & Showcase**: Every Wednesday at 10:00 PM PKT
- Zoom: https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- YouTube: https://www.youtube.com/@panaversity
