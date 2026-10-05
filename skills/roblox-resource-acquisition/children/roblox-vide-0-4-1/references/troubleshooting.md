# Troubleshooting

### Installation or lifecycle symptom

- User-defined type function diagnostics: confirm the new solver is enabled in both editor and CLI. This target's typed `create` uses UDTFs.
- Unknown class for `create("UIPadding")` or `UISizeConstraint`: this tag's class map omits those helpers. Use native `Instance.new`, parent under the owned root, and keep strict types; do not edit generated/vendor source.
- Getter inference error: use a typed local getter instead of widening to `any`. Avoid nullable initial state until its semantics are reviewed for the selected target.
- Repeat-disposal error/leaked UI: check explicit Instance ownership and the owner's detach-before-dispose wrapper.
- Vendor analyzer errors: report them distinctly. A scoped generated-package diagnostic ignore may match project policy while checking authored consumers; it does not prove upstream source is strict-clean.

## Security boundary

Vide is executable dependency code. Use the selected canonical immutable Git target and locked restore; do not dynamic-require arbitrary asset IDs or silently auto-update it. No special HTTP, credential or persistence boundary is needed for these UI APIs. Validate client-controlled actions on the server and keep secrets out of replicated modules.

## Alternatives

- Native `Instance.new` and events suffice for tiny UI edits. React Roblox, Fusion and other reactive libraries are informational alternatives for different project needs. Preserve the active project's selected Vide pin; replacing it is a decision for that project's authority, not this usage skill.
