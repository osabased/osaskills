===== R1 =====
**Verdict: it doesn't hold up.** The flow can charge a customer without creating an order, and it can charge them more than once. Both problems come from the same ordering.

**1. Charge, then insert, with retries, gives double charges.**
- The server charges the card, and the insert then fails on the unique-constraint race. The server returns 500, and the client retries.
- The retry charges the card again, because nothing ties the two requests together.
- A timeout does the same thing. The charge succeeds, the response is slow or lost, and the client retries into a second charge.
- With 3 retries, a customer can be charged up to 4 times for one order.

**2. A failed insert leaves a charge with no order.**
- If every attempt fails, or the client gives up, the customer has paid and no order exists.
- Nothing in the flow refunds or voids the charge, and nothing reconciles charges against orders.

**3. The unique-constraint failure is being treated as an error when it's a signal.**
- The constraint is probably catching a duplicate request: two concurrent POSTs, or a retry that overlaps the original. It is doing its job, but the server has already charged by the time it fires.
- The check has to happen before the charge. At the moment, the constraint only tells you after the money has moved.
- If the constraint is on something other than a request or order key, I'd want to know what it is. That would be a separate bug.

**4. Retrying on 5xx and timeout isn't safe for a non-idempotent POST.**
- The client can't tell "failed before charging" from "charged, then failed". The retry policy treats them the same.

**Fixes, in priority order**
1. **Add an idempotency key.**
   - The client generates one UUID per checkout attempt and sends it on every retry, as an `Idempotency-Key` header.
   - The server stores the key in a table with a unique constraint, and keeps the order ID and response against it.
   - A repeated key returns the stored result and does not charge again.
2. **Pass the same key to the payment provider.** Stripe and most others support this. It makes the charge itself idempotent even if your own server crashes midway.
3. **Reorder, or make the order a state machine.**
   - Insert the order first as `pending`. The unique constraint then rejects duplicates before any money moves.
   - Charge next, then mark the order `paid`.
   - If you'd rather authorize first, use auth, then insert, then capture. Void the auth if the insert fails.
4. **Handle the race explicitly.** Catch the unique violation, load the existing row, and return it as a success if it's the same logical order.
5. **Add reconciliation.** A periodic job should find provider charges with no matching order and refund them or complete the order. It covers crashes between charge and insert.
6. **Client side:** keep the retries, but add backoff with jitter. They are only safe once the key is in place.

I reviewed the flow as you described it and didn't look at any code. If you share the handler and the schema, I can check the constraint and the transaction boundaries.


===== R2 =====
**Verdict: it doesn't hold up.** The core problem is that a non-idempotent side effect (the charge) runs before a fallible step (the insert), and the client retries with no way for the server to recognize a repeat.

**Failure modes**

1. **Double charges on retry.** Any timeout or 5xx after the charge succeeds makes the client re-POST, and the server charges again. This happens when:
   - the insert fails (the unique-constraint race), so the server returns 500 after the money has moved;
   - the server or DB is slow and the client times out even though the charge went through;
   - the process crashes between charge and insert.

2. **The unique-constraint race is a symptom.** If two requests race on the insert, then two requests also raced through the charge. The unique violation is the only thing that caught the duplicate, and it caught it after the customer was billed. The 500 it produces then triggers a retry, which charges a third time.

3. **Charged with no order.** If the charge succeeds and the insert fails permanently (a DB outage, say), the customer has paid and nothing is recorded. The card was charged but there is no order row to reconcile against.

4. **Timeouts are ambiguous.** The client can't tell "never processed" from "processed, response lost." Retrying blindly on timeout is only safe if the endpoint is idempotent, and this one isn't.

5. **Retries without backoff or jitter.** Three immediate retries during an incident multiply load and widen the race window.

**Fixes, in priority order**

1. **Idempotency key.** The client generates a UUID per checkout attempt and sends it as `Idempotency-Key`, reused across retries. The server stores `(key → request hash, status, response)` with a unique index on the key.
   - A repeat with the same key and body returns the stored result.
   - A repeat with the same key and a different body returns 422.
   - A repeat while the first is in flight returns 409 or waits.

2. **Pass the same key to the payment provider.** Stripe, Adyen and most others support this. It makes the charge itself idempotent even if your own store fails.

3. **Reorder and persist intent first.** Insert the order as `pending` (this is where the unique constraint should fire, before any money moves). Then charge, then mark the order `paid`. If the insert hits a unique violation, treat it as "already exists" and return the existing order, not a 500.

4. **Reconciliation.** Run a job or webhook handler that finds charges with no `paid` order, and `pending` orders with no charge. Either complete or refund them. Rely on the provider's webhooks as the source of truth for charge status.

5. **Retry policy.** Retry only with the idempotency key. Use exponential backoff with jitter. Don't retry 4xx. Consider not retrying non-timeout 5xx without a stable key.

6. **Error semantics.** Map the unique-constraint violation to a deterministic response (200 with the existing order, or 409), not a generic 500.

With 1–3 in place, retries become safe, the race becomes harmless, and a paid customer always has an order record.


===== R3 =====
**Verdict:** CHANGES REQUIRED. Scope: client retry → `POST /checkout` → payment provider → order insert. This is a design-level review of the flow as you described it. I didn't see any code, config, or provider docs, and I ran no checks. The directory is not a git repo and I didn't search it.

**Findings**

- **F1: A card must be charged at most once per checkout intent. Charge-then-insert with client retries has no idempotency.**
  - Scenario: the client sends POST. The server charges the card, and the charge commits at the provider. The insert is slow or the response is lost, so the client times out and retries. The retry is a fresh request, so the server charges again.
  - Result: the customer is double or triple charged, and at most one order row exists.
  - Evidence: the flow as described has no idempotency key or dedupe step, and 5xx and timeout are both retried.
  - Consequence: duplicate charges and refund and support load. This is the most serious failure in the flow.
  - Next (correction): the client generates one checkout or idempotency key per intent and sends it on every retry. The server enforces it with a unique constraint on that key. It also passes the same key to the provider's idempotency mechanism, if the provider supports one. I haven't checked your provider's docs.
  - Close when: in a test, the provider call succeeds, the response is dropped, and the client retries 3 times with the same key. The provider shows exactly one charge, one order row exists, and every retry returns the original order result.

- **F2: A charge must not exist without an order. The unique-constraint failure after the charge turns a successful payment into a 5xx.**
  - Scenario: two concurrent attempts for the same intent both charge. The second insert hits the unique constraint and the server returns 500. The client retries and charges again.
  - Result: the customer is charged with no clear outcome, and the error is retried into more charges.
  - Evidence: you said the insert "sometimes" fails on this race. In this ordering the failure always comes after the money has moved.
  - Consequence: orphan or duplicate charges, and a retry policy that makes each failure worse.
  - Next (correction):
    - Claim the key first. Insert the order or intent row as `pending` under the unique key before charging. The race loser sees the conflict and returns the existing result, or 409/202, without charging.
    - Then charge, then mark the row `paid`.
    - Treat a unique violation on the final write as "already done" and return the stored result. Never surface it as a 5xx.
  - Close when: 10 or more concurrent POSTs with the same key produce exactly one charge, one order row, and the same 2xx body for all of them. No 5xx appears on the conflict path.

- **F3: A charge must not be lost on a crash or failure between the charge and the insert.**
  - Scenario: the charge commits, then the process crashes or the DB is down before the insert.
  - Result: the money is taken and no order record exists. No record means nothing can reconcile it, and a retry without F1's key charges again.
  - Consequence: unrecoverable paid-but-no-order state.
  - Next (design choice): the constraint is that there must be a durable record before the charge. Options are a pending-intent row (covered by F2), or a reconciliation job that matches provider charges, tagged with the key in metadata, against orders. The pending row is the lower-effort path. A reconciliation job also catches provider-side drift.
  - Close when: kill the process between the charge and the insert. After the retry or the reconciler runs, the order exists, with exactly one charge.

- **F4: The retry policy should apply only to safe-to-repeat operations.**
  - Scenario: the client retries every 5xx, including deterministic ones, with no backoff and no reuse of a key.
  - Consequence: this amplifies F1 and F2. Retries should be gated on F1 landing.
  - Next: retry with the same key, add backoff and jitter, and don't retry 4xx. After F1 and F2 land, the F2 conflict path returns 2xx or 409 rather than 5xx.
  - Close when: the client test shows every retry carries the same key, with backoff, and no retries on 4xx.

**Evidence gaps that could change the verdict**
- The provider's idempotency support and its behavior on timeouts. If it has none, F1 relies entirely on your server-side key.
- Whether the charge and the insert share a transaction or a unit of work. They can't atomically, since the provider is external.
- What the unique constraint is on. If it's on a client-supplied value, it may already partly serve as the key.
- Whether any reconciliation or webhook handling exists today.

**Checked and passing**
- Nothing is confirmed as passing, because I had no code or runtime evidence to check.

**Suggested order:** do F1 and F2 together, since the pending-row claim and the idempotency key are one mechanism. Then F4, then F3's reconciliation as a backstop.


===== R4 =====
**Verdict:** CHANGES REQUIRED. Scope: the client retry policy, the `POST /checkout` handler, the payment provider call, and the orders table insert. This is a design-level review of the flow you described. I haven't seen the code, the provider's idempotency support, or the schema, so the claims below are structural only.

**Findings**

- **F1: A retry can charge the card twice.**
  - Requirement: one checkout produces at most one charge.
  - Scenario: the server charges the card successfully → the order insert fails on the unique-constraint race, or the server crashes or times out before it responds → the client sees a 5xx or a timeout → it retries → the handler charges again.
  - Evidence: the flow runs charge, then insert, then respond, with no idempotency key or dedupe check anywhere before the charge. The client retries on both 5xx and timeout. A timeout is ambiguous, because the server may have charged and committed before the response was lost.
  - Consequence: duplicate charges for real customers. The unique-constraint race makes it likelier, because the insert fails after the money has already moved.
  - Next (correction): the client generates one idempotency key per checkout attempt and sends it on every retry. The server stores it, with a unique constraint, before charging. It passes the same key to the provider as the provider's idempotency key. A retry that finds an existing record returns the recorded result and doesn't charge again.
  - Close when: you force a timeout after the charge commits and retry 3 times. The provider shows exactly one charge, and every retry returns the same order and a 200.

- **F2: A failed insert leaves a charge with no order, and nothing recovers it.**
  - Requirement: a charged card must always correspond to a durable order, or be refunded.
  - Scenario: the charge succeeds → the insert fails (the unique race, a DB outage, or a crash) → the handler returns 5xx → the client gives up after 3 tries, or retries into F1.
  - Evidence: the charge and the insert are in different systems with no transaction between them. No compensation step (refund or void) or reconciliation job was described.
  - Consequence: the customer is charged and has no order. Support has no record to find, because there is no row.
  - Next (design choice): the options are (a) insert the order as `pending` before the charge, charge, then mark it `paid`, with a sweeper that reconciles stuck `pending` rows against the provider; (b) authorize first, insert, then capture; or (c) refund on insert failure. Option (a) with idempotency keys fixes F1 and F2 together. Option (c) alone still leaves a window where a crash skips the refund.
  - Close when: you inject an insert failure after a successful charge. The system ends with either a `paid` order or a refunded charge, and no state is left unreconciled after the sweeper runs.

- **F3: The unique-constraint race is treated as a failure instead of as a duplicate.**
  - Requirement: a duplicate-key conflict on the same logical order should be treated as success.
  - Scenario: two concurrent requests for the same cart, such as a double-click or a retry that overlaps a slow first attempt → both charge → one insert wins and the other hits the constraint → that one returns 5xx → the client retries.
  - Evidence: the "sometimes fails on a unique-constraint race" symptom is exactly this overlap. I'm assuming the constraint is on something like a cart ID or order reference. I haven't seen the schema.
  - Consequence: the race that shows up as intermittent failures is really a duplicate-charge source. Retrying the 5xx can't fix it.
  - Next (correction): the idempotency key from F1 serializes the work. Claim the key (insert it) before charging. A concurrent request that loses the claim waits for the winner or returns the winner's result.
  - Close when: you fire 2 to 10 simultaneous identical requests. There is one charge and one order, and every response is a 200 with the same order ID.

**Evidence gaps that could change the verdict**
- Whether the payment provider supports idempotency keys. This decides how F1 is fixed, not whether it's a defect.
- What the unique constraint covers. If it is on a client-supplied ID, the race may already be a retry-or-double-submit signal.
- Whether a reconciliation or refund job already exists outside the flow you described. If it does, F2 shrinks to a latency problem.

**Checked and passing**
- Retrying on timeout and 5xx is reasonable once the server is idempotent. The retry policy is fine on its own; it's unsafe only because the server isn't idempotent.

I haven't run anything. These are traced scenarios from your description, not reproduced failures.
