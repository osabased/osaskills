# control-sort

Question asked:

> I sort a list of order records by priority with `sorted(orders, key=lambda o: o.priority)`. Orders with the same priority must stay in the order they arrived. Should I add the arrival index to the key as a tie-breaker?

## R1

No, you don't need to. Python's `sorted()` and `list.sort()` are guaranteed to be **stable**: items with equal keys keep the order they had in the input. So if `orders` is already in arrival order, `sorted(orders, key=lambda o: o.priority)` keeps same-priority orders in arrival order.

This holds even with `reverse=True`. Python doesn't sort and then flip the list, so ties stay in their original order. `key=lambda o: -o.priority` is also safe.

**When a tie-breaker does make sense:**

- **The list might not be in arrival order.** For example, it was built from a set or dict of mixed origin, from a database query without `ORDER BY`, from merged sources, or from parallel workers. Stability only keeps whatever order the input had. In that case, don't use `enumerate` on the list, because that just records the current, possibly wrong, order. Use a real arrival field: `key=lambda o: (o.priority, o.received_at)` or a sequence number.
- **You want the intent to be explicit.** A key like `(o.priority, o.seq)` documents the requirement and keeps working if someone later switches to a sort that isn't stable, such as some database or pandas sorts. A short comment like `# stable sort keeps arrival order within a priority` works too.
- **The data isn't sorted by Python.** If the ordering really happens in SQL, pandas, or another language, check that tool's stability guarantee. For example, pandas `sort_values` is only stable with `kind="stable"` (or `"mergesort"`), and SQL guarantees no order for ties unless you add a column.

If the list arrives in order and Python does the sorting, your current code is correct as it is.

## R2

## Think tank: arrival-index tie-breaker for a stable sort
opus, sonnet, sonnet · session effort · identical brief · debate skipped at 3–0

### Recommendation (3–0)
Don't add the index. Python's `sorted()` is guaranteed stable, so orders with the same priority already come out in the order they went in. Adding the index produces the same result. It costs a tuple per element, and it needs `arrival_index` to be stored on each order (as `o.arrival_index`), or set up through `enumerate`, before the lambda can use it.

The panel's one condition is that the list has to be in arrival order before you sort it. A stable sort keeps whatever order the input has. If `orders` comes from a set, a merge of several sources, or a SQL query with no `ORDER BY`, that order isn't arrival order. Then you need a real arrival sequence number or timestamp stored on each record, and the list position won't do.

All three panelists added the same points:
- `reverse=True` is still stable.
- `list(reversed(sorted(...)))` is not: it flips the tied orders too.
- A one-line comment like `# relies on sorted() stability to keep arrival order` makes the intent clear without changing the key.

Checked: the Python Sorting HOWTO says "Sorts are guaranteed to be stable… when multiple records have the same key, their original order is preserved." It also says "The *reverse* parameter still maintains sort stability." Both claims the recommendation rests on are confirmed.

### Panel
- **A** (opus): "No. Python's `sorted()` and `list.sort()` are guaranteed stable, so orders with equal priority already keep their relative order. Only add the arrival index if the input list is *not* already in arrival order. In that case the index is required, not just a tie-breaker." High confidence.
- **B** (sonnet): "No, the tie-breaker isn't needed. Python's `sorted` is guaranteed stable, so records with equal priority keep their relative input order. That holds as long as `orders` is already in arrival order." High confidence.
- **C** (sonnet): "No, the arrival index isn't needed. Python's `sorted` is guaranteed stable, so orders with equal priority keep their relative input order. Keep `key=lambda o: o.priority`." High confidence.

### Where they split
They agree on the recommendation. One detail is wrong: C says that negating the key would flip tied orders. It doesn't. With `key=lambda o: -o.priority`, tied orders still have equal keys, so they stay in arrival order. C's own next sentence recommends `-o.priority`, which is fine. Only reversing the sorted list afterwards flips the ties.

### My take
I agree, and the panel didn't move me from my starting view. For your code the answer is no. The thing to confirm is whether `orders` really is in arrival order when you sort it. If you can't guarantee that, the fix is a stored sequence number, not the index from `enumerate`.

A and B made a good point about the future. If this code ever moves to `heapq` or `queue.PriorityQueue`, you'll need a tie-breaker, because those aren't stable. The usual form is `(priority, next(counter), order)` with `counter = itertools.count()`. Without the counter, two orders with the same priority get compared to each other directly, which can raise a `TypeError`.

## R3

**Position:** Don't add it. Python's `sorted` is guaranteed stable, so orders with equal priority keep their input order. The tie-breaker only matters if `orders` isn't already in arrival order, or if the sort is reversed in a way that breaks the guarantee.

**Reasoning:**
- The Python docs (Sorting HOWTO, and the `sorted`/`list.sort` reference) state that sorting is guaranteed stable. Records that compare equal on the key keep their original relative order. This is a language guarantee, not a CPython implementation detail.
- If `orders` is already in arrival order, `sorted(orders, key=lambda o: o.priority)` already does what is needed. Adding `arrival_index` is redundant and adds a variable that has to be kept correct.
- `reverse=True` also preserves the original order of equal elements. The docs say it keeps stability as if each comparison were reversed. If you want descending priority with ties still in arrival order, `reverse=True` is correct. Don't negate the key and don't reverse the list afterward. Reversing the list afterward would flip the ties.
- The tuple key is not harmful. It is just unnecessary and can introduce bugs. If `arrival_index` is a separate variable, not an attribute, the lambda would capture a single stale value. The key would be the same for every record, or it would raise `NameError`. It would need `enumerate`, which makes the code more complicated.

**When the answer changes (add an explicit tiebreaker):**
- `orders` is not in arrival order when it reaches the sort. Examples are a `set`, results from an unordered query, a merge of several sources, or a dict built from unordered data. In that case the input position is not the arrival order, and you need a real arrival timestamp or sequence number on each record. Sort on `(o.priority, o.seq)`.
- The sort is done in a way that is not stable, for example by a database `ORDER BY priority` without a secondary column. SQL does not guarantee tie order. Python's stability does not help there.
- `priority` has mixed or unorderable types, for example `None` alongside ints. That is a different failure (`TypeError`) which a tie-breaker does not fix.
- You want the code to document its intent or to stay correct if someone later changes the input source. A tiebreaker on a real field like `o.created_at` or `o.seq` is a defensible choice for explicitness. A comment is cheaper.

**Concrete suggestion:**
```python
# sorted() is stable: equal priorities keep their input (arrival) order.
by_priority = sorted(orders, key=lambda o: o.priority)
```
If the input order isn't guaranteed to be arrival order, use a stored field, not a positional index:
```python
by_priority = sorted(orders, key=lambda o: (o.priority, o.seq))
```
If you only have positions, `enumerate` is the way to get them, but this only helps if the list order really is arrival order, in which case stability already covers it.

**Risks and unknowns:** I can't see how `orders` is built. If it is not in arrival order, my recommendation flips. I answered from the documented stability guarantee and did not re-fetch the docs in this session.

**Confidence:** High on the stability guarantee, medium on the recommendation as a whole, because it depends on how `orders` is built.

**Position:** Don't add the arrival index. `sorted` is guaranteed stable, so ties keep their input order, provided `orders` is already in arrival order. If it isn't, add a stored sequence field instead.

**Confidence:** High on the stability guarantee, medium on the recommendation as a whole.

## R4

No, you don't need it. Python's `sorted()` and `list.sort()` are guaranteed stable, so records with equal keys keep their original relative order. If `orders` is already in arrival order, `sorted(orders, key=lambda o: o.priority)` keeps same-priority orders in arrival order.

**Points to check:**

- **`reverse=True` is still stable.** `sorted(orders, key=..., reverse=True)` keeps equal elements in their original order; it doesn't reverse them. Negating the key (`key=lambda o: -o.priority`) also keeps the order.
- **This only works if the input list is in arrival order.** If `orders` came from a set, an unordered query, a dict built in some other order, or a merge of several sources, stability just preserves that wrong order. In that case, sort by an arrival field such as `key=lambda o: (o.priority, o.arrival_ts)`.
- **Other sorting methods may not be stable.** `heapq` isn't stable, and neither is SQL `ORDER BY priority` without a second column. pandas `sort_values` is only stable with `kind="stable"` (or `"mergesort"`). For a priority queue, add a counter: `heapq.heappush(h, (o.priority, next(counter), o))`.

**When an explicit tie-breaker is still worth it:** if the order really matters, for example for fairness or auditing, adding a timestamp or sequence number to the key makes the rule visible in the code. It also keeps working if someone later replaces the in-memory sort with a database query or a heap. If the plain `sorted()` call stays, a one-line comment like `# relies on sort stability to keep arrival order` does the same job.

## R5

**Position:** No, the arrival index isn't needed. Python's `sorted` is guaranteed stable, so orders with equal priority keep their relative input order. Keep `key=lambda o: o.priority`.

**Reasoning:**
- The Python docs (Sorting HOWTO and the `list.sort` reference) say sort stability is guaranteed. Records with equal keys retain their original relative order. This has held since Python 2.3 (Timsort), and the docs have documented it as a guarantee for years, so it isn't a CPython implementation detail.
- `sorted()` is stable in the same way as `list.sort()`. It copies the iterable into a list and sorts that.
- The key function is called once per element. Elements are compared only by their key values, so equal priorities compare as equal and stability keeps their original positions.
- An `arrival_index` tie-breaker would be redundant. It would also add a tuple allocation per element and a slightly slower comparison, and it would imply the code doesn't trust a documented guarantee.

**Conditions and caveats:**
- "Arrival order" has to equal the list's current order. If `orders` is already in arrival order, for example appended as orders came in, then stability is enough. If the list was shuffled or rebuilt earlier, for example from a set, a dict keyed by something else, or a merge of multiple sources, then the list order isn't arrival order. In that case, sort by an explicit arrival timestamp or sequence number stored on the record, such as `(o.priority, o.arrival_ts)`. That is a data fix, not a stability fix.
- If the order objects already carry a real arrival index, using it as a tie-breaker is harmless and makes the intent explicit. It also survives later re-sorting or re-ordering of the list. It's optional, not required.
- `reverse=True` also preserves stability. Equal elements keep their original order, as if the reverse flag weren't applied to ties. If you instead negate the key, or sort ascending and then call `reversed()`, ties would flip. For descending priority use `reverse=True` or `-o.priority`, not `list(reversed(sorted(...)))`.
- If `priority` can be `None` or mixed types, the sort raises `TypeError`. That is a separate problem from tie-breaking.
- If priority is a float, NaN values break the total ordering and can produce inconsistent results.
- Add a short comment, such as "stable sort preserves arrival order", so a future reader doesn't "fix" it or remove the reliance.
- A test with a few equal-priority orders would lock in the behavior.

**Confidence:** High. Stability of `sorted` is an explicitly documented guarantee. The one real uncertainty is whether the input list is actually in arrival order, which I can't see from the code shown.

## R6

## Think tank: arrival-index tie-breaker for a stable sort
opus, sonnet, sonnet · session effort · identical brief · debate skipped at 3–0

### Recommendation (3–0)
Don't add the tie-breaker. Python's `sorted()` is guaranteed to be stable, so orders with equal `priority` keep the order they had in the input list. If `orders` is already in arrival order, your current one-line key does what you need. Taking a position from `enumerate` at sort time would only repeat what stability already gives you.

What all three see as the real risk is whether the list order actually is the arrival order. It might not be if `orders` comes from:
- a `set`
- a database query with no `ORDER BY`
- results merged from several workers
- an earlier sort

In those cases a positional index won't help either. Store a real sequence number or timestamp on each order and sort by `(o.priority, o.seq)`.

The panel also agreed on these points:
- `reverse=True` still keeps ties in arrival order. Writing `[::-1]` or `reversed()` after the sort would flip the ties.
- Stability is lost if the sort moves out of Python's `sorted`. SQL `ORDER BY` doesn't guarantee tie order, and pandas `sort_values` needs `kind="stable"`.
- Write a comment saying the code relies on stability.

Checked: the Python Sorting HOWTO says "Sorts are guaranteed to be stable. That means that when multiple records have the same key, their original order is preserved." It also says "The *reverse* parameter still maintains sort stability (so that records with equal keys retain the original order)." Both facts the recommendation rests on are confirmed.

### Panel
- **A** (opus): "Don't add an index tie-breaker, because `sorted()` is guaranteed stable and already keeps arrival order for equal priorities; use an explicit stored `arrival_seq` key only if the list isn't guaranteed to be in arrival order." High.
- **B** (sonnet): "Don't add the tie-breaker. `sorted` is stable, so the existing key already keeps arrival order, provided `orders` is already in arrival order." High.
- **C** (sonnet): "Don't add the arrival index. `sorted` is guaranteed stable, so ties keep their input order, provided `orders` is already in arrival order. If it isn't, add a stored sequence field instead." High on the stability guarantee, medium on the recommendation as a whole.

### My take
I agree, and the panel didn't move me from where I started: you don't need the tie-breaker, as long as the list really is in arrival order.

A and C both pointed out that `lambda o: (o.priority, arrival_index)` uses one shared variable, so every order would get the same tie-break value. That critique is aimed at the example I wrote in the brief, not at your code, because you never said how you'd write it. Their point still holds: a positional index would have to come from `enumerate`, and that is just extra code.

What I'd actually do:
- Keep the current key.
- Add a comment saying it relies on `sorted` being stable.
- Add a test with two orders of equal priority (A's idea), so a later refactor can't silently break the order.

One case the panel didn't raise: if you ever switch to a priority queue with `heapq`, it is *not* stable. Then you'd need the `(priority, seq)` tuple, which also stops Python from trying to compare two order records when their priorities are equal.

## R7

**Position:** Don't add the tie-breaker if `orders` is already in arrival order. Python's sort is guaranteed stable, so `sorted(orders, key=lambda o: o.priority)` already keeps orders that share a priority in arrival order. Add an explicit arrival key only if the list's order isn't actually arrival order.

**Reasoning:**
- **The docs guarantee it.** The Python Sorting HOWTO (https://docs.python.org/3/howto/sorting.html) says: "Sorts are guaranteed to be stable. That means that when multiple records have the same key, their original order is preserved." The `sorted()` reference says the same. This is a promise of the language, not a side effect of how CPython happens to sort, so you can rely on it.
- **`reverse=True` keeps it.** The same page says "The *reverse* parameter still maintains sort stability." If they want the highest priority first, `sorted(orders, key=lambda o: o.priority, reverse=True)` still keeps ties in arrival order. Writing `sorted(...)[::-1]` or `reversed(sorted(...))` instead would flip the ties too.
- **The proposed code has a bug.** In `key=lambda o: (o.priority, arrival_index)`, the name `arrival_index` isn't tied to each order. It's one free variable, so every key gets the same value. That tie-breaker would do nothing, or raise `NameError` if the name isn't defined. A working version would need `enumerate`:
  ```python
  [o for _, o in sorted(enumerate(orders), key=lambda p: (p[1].priority, p[0]))]
  ```
  That is more code to get the result stability already gives you.
- **The real question is where the order comes from.** Stability keeps the order the list is in, not the order the orders arrived. The plain sort is only correct if `orders` really is in arrival order. Here are cases where it isn't:
  - it was built from a `set`
  - it came from a database query with no `ORDER BY`
  - it was merged from concurrent workers or several sources
  - it was re-sorted somewhere earlier
  - it was deserialized from a source with no defined order

  In those cases an index from `enumerate` doesn't help either, because it just numbers an order that is already wrong. What you need is a real arrival field, such as a sequence number or a monotonic timestamp:
  ```python
  sorted(orders, key=lambda o: (o.priority, o.arrival_seq))
  ```

**Recommendation:** Keep the one-line key. Add a comment such as `# sorted() is stable: equal priorities keep arrival order`. Add a test with two orders of equal priority so a later refactor can't quietly break the order. If the arrival order matters for business reasons and the list's order isn't guaranteed where it's built, store an arrival sequence number on each order and sort by `(priority, arrival_seq)`.

**Risks and unknowns:**
- The main assumption is that `orders` is in arrival order when it gets sorted. We don't know how it's built.
- If `priority` holds values that don't order consistently, sorting is unreliable whatever the tie-breaker. Examples are NaN floats, or a mix of `None` and numbers, which raises `TypeError`.
- If the sort later moves into a database query or another language, stability is no longer guaranteed. A pandas sort with the default quicksort isn't stable unless you pass `kind="stable"`, and SQL `ORDER BY` isn't stable either. Then an explicit tie-breaker would be needed.
- What would change my mind: evidence that the list doesn't arrive in arrival order, or that the sort runs somewhere other than Python's `list.sort`/`sorted`.

**Confidence:** High. Stability is documented and guaranteed. What's left uncertain is how `orders` is built, which the brief doesn't say.

Position: Don't add an index tie-breaker, because `sorted()` is guaranteed stable and already keeps arrival order for equal priorities; use an explicit stored `arrival_seq` key only if the list isn't guaranteed to be in arrival order.
Confidence: High

## R8

**Position:** No, the tie-breaker isn't needed. Python's `sorted` is guaranteed stable, so records with equal priority keep their relative input order. That holds as long as `orders` is already in arrival order.

**Reasoning:**
- The Python docs (Sorting HOWTO and the `list.sort` docs) say sorts are guaranteed stable. Records that compare equal keep their original relative order. This has been a language guarantee since Python 2.3, not an implementation accident of CPython's Timsort.
- With `key=lambda o: o.priority`, two orders with equal priority have equal keys, so they count as equal and stay in input order. The result is exactly the requirement.
- Adding `arrival_index` is harmless but redundant. It adds a field to maintain, and it can hide the real dependency, which is that the input list must be in arrival order.
- `reverse=True` also preserves stability. Equal elements keep their original order, not the reversed one. If the developer wants descending priority with ties still in arrival order, `sorted(..., key=..., reverse=True)` does that correctly. Negating the key is unnecessary. Don't reverse the list afterward, because that would flip the ties.

**Conditions and assumptions:**
- `orders` must already be in arrival order when it is sorted. If it comes from a set, from a dict built in some other order, or from a merge of concurrent sources, the list order isn't arrival order. Then an explicit arrival index or timestamp is needed, and it should be a real sequence number, not the list position.
- `o.priority` must be a consistently comparable type. Mixing `None` and ints would raise `TypeError`. That is a separate issue from stability.
- If the code later switches to a different mechanism, such as `heapq`, a `PriorityQueue`, or a database `ORDER BY`, stability is no longer guaranteed. `heapq` and `PriorityQueue` are not stable, so the index tie-breaker would be required there. `ORDER BY` in SQL also gives no stability guarantee without an explicit secondary key.
- Floating-point NaN priorities break ordering assumptions, though that is an edge case.

**Caveats:**
- If you want the requirement to be explicit and robust to future refactors, a short comment such as "stable sort preserves arrival order" is cheaper than carrying an index. A test with equal-priority records covers it too.
- An explicit tie-breaker is reasonable if the code may be ported or the list's ordering is not controlled locally. In plain `sorted` on an arrival-ordered list, it's unnecessary.

**Confidence:** High. Stability of `sorted` and `list.sort` is documented behavior. The remaining uncertainty is whether the input list is really in arrival order, which I can't see from the snippet.

## R9

**Position:** No. Python's `sorted()` and `list.sort()` are guaranteed stable, so orders with equal priority already keep their relative order. Only add the arrival index if the input list is *not* already in arrival order. In that case the index is required, not just a tie-breaker.

**Reasoning:**
- **Stability is guaranteed by the language.** It isn't just how CPython happens to behave. The Python docs (Sorting HOW-TO, "Sort Stability and Complex Sorts", and the `sorted()` entry under Built-in Functions) say: "The built-in sorted() function is guaranteed to be stable. A sort is stable if it guarantees not to change the relative order of elements that compare equal." Timsort/Powersort keeps this guarantee, and the docs suggest using it for multi-pass sorts.
- **`reverse=True` stays stable too.** Equal elements keep their original order. They are not flipped. So `sorted(orders, key=lambda o: o.priority, reverse=True)` is still safe. Calling `reversed(sorted(...))` is not, because it reverses the ties as well.
- **The tie-breaker adds nothing here.** With `(o.priority, arrival_index)`, the second element only matters on ties, and on ties stability already gives the same result. It also costs a tuple per element. And as written the lambda can't see `arrival_index` unless it's an attribute on the order (`o.arrival_index`) or you go through `enumerate`. The simple version has no such plumbing to get wrong.

**Conditions and caveats (when the index is needed):**
1. **The list isn't in arrival order.** Stability keeps the *input* order, not arrival order. If `orders` comes from a set, from merging several queues, from a database query without `ORDER BY`, from a concurrent producer, or from an earlier sort on some other field, then the input order is not arrival order. You then need a real arrival timestamp or sequence number in the key. This is the assumption my answer depends on most.
2. **The code later moves to a structure that isn't stable.** `heapq` and `queue.PriorityQueue` are not stable, and on ties they fall back to comparing the order objects themselves, which can raise `TypeError`. The standard fix is `(priority, counter, order)` using `itertools.count()`. SQL `ORDER BY priority` and many sorts in other languages (C++ `std::sort`, JS engines before ES2019) don't guarantee stability either.
3. **Documenting intent.** Some teams want an explicit tie-breaker so the requirement survives refactoring. That's reasonable, but a comment such as `# relies on sorted() stability to preserve arrival order` does the same job at no cost. If you do add the key, use a real stored sequence number, not an index reconstructed after the fact.

**Risks and unknowns:** I can't see how `orders` is built. If it isn't strictly in arrival order (point 1), my "no" becomes "yes, and use a real arrival sequence number".

**Confidence:** High. Stability is a documented language guarantee. The remaining uncertainty is only about where the input list comes from.

## R10

**Position:** Don't add it. Python's `sorted` is guaranteed stable, so orders with equal priority keep their input order. The tie-breaker only matters if `orders` is not already in arrival order, or if `priority` can't be compared normally.

**Reasoning:**
- The Python docs (Sorting HOWTO, and the `list.sort` / `sorted` reference) say sorts are guaranteed stable. Records that compare equal keep their original relative order. This has been guaranteed since Python 2.3 and holds in every current CPython and PyPy.
- With `key=lambda o: o.priority`, two orders with equal priority have equal keys. Stability then keeps them in the order they appeared in the input. If `orders` is iterated in arrival order, the existing code already does what's required.
- Adding `arrival_index` is redundant in that case. It also adds a failure mode: `arrival_index` has to exist and be correct, and it adds a little overhead.
- The one real difference is intent. A tie-breaker makes the rule explicit and doesn't depend on a reader knowing about stability. If you want that, a short comment is cheaper: `# sorted() is stable: ties keep arrival order`.

**When the answer changes (add the tie-breaker, or sort differently):**
1. `orders` isn't in arrival order when sorted. Examples are a `set`, a dict keyed by something else, results merged from several sources or threads, or a DB query with no `ORDER BY`. Then stability preserves the wrong order. The fix is to sort on a real arrival field such as a sequence number or timestamp, e.g. `key=lambda o: (o.priority, o.seq)`. Enumerating the list at sort time would just bake in the current, possibly wrong, order.
2. You use `reverse=True` for highest priority first. Python preserves stability even then, because ties keep their original order and are not flipped. So it still works. Don't "fix" it by negating the key unless you need to.
3. `priority` can be `None`, mixed types, or NaN floats. These cause a `TypeError` or inconsistent ordering. Equal-looking keys may not behave as ties, and NaN breaks sort invariants. A tie-breaker doesn't fix this. Normalize the priority first.
4. The sort moves out of Python, for example to SQL, pandas (`sort_values` defaults to quicksort, which isn't stable, so you need `kind="stable"`), or NumPy. Then stability is not automatic.
5. `priority` is a custom object with a weird `__lt__`. Python only uses `<`, so equality isn't tested directly. Ties are whatever isn't less than in either direction. This is fine for sane types.

**Concrete suggestion:**
```python
# sorted() is stable, so equal priorities keep their input (arrival) order
by_priority = sorted(orders, key=lambda o: o.priority)
```
If arrival order isn't guaranteed in `orders`, use an explicit stored sequence number instead: `key=lambda o: (o.priority, o.seq)`.

**Risks and unknowns:** The answer depends mostly on `orders` being in arrival order, which I can't see. I'm also assuming `priority` is a normal comparable type, such as an int.

**Confidence:** High on the stability guarantee and on not needing the tie-breaker when input is in arrival order. Medium overall, because the input's ordering is unknown.

**Position:** Don't add the tie-breaker. `sorted` is stable, so the existing key already keeps arrival order, provided `orders` is already in arrival order.

**Confidence:** High

## R11

No, you don't need it. Python's `sorted()` and `list.sort()` are **guaranteed stable**: items with equal keys keep their original relative order. The language docs promise this, so it isn't an implementation detail. If `orders` is already in arrival order, this works as is:

```python
sorted(orders, key=lambda o: o.priority)
```

Adding `enumerate` indices to the key would make the sort slower and harder to read without changing the result.

**When you would need a tie-breaker:** stability keeps whatever order the input has. If `orders` might not be in arrival order, add a tie-breaker. That can happen if the list was built from a set, merged from several sources, or loaded from a database query with no `ORDER BY`. In that case, use a real arrival field, not the list position:

```python
sorted(orders, key=lambda o: (o.priority, o.arrived_at))
```

**Two smaller points:**
- `reverse=True` also keeps equal items in their original order, so `sorted(orders, key=lambda o: o.priority, reverse=True)` still keeps ties in arrival order.
- If this rule matters to the business, write a short test with two same-priority orders. That way a later change, such as moving the sort into SQL or a different language, can't silently break it.
