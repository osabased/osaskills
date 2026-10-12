# Checked child examples

Read the matching example when writing a module child or a development-tool child. Both follow the layout in [child authoring](../references/child-authoring.md#skillmd): `## Check the pin`, `## Core API`, `## Example`, `## Gotchas`, `## Read further`. They are authoring examples, not adopted dependencies or installed skills. `SKILL.example.md` and `resource.example.yaml` become `SKILL.md` and `resource.yaml` only in a separate candidate folder. Don't install an example unchanged or copy its pin into an unrelated project.

- [GoodSignal module child](goodsignal/SKILL.example.md) shows an exact commit, owned connections, a maintained Luau fixture and an explicit scheduler/engine proof boundary.
- [Rojo tool child](rojo-build/SKILL.example.md) shows a real CLI, an independent output contract and a portable smoke generator. Generated project files stay outside the child; the generator is the maintained fixture, while `check_build.py` is the command helper.

The examples pass the same structural validator as real children. Tests copy them outside discovery, validate them, and run the tool fixture with a fake executable to check the wrapper's failure behavior. A structural or fake-tool pass is not a runtime test of the upstream resource.

Maintained fixture paths resolve relative to the child root. Proof conditions name observable results, such as exit status, expected script classes, payload count and preserved output.
