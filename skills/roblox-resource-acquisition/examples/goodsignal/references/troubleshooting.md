# Troubleshooting

### No callback arrives

A missing package or wrong require path prevents setup. Check the installed source coordinate and ModuleScript placement before reconnecting; inspect whether the connection was already disconnected.

### State changes after cleanup

An already dispatched callback can outlive disconnection. Check ownership/invalidation and cancel separately owned work; do not repair this by assuming DisconnectAll cancels tasks.

- The fixture covers one non-yielding listener, payload delivery and repeated cleanup. It does not establish network behavior, callback error continuation, Wait cancellation, engine startup or diagnostics cleanliness.

No special resource-specific security boundary is introduced by local callback dispatch. Preserve server authority, validate client inputs and pin inspected source; never load a same-named unreviewed replacement dynamically.
