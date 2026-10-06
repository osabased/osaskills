# Troubleshooting

### Installation or lifecycle symptom

- Missing story: confirm the ModuleScript suffix is `.story`, development mapping includes it, source returns the correct table and Studio/Rojo loaded the current source. Build success alone does not prove plugin discovery.
- Nil `props.controls` or missing cleanup: check the selected advanced Vide contract and pass the same Vide package through `vide`; avoid nesting gameplay mounts.
- Multiple widgets: identify local `UILabs(DEV)` versus standard `UILabs` installations before interpreting results. Preserve unrelated plugin ownership.
- Identical local copies: filenames can differ while release hashes, toolbar names and widget IDs match. Enumerate the actual local plugin files through the host's plugin-folder binding and retain their full paths. When the task authorizes isolating those copies, disable/unload one task-owned copy at a time and reload Studio as needed to associate the remaining preview with its file. Preserve unrelated plugins. Until that association is observed, report loaded-copy/discovery identity as unavailable; byte equality alone cannot establish uniqueness.
- Stale preview or repeated reload leakage: reduce to one story, stop/remount and retain Output plus exact version. Diagnose with the parent repair workflow; source review is not a hot-reload pass.
- Installer/hash failure: compare official release URL, expected digest and actual bytes. Preserve the previous managed asset; never bypass the digest to finish setup.

## Security boundary

Studio plugins execute editor code with authoring privileges. Download the canonical exact release, verify its digest and preserve the managed asset's identity. Stories execute arbitrary project code: use local fixtures/mock data, keep credentials and live service actions out, and do not publish or mutate production data merely to prove a preview. Keep gameplay authorization server-owned.

## Alternatives

- Use a development-only PlayerGui workbench to preview one component with explicit gameplay mount cleanup. Other story hosts or framework-specific test tools may suit different needs. Preserve an already-selected UI Labs target; an alternative or upgrade remains a decision for the project's owning authority.
