# ntfslink

`ntfslink` is a Windows-only Python package for manipulating NTFS links:

- directory junctions (mount points)
- file and directory symbolic links
- NTFS hard links, including link counts and path enumeration
- filesystem capability checks

The package targets Python 3.8 and later. It uses Win32 APIs through `ctypes`
and optionally provides a compiled C extension for the reparse-buffer codec.

## Requirements

- Windows with an NTFS volume
- Python 3.8 or newer
- Administrator access for some operations, especially hard-link path
    enumeration through the raw NTFS MFT

Junctions can target directories without requiring symbolic-link privileges.
Symbolic links require Windows Vista or later and either
`SeCreateSymbolicLinkPrivilege` or Windows Developer Mode. The package also
supports capability checks for these features.

## Installation

Install from a checkout with:

```text
python -m pip install .
```

The C extension is optional. If it cannot be compiled, installation continues
and the pure-Python backend is used automatically.

For development and tests, install the test dependencies:

```text
python -m pip install -e ".[test]"
python -m pytest
```

The test suite includes unit tests for all backends and Windows-gated
integration tests for real NTFS operations.

## Quick start

```python
import ntfslink

# Create a directory junction.
ntfslink.create_junction(r"C:\data\source", r"C:\data\current")
print(ntfslink.read_link(r"C:\data\current"))
ntfslink.delete_reparse_point(r"C:\data\current")

# Create a symbolic link. Set target_is_directory explicitly when the target
# does not exist yet.
ntfslink.create_symlink(
    r"C:\data\report.txt",
    r"C:\data\latest.txt",
    target_is_directory=False,
)

# Create and inspect hard links.
ntfslink.create_hardlink(r"C:\data\report.txt", r"C:\data\report-copy.txt")
print(ntfslink.hardlink_count(r"C:\data\report.txt"))
print(ntfslink.enumerate_hardlinks(r"C:\data\report.txt"))
```

Link functions accept an optional `backend=` argument, which is useful for
backend-specific testing. Sources and destinations are ordinary path-like
values accepted by the underlying Windows APIs.

## Public API

The main functions are exported from `ntfslink`:

| Function | Purpose |
| --- | --- |
| `create_junction(src, dst)` | Create a directory junction at `dst` targeting `src`. |
| `create_symlink(src, dst, target_is_directory=None)` | Create a file or directory symbolic link. Relative targets are supported. |
| `read_link(path)` | Read the target of a junction or symbolic link. |
| `delete_reparse_point(path)` | Remove a junction or symbolic link and its placeholder. |
| `is_reparse_point(path)` | Check whether a path is a reparse point. |
| `is_junction(path)` / `is_symlink(path)` | Check the specific reparse-point type. |
| `create_hardlink(src, dst)` | Create a hard link to an existing file. NTFS does not support directory hard links. |
| `hardlink_count(path)` | Return the file's NTFS hard-link count. |
| `enumerate_hardlinks(path)` | Return paths for every hard link to the file. |

Capability queries are available under `ntfslink.supports`:

```python
ntfslink.supports.hardlinks(path)
ntfslink.supports.reparse_points(path)
ntfslink.supports.junctions(path)
ntfslink.supports.symlinks(path)
```

A missing `path` asks for the platform-level default. Hard links are treated
as supported on older Windows versions because NTFS has supported them since
Windows 2000; newer systems can be checked using the volume capability flag.

Invalid source and destination paths raise `InvalidTargetError` and
`InvalidLinkError`, respectively. These, along with `InvalidHandleError`, are
available from `ntfslink.exceptions`.

## Backends

Backend selection is automatic by default:

1. `cext` when the optional extension is importable
2. the maintained `struct` pure-Python fallback otherwise

Set `NTFSLINK_BACKEND` to select a backend explicitly:

```text
NTFSLINK_BACKEND=auto      # default
NTFSLINK_BACKEND=cext
NTFSLINK_BACKEND=struct
NTFSLINK_BACKEND=ctypes    # compatibility/regression backend
```

The active backend can be inspected with:

```python
ntfslink.active_backend()
ntfslink.available_backends()
```

The C extension and pure-Python implementations share the same reparse-buffer
format and high-level behavior. The `struct` codec is the maintained fallback;
the `ctypes` codec remains available for regression testing.

## Hard-link enumeration

Hard-link creation uses the long-standing `CreateHardLinkW` API. Enumeration
uses NTFS file records (`FSCTL_GET_NTFS_FILE_RECORD`) and reconstructs each
linked path from MFT filename attributes. This avoids making the Vista-only
`FindFirstFileNameW`/`FindNextFileNameW` APIs a requirement, so the design
supports the Windows XP SP2 hard-link baseline.

Opening a volume handle for MFT queries generally requires an elevated
process. On systems where that access is unavailable, enumeration raises an
OS-level error rather than being silently incomplete. Enumeration is intended
for individual files, not bulk MFT scanning.

## Project layout

- `src/ntfslink/`: public API, backend dispatcher, Win32 implementations, and buffer codecs
- `tests/`: unit and Windows integration tests
- `benchmarks/`: codec benchmark and the fallback-backend decision
- `build/`: local build output; it is not the package source

## License and credits

The implementation is derived in part from research and ideas in
[reparselib](https://github.com/amdf/reparselib), Windows API documentation,
and the hard-link enumeration discussion credited by the original project.

See the [project repository](https://github.com/juntalis/ntfslink-python) for
source, issues, and development history.
