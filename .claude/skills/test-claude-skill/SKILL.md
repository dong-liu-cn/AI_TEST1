---
name: test-claude-skill
description: Test skill placed in .claude/skills to verify if Cline can detect it.
---

# test-claude-skill

This is a test skill to verify whether Cline reads skills from the `.claude/skills/` directory within a project.

## Steps
1. If this skill appears in Available skills, Cline reads `.claude/skills/`
2. If not, Cline only reads `.cline/skills/`