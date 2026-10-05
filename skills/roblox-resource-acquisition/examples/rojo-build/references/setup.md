# Setup

1. Resolve the project-owned target and installation before using the common path.

Resolve the active project's selected tool and configuration. This example models a child installed at project/repository scope; an unresolved project does not authorize a user/global fallback. Use Python 3.10+ and the canonical `rojo-rbx/rojo` 7.7.0 executable. A broken PATH shim may have an already installed versioned executable in the configured tool-manager cache; confirm `rojo --version` and its integrity before use.

Keep project-specific files outside this child. The project owns `tool-lock.json` containing `canonical_url: https://github.com/rojo-rbx/rojo`, `package_id: rojo-rbx/rojo`, `version: 7.7.0` and `sha256` as the raw SHA-256 hex of the inspected executable. This helper's lock format uses raw hex; schema-v3 evidence-input hashes separately require the `sha256:` prefix. The project also owns a Rojo JSON configuration, authored strict Luau source and `expected-scripts.json` with a `scripts` list of objects containing `path`, `class` and `sourceFile`. Build the expected paths from the intended project contract, independently from Rojo's mapping: a successful build can omit a whole directory.

In the commands below, PowerShell variables `$Parent`, `$Child`, `$Project` and `$Rojo` hold the resolved absolute installed parent directory, canonical child directory, project root and inspected executable. Another shell uses equivalent path arguments. Do not embed a task's machine-specific paths into this reusable child.
