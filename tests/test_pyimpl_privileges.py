from ntfslink._pyimpl import privileges


def test_ensure_privileges_only_calls_obtain_once(monkeypatch):
    privileges.reset_for_tests()
    calls = []
    monkeypatch.setattr(privileges, 'obtain_privileges', lambda names: calls.append(names))

    privileges.ensure_privileges()
    privileges.ensure_privileges()
    privileges.ensure_privileges()

    assert len(calls) == 1
    privileges.reset_for_tests()


def test_obtain_privileges_noop_for_empty_list(monkeypatch):
    called = []
    monkeypatch.setattr(privileges.winapi, 'GetCurrentProcess', lambda: called.append('called'))
    privileges.obtain_privileges([])
    assert called == []


def test_obtain_privileges_looks_up_and_adjusts_each(monkeypatch):
    looked_up = []
    adjusted = []

    monkeypatch.setattr(privileges.winapi, 'GetCurrentProcess', lambda: 1234)
    monkeypatch.setattr(privileges.winapi, 'OpenProcessToken', lambda hproc, access, phtoken: None)
    monkeypatch.setattr(privileges.winapi, 'CloseHandle', lambda h: None)

    def fake_lookup(system, name, luid_ref):
        looked_up.append(name)

    def fake_adjust(token, disable_all, tp_ref, buflen, prev, retlen):
        adjusted.append(True)

    monkeypatch.setattr(privileges.winapi, 'LookupPrivilegeValueW', fake_lookup)
    monkeypatch.setattr(privileges.winapi, 'AdjustTokenPrivileges', fake_adjust)

    privileges.obtain_privileges(['SeBackupPrivilege', 'SeRestorePrivilege'])

    assert looked_up == ['SeBackupPrivilege', 'SeRestorePrivilege']
    assert adjusted == [True]
