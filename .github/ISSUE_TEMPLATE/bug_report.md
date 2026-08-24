---
name: Bug report
about: Report something that doesn't work as documented
title: "fix: "
labels: bug
assignees: ""
---

**Describe the bug**
A clear and concise description of what the bug is.

**To reproduce**

Steps to reproduce the behavior:

1. Start the server with `uv run serve`
2. Call `GET /api/v1/products/search?...`
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
The full JSON response envelope, if applicable:

```json
{}
```

**Environment**

- OS: [e.g., Ubuntu 24.04]
- Python version: [output of `python --version`]
- Relevant `.env` settings (**do not post secrets**): [e.g., READ_ONLY=true]

**Additional context**
Logs, screenshots, or anything else that helps.
