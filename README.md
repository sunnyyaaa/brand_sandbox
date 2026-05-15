# brand-sandbox

A minimal two-node + one-derivative BRAND pipeline used as a teaching sandbox.

## What it does

1. `brain_sim` (100 Hz) generates random `focus`, `stress`, `energy` values in [0,1]
   (rounded to 0.1) and writes them to the Redis stream `brain_state`.
2. `state_decoder` reads `brain_state`, applies a rule-based classifier, and
   writes a labeled state (one of `engaged`, `overwhelmed`, `tired`, `distracted`,
   `neutral`) to the Redis stream `decoded_state`. It also logs each decision.
3. `saveBrainState` (derivative) runs on session shutdown and dumps Redis to an
   RDB file via `r.save()`.

## Run it

With the `rt` conda env active and a Redis server reachable:

```bash
supervisor -g ../brand-modules/brand-sandbox/graphs/brain_sandbox.yaml
```

Stop with Ctrl-C; the derivative will fire automatically.

## Inspect Redis afterwards

```bash
redis-cli XLEN brain_state
redis-cli XLEN decoded_state
redis-cli XRANGE decoded_state - + COUNT 5
```

Decode bytes in Python:

```python
import numpy as np
np.frombuffer(b, dtype=np.float32)[0]   # for focus/stress/energy
np.frombuffer(b, dtype=np.uint32)[0]    # for i
b.decode('utf-8')                       # for state
```
