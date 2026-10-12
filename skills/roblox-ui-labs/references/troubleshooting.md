# UI Labs troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| The story doesn't appear | The ModuleScript name must end in `.story`; the module must be in the edit DataModel (check Rojo sync) and under a storybook's `storyRoots` (or it shows under "Unknown Stories"). A successful build doesn't prove discovery. |
| `props.controls` is nil, or controls aren't Sources | The table lacks `vide = Vide` (so it isn't treated as a Vide story), or it is a generic story, where `controls` holds plain values. Use the shape that matches the story type. |
| Yield warning, or the story doesn't render | The story yielded. Remove waits; load data before the story or use mocks. |
| UI or connections remain after unmount | A function story errored before returning its cleanup, or a Vide story created resources without `Vide.cleanup`. Clean up partial work before rethrowing, and register cleanups right away. |
| A nested mount leaks | The story called `Vide.mount` itself. Return the component instead. |
| Two UI Labs widgets | A local-file install (`UI Labs (DEV)`) and a Creator Store install (`UI Labs`) are both loaded. Identify the one under test. Identical files can have different names; their hashes show which are the same, but not which one Studio loaded. Disable one copy at a time (only if the task allows it), reload Studio, and record which file backs the widget. |
| A stale preview, or leaks after reloads | Reduce to one story and stop/remount it. Record Output and the exact plugin version. Source review is not a hot-reload test. |
| The installer reports a hash failure | Compare the official URL, the expected digest and the downloaded bytes. Keep the previous managed file; never bypass the digest. |
