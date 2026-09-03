import subprocess
import sys


def test_import_fails_cleanly_on_non_windows_platform():
    code = (
        "import sys, types\n"
        "sys.platform = 'linux'\n"
        "try:\n"
        "    import ntfslink\n"
        "    print('IMPORTED-UNEXPECTEDLY')\n"
        "except ImportError as e:\n"
        "    print('RAISED:' + str(e))\n"
    )
    result = subprocess.run(
        [sys.executable, '-c', code], capture_output=True, text=True, timeout=30
    )
    assert 'RAISED:' in result.stdout
    assert 'IMPORTED-UNEXPECTEDLY' not in result.stdout
