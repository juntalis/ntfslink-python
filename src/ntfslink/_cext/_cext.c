/*
 * C-extension backend: same primitive-operation surface as
 * ntfslink/_pyimpl/backend.py (build_reparse_buffer, set_reparse_point,
 * create_hard_link, get_ntfs_file_record, ...), implemented natively for
 * performance. Strict C89: every declaration precedes any statement in
 * its block, and 64-bit values use the Windows SDK's LONGLONG/ULONGLONG
 * typedefs rather than the C99 "long long" keyword, so no C99 extension
 * is needed anywhere in this file.
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <windows.h>
#include <winioctl.h>
#include <string.h>

/* The FSCTL_ and IO_REPARSE_TAG_ constants come from winioctl.h/winnt.h
 * (pulled in above) - don't redefine them here, that just produces
 * macro-redefinition warnings and risks drifting from the SDK's own
 * values. */

#define MAX_REPARSE_BUFFER_SIZE (16 * 1024)
#define FILE_FLAG_REPARSE_BACKUP (FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS)

#pragma pack(push, 1)
typedef struct {
    ULONG ReparseTag;
    USHORT ReparseDataLength;
    USHORT Reserved;
} ReparseHeader;

typedef struct {
    USHORT SubstituteNameOffset;
    USHORT SubstituteNameLength;
    USHORT PrintNameOffset;
    USHORT PrintNameLength;
} MountPointBufferHeader;

typedef struct {
    USHORT SubstituteNameOffset;
    USHORT SubstituteNameLength;
    USHORT PrintNameOffset;
    USHORT PrintNameLength;
    ULONG Flags;
} SymlinkBufferHeader;
#pragma pack(pop)

static PyObject *
set_error_from_lasterror(void)
{
    PyErr_SetFromWindowsErr((int)GetLastError());
    return NULL;
}

/* ---------------------------------------------------------------------
 * build_reparse_buffer(tag, subst_name, print_name, flags=0) -> bytes
 * --------------------------------------------------------------------- */
static PyObject *
cext_build_reparse_buffer(PyObject *self, PyObject *args)
{
    unsigned long tag;
    unsigned long flags;
    PyObject *subst_obj;
    PyObject *print_obj;
    Py_ssize_t subst_chars;
    Py_ssize_t print_chars;
    wchar_t *subst_w;
    wchar_t *print_w;
    size_t subst_bytes;
    size_t print_bytes;
    unsigned char buf_header[sizeof(SymlinkBufferHeader)];
    size_t buf_header_size;
    unsigned char *path_buffer;
    size_t path_buffer_size;
    ReparseHeader header;
    Py_ssize_t total;
    PyObject *result;
    char *out;

    flags = 0;
    path_buffer = NULL;

    if (!PyArg_ParseTuple(args, "kUU|k", &tag, &subst_obj, &print_obj, &flags))
        return NULL;

    subst_w = PyUnicode_AsWideCharString(subst_obj, &subst_chars);
    if (!subst_w)
        return NULL;
    print_w = PyUnicode_AsWideCharString(print_obj, &print_chars);
    if (!print_w) {
        PyMem_Free(subst_w);
        return NULL;
    }

    subst_bytes = (size_t)subst_chars * sizeof(wchar_t);
    print_bytes = (size_t)print_chars * sizeof(wchar_t);

    if (tag == IO_REPARSE_TAG_MOUNT_POINT) {
        MountPointBufferHeader h;
        h.SubstituteNameOffset = 0;
        h.SubstituteNameLength = (USHORT)subst_bytes;
        h.PrintNameOffset = (USHORT)(subst_bytes + sizeof(wchar_t));
        h.PrintNameLength = (USHORT)print_bytes;
        buf_header_size = sizeof(h);
        memcpy(buf_header, &h, buf_header_size);

        /* Windows' own junctions put a null wchar between the substitute
         * and print names *and* a trailing one after the print name (not
         * counted in PrintNameLength) - match that exactly for interop
         * with junctions created/read by other tools. */
        path_buffer_size = subst_bytes + sizeof(wchar_t) + print_bytes + sizeof(wchar_t);
        path_buffer = (unsigned char *)PyMem_Malloc(path_buffer_size ? path_buffer_size : 1);
        if (!path_buffer) {
            PyMem_Free(subst_w);
            PyMem_Free(print_w);
            return PyErr_NoMemory();
        }
        memcpy(path_buffer, subst_w, subst_bytes);
        memset(path_buffer + subst_bytes, 0, sizeof(wchar_t));
        memcpy(path_buffer + subst_bytes + sizeof(wchar_t), print_w, print_bytes);
        memset(path_buffer + subst_bytes + sizeof(wchar_t) + print_bytes, 0, sizeof(wchar_t));
    } else if (tag == IO_REPARSE_TAG_SYMLINK) {
        SymlinkBufferHeader h;
        h.SubstituteNameOffset = 0;
        h.SubstituteNameLength = (USHORT)subst_bytes;
        h.PrintNameOffset = (USHORT)subst_bytes;
        h.PrintNameLength = (USHORT)print_bytes;
        h.Flags = (ULONG)flags;
        buf_header_size = sizeof(h);
        memcpy(buf_header, &h, buf_header_size);

        path_buffer_size = subst_bytes + print_bytes;
        path_buffer = (unsigned char *)PyMem_Malloc(path_buffer_size ? path_buffer_size : 1);
        if (!path_buffer) {
            PyMem_Free(subst_w);
            PyMem_Free(print_w);
            return PyErr_NoMemory();
        }
        memcpy(path_buffer, subst_w, subst_bytes);
        memcpy(path_buffer + subst_bytes, print_w, print_bytes);
    } else {
        PyMem_Free(subst_w);
        PyMem_Free(print_w);
        PyErr_Format(PyExc_NotImplementedError, "Unsupported reparse tag: 0x%08lX", tag);
        return NULL;
    }

    PyMem_Free(subst_w);
    PyMem_Free(print_w);

    header.ReparseTag = (ULONG)tag;
    header.ReparseDataLength = (USHORT)(buf_header_size + path_buffer_size);
    header.Reserved = 0;

    total = (Py_ssize_t)(sizeof(header) + buf_header_size + path_buffer_size);
    result = PyBytes_FromStringAndSize(NULL, total);
    if (!result) {
        PyMem_Free(path_buffer);
        return NULL;
    }
    out = PyBytes_AS_STRING(result);
    memcpy(out, &header, sizeof(header));
    memcpy(out + sizeof(header), buf_header, buf_header_size);
    memcpy(out + sizeof(header) + buf_header_size, path_buffer, path_buffer_size);
    PyMem_Free(path_buffer);
    return result;
}

/* ---------------------------------------------------------------------
 * parse_reparse_buffer(data: bytes-like) -> (tag, flags, subst_name, print_name)
 * --------------------------------------------------------------------- */
static PyObject *
cext_parse_reparse_buffer(PyObject *self, PyObject *args)
{
    Py_buffer buf;
    const unsigned char *data;
    ReparseHeader header;
    USHORT so, sl, po, pl;
    ULONG flags;
    size_t path_offset;
    int ok;
    PyObject *subst_name;
    PyObject *print_name;

    so = 0; sl = 0; po = 0; pl = 0;
    flags = 0;
    path_offset = 0;
    ok = 1;

    if (!PyArg_ParseTuple(args, "y*", &buf))
        return NULL;

    if (buf.len < (Py_ssize_t)sizeof(ReparseHeader)) {
        PyBuffer_Release(&buf);
        PyErr_SetString(PyExc_ValueError, "Buffer too small for a reparse point header");
        return NULL;
    }

    data = (const unsigned char *)buf.buf;
    memcpy(&header, data, sizeof(header));

    if (header.ReparseTag == IO_REPARSE_TAG_MOUNT_POINT) {
        MountPointBufferHeader h;
        if (buf.len < (Py_ssize_t)(sizeof(header) + sizeof(h))) {
            ok = 0;
        } else {
            memcpy(&h, data + sizeof(header), sizeof(h));
            so = h.SubstituteNameOffset; sl = h.SubstituteNameLength;
            po = h.PrintNameOffset; pl = h.PrintNameLength;
            path_offset = sizeof(header) + sizeof(h);
        }
    } else if (header.ReparseTag == IO_REPARSE_TAG_SYMLINK) {
        SymlinkBufferHeader h;
        if (buf.len < (Py_ssize_t)(sizeof(header) + sizeof(h))) {
            ok = 0;
        } else {
            memcpy(&h, data + sizeof(header), sizeof(h));
            so = h.SubstituteNameOffset; sl = h.SubstituteNameLength;
            po = h.PrintNameOffset; pl = h.PrintNameLength;
            flags = h.Flags;
            path_offset = sizeof(header) + sizeof(h);
        }
    } else {
        PyBuffer_Release(&buf);
        PyErr_Format(PyExc_NotImplementedError, "Unsupported reparse tag: 0x%08lX",
                     (unsigned long)header.ReparseTag);
        return NULL;
    }

    if (!ok ||
        (Py_ssize_t)(path_offset + so + sl) > buf.len ||
        (Py_ssize_t)(path_offset + po + pl) > buf.len) {
        PyBuffer_Release(&buf);
        PyErr_SetString(PyExc_ValueError, "Reparse buffer truncated");
        return NULL;
    }

    subst_name = PyUnicode_DecodeUTF16(
        (const char *)data + path_offset + so, sl, NULL, NULL);
    print_name = subst_name ? PyUnicode_DecodeUTF16(
        (const char *)data + path_offset + po, pl, NULL, NULL) : NULL;
    PyBuffer_Release(&buf);

    if (!subst_name || !print_name) {
        Py_XDECREF(subst_name);
        Py_XDECREF(print_name);
        return NULL;
    }

    return Py_BuildValue("kkNN", (unsigned long)header.ReparseTag,
                          (unsigned long)flags, subst_name, print_name);
}

/* ---------------------------------------------------------------------
 * Privilege acquisition (SeBackup/SeRestore/SeCreateSymbolicLink) - must
 * run before opening a handle for reparse-point manipulation, or a
 * non-administrator process that was only *granted* (not yet enabled)
 * these privileges will fail with access-denied.
 * --------------------------------------------------------------------- */
static int privileges_acquired = 0;

static void
enable_privilege(HANDLE token, LPCWSTR name)
{
    LUID luid;
    TOKEN_PRIVILEGES tp;

    if (!LookupPrivilegeValueW(NULL, name, &luid)) return;
    tp.PrivilegeCount = 1;
    tp.Privileges[0].Luid = luid;
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
    AdjustTokenPrivileges(token, FALSE, &tp, sizeof(tp), NULL, NULL);
}

static void
ensure_privileges_internal(void)
{
    HANDLE token;

    if (privileges_acquired)
        return;

    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES, &token))
        return; /* best-effort: let the subsequent CreateFileW fail on its own if this matters */

    enable_privilege(token, L"SeBackupPrivilege");
    enable_privilege(token, L"SeRestorePrivilege");
    enable_privilege(token, L"SeCreateSymbolicLinkPrivilege");
    CloseHandle(token);

    privileges_acquired = 1;
}

/* ---------------------------------------------------------------------
 * Shared handle helper
 * --------------------------------------------------------------------- */
static HANDLE
open_path(const wchar_t *path, DWORD access, DWORD disposition, DWORD flags)
{
    ensure_privileges_internal();
    return CreateFileW(path, access, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                        NULL, disposition, flags, NULL);
}

static wchar_t *
arg_to_wchar(PyObject *obj, Py_ssize_t *out_len)
{
    return PyUnicode_AsWideCharString(obj, out_len);
}

/* ---------------------------------------------------------------------
 * set_reparse_point(path: str, buffer: bytes) -> None
 * --------------------------------------------------------------------- */
static PyObject *
cext_set_reparse_point(PyObject *self, PyObject *args)
{
    PyObject *path_obj;
    Py_buffer buf;
    Py_ssize_t path_len;
    wchar_t *path;
    HANDLE h;
    DWORD bytes_returned;
    BOOL ok;
    DWORD last_error;

    if (!PyArg_ParseTuple(args, "Uy*", &path_obj, &buf))
        return NULL;

    path = arg_to_wchar(path_obj, &path_len);
    if (!path) { PyBuffer_Release(&buf); return NULL; }

    h = open_path(path, GENERIC_WRITE, OPEN_EXISTING, FILE_FLAG_REPARSE_BACKUP);
    PyMem_Free(path);
    if (h == INVALID_HANDLE_VALUE) { PyBuffer_Release(&buf); return set_error_from_lasterror(); }

    bytes_returned = 0;
    ok = DeviceIoControl(h, FSCTL_SET_REPARSE_POINT, buf.buf, (DWORD)buf.len,
                          NULL, 0, &bytes_returned, NULL);
    last_error = GetLastError();
    CloseHandle(h);
    PyBuffer_Release(&buf);

    if (!ok) { SetLastError(last_error); return set_error_from_lasterror(); }
    Py_RETURN_NONE;
}

/* ---------------------------------------------------------------------
 * get_reparse_buffer(path: str) -> bytes
 * --------------------------------------------------------------------- */
static PyObject *
cext_get_reparse_buffer(PyObject *self, PyObject *args)
{
    PyObject *path_obj;
    Py_ssize_t path_len;
    wchar_t *path;
    HANDLE h;
    PyObject *result;
    DWORD bytes_returned;
    BOOL ok;
    DWORD last_error;

    if (!PyArg_ParseTuple(args, "U", &path_obj))
        return NULL;

    path = arg_to_wchar(path_obj, &path_len);
    if (!path) return NULL;

    h = open_path(path, GENERIC_READ, OPEN_EXISTING, FILE_FLAG_REPARSE_BACKUP);
    PyMem_Free(path);
    if (h == INVALID_HANDLE_VALUE) return set_error_from_lasterror();

    result = PyBytes_FromStringAndSize(NULL, MAX_REPARSE_BUFFER_SIZE);
    if (!result) { CloseHandle(h); return NULL; }

    bytes_returned = 0;
    ok = DeviceIoControl(h, FSCTL_GET_REPARSE_POINT, NULL, 0,
                          PyBytes_AS_STRING(result), MAX_REPARSE_BUFFER_SIZE,
                          &bytes_returned, NULL);
    last_error = GetLastError();
    CloseHandle(h);

    if (!ok) {
        Py_DECREF(result);
        SetLastError(last_error);
        return set_error_from_lasterror();
    }
    if (_PyBytes_Resize(&result, bytes_returned) < 0)
        return NULL;
    return result;
}

/* ---------------------------------------------------------------------
 * delete_reparse_point_ioctl(path: str, tag: int) -> None
 * --------------------------------------------------------------------- */
static PyObject *
cext_delete_reparse_point_ioctl(PyObject *self, PyObject *args)
{
    PyObject *path_obj;
    unsigned long tag;
    Py_ssize_t path_len;
    wchar_t *path;
    HANDLE h;
    ReparseHeader header;
    DWORD bytes_returned;
    BOOL ok;
    DWORD last_error;

    if (!PyArg_ParseTuple(args, "Uk", &path_obj, &tag))
        return NULL;

    path = arg_to_wchar(path_obj, &path_len);
    if (!path) return NULL;

    h = open_path(path, GENERIC_WRITE, OPEN_EXISTING, FILE_FLAG_REPARSE_BACKUP);
    PyMem_Free(path);
    if (h == INVALID_HANDLE_VALUE) return set_error_from_lasterror();

    header.ReparseTag = (ULONG)tag;
    header.ReparseDataLength = 0;
    header.Reserved = 0;

    bytes_returned = 0;
    ok = DeviceIoControl(h, FSCTL_DELETE_REPARSE_POINT, &header, sizeof(header),
                          NULL, 0, &bytes_returned, NULL);
    last_error = GetLastError();
    CloseHandle(h);

    if (!ok) { SetLastError(last_error); return set_error_from_lasterror(); }
    Py_RETURN_NONE;
}

/* ---------------------------------------------------------------------
 * create_hard_link(src: str, dst: str) -> None
 * --------------------------------------------------------------------- */
static PyObject *
cext_create_hard_link(PyObject *self, PyObject *args)
{
    PyObject *src_obj;
    PyObject *dst_obj;
    Py_ssize_t src_len;
    Py_ssize_t dst_len;
    wchar_t *src;
    wchar_t *dst;
    BOOL ok;
    DWORD last_error;

    if (!PyArg_ParseTuple(args, "UU", &src_obj, &dst_obj))
        return NULL;

    src = arg_to_wchar(src_obj, &src_len);
    if (!src) return NULL;
    dst = arg_to_wchar(dst_obj, &dst_len);
    if (!dst) { PyMem_Free(src); return NULL; }

    ok = CreateHardLinkW(dst, src, NULL);
    last_error = GetLastError();
    PyMem_Free(src);
    PyMem_Free(dst);

    if (!ok) { SetLastError(last_error); return set_error_from_lasterror(); }
    Py_RETURN_NONE;
}

/* ---------------------------------------------------------------------
 * Shared BY_HANDLE_FILE_INFORMATION fetch
 * --------------------------------------------------------------------- */
static int
get_file_info(const wchar_t *path, BY_HANDLE_FILE_INFORMATION *info)
{
    HANDLE h;
    BOOL ok;
    DWORD last_error;

    h = open_path(path, GENERIC_READ, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS);
    if (h == INVALID_HANDLE_VALUE) return 0;
    ok = GetFileInformationByHandle(h, info);
    last_error = GetLastError();
    CloseHandle(h);
    if (!ok) { SetLastError(last_error); return 0; }
    return 1;
}

/* ---------------------------------------------------------------------
 * get_link_count(path: str) -> int
 * --------------------------------------------------------------------- */
static PyObject *
cext_get_link_count(PyObject *self, PyObject *args)
{
    PyObject *path_obj;
    Py_ssize_t path_len;
    wchar_t *path;
    BY_HANDLE_FILE_INFORMATION info;
    int ok;

    if (!PyArg_ParseTuple(args, "U", &path_obj))
        return NULL;

    path = arg_to_wchar(path_obj, &path_len);
    if (!path) return NULL;

    ok = get_file_info(path, &info);
    PyMem_Free(path);
    if (!ok) return set_error_from_lasterror();

    return PyLong_FromUnsignedLong(info.nNumberOfLinks);
}

/* ---------------------------------------------------------------------
 * get_file_reference_number(path: str) -> int
 * --------------------------------------------------------------------- */
static PyObject *
cext_get_file_reference_number(PyObject *self, PyObject *args)
{
    PyObject *path_obj;
    Py_ssize_t path_len;
    wchar_t *path;
    BY_HANDLE_FILE_INFORMATION info;
    int ok;
    ULONGLONG frn;

    if (!PyArg_ParseTuple(args, "U", &path_obj))
        return NULL;

    path = arg_to_wchar(path_obj, &path_len);
    if (!path) return NULL;

    ok = get_file_info(path, &info);
    PyMem_Free(path);
    if (!ok) return set_error_from_lasterror();

    frn = ((ULONGLONG)info.nFileIndexHigh << 32) | info.nFileIndexLow;
    return PyLong_FromUnsignedLongLong(frn);
}

/* ---------------------------------------------------------------------
 * get_ntfs_file_record(volume_root: str, frn: int) -> bytes
 * --------------------------------------------------------------------- */
static PyObject *
cext_get_ntfs_file_record(PyObject *self, PyObject *args)
{
    PyObject *root_obj;
    ULONGLONG frn;
    Py_ssize_t root_len;
    wchar_t *root;
    wchar_t device_path[MAX_PATH];
    HANDLE h;
    LONGLONG input_frn;
    PyObject *result;
    DWORD bytes_returned;
    BOOL ok;
    DWORD last_error;

    if (!PyArg_ParseTuple(args, "UK", &root_obj, &frn))
        return NULL;

    root = arg_to_wchar(root_obj, &root_len);
    if (!root) return NULL;

    /* Strip a trailing backslash and prefix with the device namespace, e.g.
     * "C:\\" -> "\\\\.\\C:" */
    while (root_len > 0 && root[root_len - 1] == L'\\') root_len--;
    _snwprintf(device_path, MAX_PATH, L"\\\\.\\%.*ls", (int)root_len, root);
    PyMem_Free(root);

    h = open_path(device_path, GENERIC_READ, OPEN_EXISTING, 0);
    if (h == INVALID_HANDLE_VALUE) return set_error_from_lasterror();

    input_frn = (LONGLONG)frn;
    result = PyBytes_FromStringAndSize(NULL, MAX_REPARSE_BUFFER_SIZE);
    if (!result) { CloseHandle(h); return NULL; }

    bytes_returned = 0;
    ok = DeviceIoControl(h, FSCTL_GET_NTFS_FILE_RECORD, &input_frn, sizeof(input_frn),
                          PyBytes_AS_STRING(result), MAX_REPARSE_BUFFER_SIZE,
                          &bytes_returned, NULL);
    last_error = GetLastError();
    CloseHandle(h);

    if (!ok) {
        Py_DECREF(result);
        SetLastError(last_error);
        return set_error_from_lasterror();
    }
    if (_PyBytes_Resize(&result, bytes_returned) < 0)
        return NULL;
    return result;
}

/* ---------------------------------------------------------------------
 * volume_root(path: str) -> str
 * --------------------------------------------------------------------- */
static PyObject *
cext_volume_root(PyObject *self, PyObject *args)
{
    PyObject *path_obj;
    Py_ssize_t path_len;
    wchar_t *path;
    wchar_t out[MAX_PATH + 2];
    BOOL ok;
    DWORD last_error;

    if (!PyArg_ParseTuple(args, "U", &path_obj))
        return NULL;

    path = arg_to_wchar(path_obj, &path_len);
    if (!path) return NULL;

    ok = GetVolumePathNameW(path, out, MAX_PATH + 2);
    last_error = GetLastError();
    PyMem_Free(path);

    if (!ok) { SetLastError(last_error); return set_error_from_lasterror(); }
    return PyUnicode_FromWideChar(out, -1);
}

/* ---------------------------------------------------------------------
 * query_volume_flags(path: str, use_cache: bool=False) -> int
 * --------------------------------------------------------------------- */
static PyObject *volume_flags_cache = NULL;

static PyObject *
cext_query_volume_flags(PyObject *self, PyObject *args)
{
    PyObject *path_obj;
    int use_cache;
    Py_ssize_t path_len;
    wchar_t *path;
    wchar_t root[MAX_PATH + 2];
    PyObject *key;
    PyObject *cached;
    DWORD fs_flags;
    BOOL ok;
    PyObject *result;

    use_cache = 0;
    key = NULL;

    if (!PyArg_ParseTuple(args, "U|p", &path_obj, &use_cache))
        return NULL;

    path = arg_to_wchar(path_obj, &path_len);
    if (!path) return NULL;

    if (!GetVolumePathNameW(path, root, MAX_PATH + 2)) {
        PyMem_Free(path);
        return set_error_from_lasterror();
    }
    PyMem_Free(path);

    if (use_cache) {
        if (!volume_flags_cache) volume_flags_cache = PyDict_New();
        key = PyUnicode_FromWideChar(root, -1);
        cached = key ? PyDict_GetItem(volume_flags_cache, key) : NULL;
        if (cached) {
            Py_DECREF(key);
            Py_INCREF(cached);
            return cached;
        }
    }

    fs_flags = 0;
    ok = GetVolumeInformationW(root, NULL, 0, NULL, NULL, &fs_flags, NULL, 0);
    if (!ok) {
        Py_XDECREF(key);
        return set_error_from_lasterror();
    }

    result = PyLong_FromUnsignedLong(fs_flags);
    if (use_cache && key && result) {
        PyDict_SetItem(volume_flags_cache, key, result);
    }
    Py_XDECREF(key);
    return result;
}

static PyObject *
cext_clear_volume_cache(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    if (volume_flags_cache) PyDict_Clear(volume_flags_cache);
    Py_RETURN_NONE;
}

/* ---------------------------------------------------------------------
 * ensure_privileges() -> None
 * --------------------------------------------------------------------- */
static PyObject *
cext_ensure_privileges(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    HANDLE token;

    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES, &token))
        return set_error_from_lasterror();
    CloseHandle(token);

    ensure_privileges_internal();
    Py_RETURN_NONE;
}

static PyObject *
cext_reset_privileges_for_tests(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    privileges_acquired = 0;
    Py_RETURN_NONE;
}

/* ---------------------------------------------------------------------
 * Module definition
 * --------------------------------------------------------------------- */
static PyMethodDef cext_methods[] = {
    {"build_reparse_buffer", cext_build_reparse_buffer, METH_VARARGS, NULL},
    {"parse_reparse_buffer", cext_parse_reparse_buffer, METH_VARARGS, NULL},
    {"set_reparse_point", cext_set_reparse_point, METH_VARARGS, NULL},
    {"get_reparse_buffer", cext_get_reparse_buffer, METH_VARARGS, NULL},
    {"delete_reparse_point_ioctl", cext_delete_reparse_point_ioctl, METH_VARARGS, NULL},
    {"create_hard_link", cext_create_hard_link, METH_VARARGS, NULL},
    {"get_link_count", cext_get_link_count, METH_VARARGS, NULL},
    {"get_file_reference_number", cext_get_file_reference_number, METH_VARARGS, NULL},
    {"get_ntfs_file_record", cext_get_ntfs_file_record, METH_VARARGS, NULL},
    {"volume_root", cext_volume_root, METH_VARARGS, NULL},
    {"query_volume_flags", cext_query_volume_flags, METH_VARARGS, NULL},
    {"clear_volume_cache", cext_clear_volume_cache, METH_NOARGS, NULL},
    {"ensure_privileges", cext_ensure_privileges, METH_NOARGS, NULL},
    {"reset_privileges_for_tests", cext_reset_privileges_for_tests, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cext_module = {
    PyModuleDef_HEAD_INIT,
    "_cext",
    NULL,
    -1,
    cext_methods
};

PyMODINIT_FUNC
PyInit__cext(void)
{
    return PyModule_Create(&cext_module);
}
