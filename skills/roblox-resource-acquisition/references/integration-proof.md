# Executable integration and lifecycle proof

Read this reference when generated guidance claims executable integration, composes the resource with an adopted cleanup/lifecycle library, or claims runtime behavior such as startup, real input, animation, or clean Studio diagnostics. Skip it for advice-only guidance and inert utilities whose documented behavior has no owned runtime lifecycle.

## Bound the claims before building the harness

List the behaviors the child will claim and assign each to the cheapest evidence surface that can actually observe it. Keep these proof lanes separate:

- **Static and construction:** strict analysis, formatting/lint, build, module loading, object construction, and source-grounded API/type compatibility.
- **Owned behavior and lifecycle:** state changes, subscriptions, partial acquisition, cancellation, teardown, repeated destroy, and producer isolation after disposal.
- **Runtime host behavior:** normal startup, real user input/focus, rendered layout, animation progression/interruption, engine callbacks, and host shutdown.
- **Diagnostics:** unexpected warnings/errors from before fixture loading through the end of the harness-owned runtime boundary.

A passing analyzer, build, CLI test, domain-method call, or construction assertion proves only the lane it observes. It does not establish real input, rendered layout, animation quality, normal client startup, or a clean Studio console. Add Studio/runtime work only when the resource guidance actually makes one of those claims.

## Compose lifecycle owners from inspected behavior

When the integration combines the resource with a cleanup owner or another lifecycle library, inspect the exact pinned implementations that determine ordering, error continuation, reentrancy, and cancellation. Do not infer those guarantees from method names, popularity, or the fact that both objects expose `Destroy`/`Cleanup`.

Create the durable owner before fallible acquisition and register its cleanup path before constructing any resource that can leave state behind. If ordering or best-effort continuation matters, encode it in one owner-held composite cleanup rather than assuming separate cleanup entries run in insertion or reverse order. The composite must:

1. detach each owned handle before invoking it so repeated or reentrant teardown cannot run it twice;
2. stop producers, callbacks, and pending work before consuming the state or view they can reach;
3. attempt every top-level phase even when one phase fails, while collecting labelled failures;
4. keep a construction/body failure primary and append cleanup failures without replacing it; and
5. make partial acquisition, cancellation, explicit destroy, automatic owner/root destruction, and repeated destroy converge on the same idempotent path.

An acquisition API must either return an owned disposer after success or roll back its own side effects before raising. If the inspected API can throw after side effects without returning a handle, record that as an integration defect rather than pretending the caller can clean it.

Distinguish feature/component resources from package-global or process-global work. A component owner cleans only what it activated or acquired. Apply the host-ownership boundary below before requiring or exercising any global finalizer.

## Respect host ownership

Package-global schedulers, shared providers, and other runtime-wide work may legitimately live for the normal supported runtime lifetime. Require a supported host-level finalizer only when the claimed behavior must explicitly stop at a host boundary the harness or application owns. A component must not reach into private modules or stop shared state it does not own. Do not treat a missing shutdown API as a resource defect until a red-capable guard attributes the continuing work to that resource and the supported lifetime contract requires it to stop at the owned boundary.

For a disposable Studio process launched and owned by the harness, the owned boundary includes process exit; the harness may terminate that process and its outer runner must inspect diagnostics emitted after the in-process done marker through exit. For an existing user Studio application, leave the application open. If the task starts a play session in it, the owned boundary ends after that session's supported stop and teardown; stop only the task-started session and preserve any pre-existing play session. Never turn a UI-runtime or clean-console proof requirement into permission to close the user's Studio process.

## Keep examples executable and authoritative

Use one maintained representative fixture as the source for executable examples and integration proof. Put project-authored Luau on a canonically strict-analyzed path and run it with the exact adopted resource and companion-library pins. Minimal fakes may inject a failure at an explicit seam, but they do not prove real library composition, typing, startup, or teardown behavior.

Derive child examples from that fixture or point to it. Do not maintain a second implementation in prose. Record the fixture, relevant API/contract/configuration inputs, and each material companion dependency as scoped `skill_validation.checks[].inputs`; a passing check becomes stale when one of those hashed inputs changes.

During an authorized integration, add the applicable assertions to the fixture and the project's owning analyzer/test/Studio harness so the claimed contract fails mechanically. If the task does not authorize that integration surface or the environment cannot execute it, narrow the claim and record the unavailable lane instead of substituting advice.

## Prove failure and disposal behavior

For integrations with owned lifecycle work, the maintained fixture must cover the applicable cases:

- failure after each meaningful partial-acquisition boundary;
- a producer or cleanup phase that throws while later phases still run;
- simultaneous body/construction and cleanup failure with deterministic labelled reporting;
- cancellation or invalidation of waits, tasks, and callbacks;
- repeated or reentrant destroy with every resource attempted at most once;
- automatic owner/root destruction when the integration promises it; and
- post-disposal producer activity that can no longer mutate, call, or reach the disposed consumer.

Use the real pinned libraries for the success path and for their actual cleanup behavior. Inject only the failing edge needed to make each owner contract deterministic. Do not write a test that asserts ordering or continuation the pinned cleanup library does not provide.

## Require a red-capable diagnostics harness

Claim a clean Studio console only when the harness captures structured warnings and errors from before fixture/spec loading through the complete boundary it owns, as defined in [Respect host ownership](#respect-host-ownership). Unexpected diagnostics must produce a synthetic failure or nonzero result, and the retained artifact must identify the active or last fixture/spec. A done marker, green assertion summary, or listener disconnected before owned teardown is insufficient.

Before accepting that claim, force both an unallowlisted generic warning and a generic error after otherwise passing assertions. Each must fail and retain its output. Intentional diagnostics require exact, test-local expectations; broad package or message-family allowlists are invalid. Finalizers must run after failed assertions, then the harness may take a bounded quiescence turn before disconnecting in-process listeners. For a harness-owned disposable process, the outer runner must still inspect output emitted after the done marker through process exit.

Do not attribute an intermittent or source-less diagnostic to the most visible resource. First make the guard red-capable, then isolate the producer with fresh minimal cases. Until ownership is proved, report the diagnostic and the unproved candidates without changing component or package-global lifecycle.

Record static/construction, owned lifecycle, runtime-host, and diagnostics results as separate current checks or explicit unavailable claims. Use existing `executable-integration` and `lifecycle-failure-cleanup` check kinds with honest execution modes, commands, retained artifacts, and scoped inputs; no new record field is required.
