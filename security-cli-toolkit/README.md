# 🛡️ Security CLI Toolkit (sctk)

> **Portfolio Project #16** — Multi-language security scanner with unified CLI.

A pre-deploy security scanner that runs 3 independent tools (Go, Rust, Python) under one dispatcher, normalizing output to a single JSON schema. Built for teams that want offline, vendor-neutral secret detection without SaaS dependencies.

## Key Features

| Feature | Detail |
|---------|--------|
| **3 scanners** | `sift` (Go) — entropy + regex secret detection, `secradar` (Rust) — git-history buried secrets, `dockguard` (Python) — Dockerfile linter |
| **Unified output** | Single `sctk scan .` merges all tools into one JSON array; `output-schema.json` for CI parsing |
| **CI-ready** | GitHub Actions workflow, pre-commit hook, `jq`-friendly JSON; fail build on HIGH/CRITICAL |
| **Cross-platform** | Git Bash / MSYS / WSL / Linux; bundled .exe for Windows (no Go/Rust toolchain needed) |
| **Offline** | Zero network calls — code never leaves your machine |

## Scan Example

```json
[
  {"tool": "sift", "rule_id": "S002", "severity": "HIGH", "file": ".env", "line": 2, "snippet": "GH_TOKEN=ghp_12...vwxy"},
  {"tool": "dockguard", "rule_id": "DG001", "severity": "warning", "file": "Dockerfile", "line": 3, "suggestion": "Switch to non-root user"}
]
```

## Tech Stack

![Go](https://img.shields.io/badge/Go-00ADD8?style=flat&logo=go&logoColor=white) `sift` scanner — ~3.9 MB static binary
![Rust](https://img.shields.io/badge/Rust-000000?style=flat&logo=rust&logoColor=white) `secradar` scanner — cargo release build
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) `dockguard` linter + `sctk` dispatcher (bash)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white) Security scan workflow

## Engineering Decisions Worth Noting

- **Bash dispatcher over compiled CLI:** `sctk` is a 200-line bash script — no Rust/Go/Python dependency for the dispatcher itself. Binary or source auto-detection per tool.
- **cygpath bridge:** On Windows/MSYS, Python runs as a Windows binary but paths like `/c/...` aren't recognized. `run_dockguard` converts via `cygpath -w` before invoking Python. Same for Go binaries scanning MSYS paths.
- **Wrapper over `python -m`:** MSYS Python has unreliable module resolution for `__main__.py`. A 7-line `run.py` wrapper (`sys.path.insert` + import) sidesteps the issue.
- **Flattened JSON merge:** Each tool emits different shapes (list vs `{findings:[...]}`); the scanner normalizes all into a flat `[finding, ...]` array with `[1:-1]` bracket-strip for stream concatenation.
- **.siftrules regex constraints:** Sift custom rules split on literal `|` — so alternation uses character classes `[...]` instead of `(?:a|b)`.

## Repository Structure

```
security-cli-toolkit/
├── bin/
│   ├── sctk                     # Unified dispatcher (bash, 200 LOC)
│   ├── sift/sift.exe            # Go binary — entropy secret scanner
│   ├── sift/.siftrules          # 9 custom detection rules (Stripe, GH, Slack, AWS, DB URIs, SSH keys)
│   ├── secradar/secradar.exe    # Rust binary — git-history secret scanner
│   └── dockguard/               # Python Dockerfile linter (source + run.py wrapper)
├── extras/
│   ├── github-actions-security.yml
│   ├── pre-commit-hook.sh
│   ├── Dockerfile.secure
│   └── REPORT-TEMPLATE.md
├── docs/QUICKSTART.md
├── output-schema.json           # JSON Schema for normalized scan output
└── README.md
```

## Verification

```bash
sctk status                    # ✓ sift ✓ secradar ✓ dockguard
sctk scan ./src --output report.json
jq '.[] | select(.severity=="HIGH")' report.json
```

## Commercial Bundle

The production bundle (prebuilt binaries, Windows .exe, CI templates) is available as a commercial product. Source scanners are MIT-licensed; templates and packaging are licensed.

> [**→ Commercial repo (private)**](https://github.com/afuckingco/sctk-commercial)
> [**→ Gumroad listing**](https://gumroad.com/l/sctk-commercial)

---

**Built by A.A. Pangimpian** — PILGRIMS v17 security framework, SignBridge AI (92.4% accuracy).
