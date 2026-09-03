# Buffer codec benchmark results

`python benchmarks/bench_backends.py`, 20,000 samples (mixed junction /
absolute symlink / relative symlink), Python 3.13.7, x64:

```
ctypes    build=0.0244s  parse=0.0254s  total=0.0498s  ~1.24us/op
struct    build=0.0134s  parse=0.0196s  total=0.0330s  ~0.83us/op
ctypes/struct ratio: 1.51x
```

**Decision: `struct` is the maintained `auto`-mode pure-Python fallback**
(see `backend.py`'s `_resolve`). It's consistently ~1.5x faster than the
`ctypes.Structure`-based codec, matching the general expectation that
`struct.pack`/`unpack_from` (one precompiled C loop over the whole format)
beats `ctypes.Structure` (per-field descriptor dispatch plus an extra
allocation+copy to get `bytes()` out of an instance) for small, flat,
fixed-shape binary structures. In absolute terms both are low-single-digit
microseconds per operation — this only matters at all because junction/
symlink creation and reads happen once per call, not in a hot loop.

The `ctypes`-based codec (`_pyimpl/buffer_ctypes.py`) is kept and fully
tested rather than deleted, since it's still selectable via
`NTFSLINK_BACKEND=ctypes` for regression testing and as a fallback of last
resort if a future `struct`-specific bug ever needs isolating.
