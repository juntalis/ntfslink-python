"""Compares the ctypes.Structure-based and stdlib-struct-based reparse
buffer codecs' build+parse throughput, to decide which becomes the
maintained pure-Python fallback (see Prompt.md, "Benchmarking to choose
the pure-Python fallback"). Does not touch the filesystem or Win32 at
all — pure in-memory pack/unpack.
"""
import random
import time

from ntfslink import _consts as consts
from ntfslink._pyimpl import buffer_ctypes, buffer_struct

ATTEMPTS = 20_000
random.seed(0)


def _sample():
    seed = random.randrange(0, 3)
    if seed == 0:
        return consts.IO_REPARSE_TAG_MOUNT_POINT, '\\??\\C:\\some\\real\\target\\path\\', \
            'C:\\some\\real\\target\\path\\', 0
    if seed == 1:
        return consts.IO_REPARSE_TAG_SYMLINK, '\\??\\C:\\some\\real\\target\\file.txt', \
            'C:\\some\\real\\target\\file.txt', 0
    return consts.IO_REPARSE_TAG_SYMLINK, 'relative\\target\\file.txt', \
        'relative\\target\\file.txt', consts.SYMBOLIC_LINK_FLAG_RELATIVE


SAMPLES = [_sample() for _ in range(ATTEMPTS)]


def bench_build(codec):
    start = time.perf_counter()
    buffers = [codec.build_reparse_buffer(*s) for s in SAMPLES]
    return time.perf_counter() - start, buffers


def bench_parse(codec, buffers):
    start = time.perf_counter()
    for b in buffers:
        codec.parse_reparse_buffer(b)
    return time.perf_counter() - start


def run(name, codec):
    build_time, buffers = bench_build(codec)
    parse_time = bench_parse(codec, buffers)
    total = build_time + parse_time
    per_op_us = (total / (ATTEMPTS * 2)) * 1e6
    print(f'{name:8s}  build={build_time:.4f}s  parse={parse_time:.4f}s  '
          f'total={total:.4f}s  ~{per_op_us:.2f}us/op')
    return total


if __name__ == '__main__':
    print(f'{ATTEMPTS} samples, run twice each (JIT/cache warmup on first pass)\n')
    for _label in ('warmup', 'measured'):
        print(f'--- {_label} ---')
        ctypes_total = run('ctypes', buffer_ctypes)
        struct_total = run('struct', buffer_struct)
        if struct_total > 0:
            print(f'ctypes/struct ratio: {ctypes_total / struct_total:.2f}x\n')
