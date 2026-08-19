# Contributing

Thanks for contributing. Here is a brief guide to keep additions and updates clean, practical, and consistent.

## Workflow

1. **Issues**: Open an issue for bug reports, broken links, or new skill suggestions.
2. **Branches**: Fork the repository and create a feature branch (`git checkout -b feat/my-new-skill`).
3. **Pull Requests**: Submit a PR with a clear summary of what was added or modified and why.

## Skill Format Guidelines

When adding or modifying a skill:

- **Directory**: Place each skill in its own root folder (`<skill-name>/`).
- **SKILL.md**: Must contain valid YAML frontmatter at the top:
  ```yaml
  ---
  name: skill-name
  description: "Triggers and clear purpose of the skill."
  ---
  ```
- **References**: Put deep dives, checklists, and doc maps inside `references/`.
- **Tone & Style**: Keep instructions actionable, concise, and deterministic. Avoid decorative emojis.

## Commit Guidelines

Use concise, conventional commit messages:
- `feat(skill-name): add new skill`
- `fix(skill-name): update references and CVE list`
- `docs: update documentation`
