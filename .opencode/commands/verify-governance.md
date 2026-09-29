---
description: Validate OpenSpec specs, the OKF knowledge bundle, and relative links
agent: build
---

Run the governance checks for this repository. Do not commit until all three pass.
Commands run from the project root.

## 1. OpenSpec — both roots, independently

OpenSpec resolves the *nearest* root by walking up, so each root must be
validated from its own directory. Running the second command from the repo root
would silently re-validate the first one.

```
!`OPENSPEC_TELEMETRY=0 openspec validate --specs --strict 2>&1 | tail -15`

!`cd mcp && OPENSPEC_TELEMETRY=0 openspec validate --all --strict 2>&1 | tail -15`
```

## 2. OKF — knowledge bundle

```
!`python3 scripts/okf_lint.py 2>&1 | tail -20`
```

## 3. Relative links in authored trees

`openspec validate` does **not** check that markdown links resolve, so this is a
separate step. It catches the most common authoring failure: a relative link
written for the wrong directory depth.

```
!`python3 -c "
import re
from pathlib import Path
pat = re.compile(r'\[[^\]]*\]\(([^)#][^)]*)\)')
targets = ['openspec', 'knowledge', 'docs/proposal', 'mcp/openspec', 'AGENTS.md', 'README.md']
total = broken = 0
for t in targets:
    p = Path(t)
    files = sorted(p.rglob('*.md')) if p.is_dir() else ([p] if p.is_file() else [])
    for md in files:
        for raw in pat.findall(md.read_text(encoding='utf-8')):
            link = raw.split()[0]
            if link.startswith(('http://', 'https://', 'mailto:')):
                continue
            total += 1
            if not (md.parent / link).resolve().exists():
                broken += 1
                print(f'BROKEN {md}: {link}')
print(f'{total} relative links checked, {broken} broken')
" 2>&1 | tail -20`
```

## Now interpret the output

- **Any `✗` from either OpenSpec root** — fix the spec. Requirements need SHALL
  or MUST, at least one scenario each, and scenarios must use exactly four
  `####` hashes.
- **OKF linter failure** — check that `type:` is non-empty, `status` is one of
  `draft` / `stable` / `deprecated`, and timestamps are ISO-8601. Child
  `index.md` files carry no frontmatter; the bundle-root `knowledge/index.md` may
  carry `okf_version` only.
- **Broken links** — a relative link is resolved from the file's own directory.
  From `openspec/specs/<capability>/spec.md` the knowledge bundle is
  `../../../knowledge/features/<capability>.md` — three levels up, not two.

If a spec disagrees with the code, do not relax the spec to match the bug. Report
the divergence and let a decision be made; a failing spec is a finding, not an
error to be silenced.
