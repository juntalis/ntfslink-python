# encoding: utf-8
"""
ntdll.py
TODO: Description

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from ctypes import *
from ctypes.wintypes import *

NTSTATUS = LONG

class UNICODE_STRING(Structure):
	_fields_ = [
		('Length', WORD),
		('MaximumLength', WORD),
		('Buffer', LPWSTR),
	]

PUNICODE_STRING = POINTER(UNICODE_STRING)

IRP_MJ_MAXIMUM_FUNCTION = 0x1b

class DRIVER_OBJECT(Structure):
	_fields_ = (
		('Type', SHORT),
		('Size', SHORT),
		('DeviceObject', LPVOID),
		('Flags', ULONG),

		('DriverStart', LPVOID),
		('DriverSize', ULONG),
		('DriverSection', LPVOID),
		('DriverExtension', LPVOID),

		('DriverName', UNICODE_STRING),
		('HardwareDatabase', PUNICODE_STRING),
		('FastIoDispatch', LPVOID),

		('DriverInit', LPVOID),
		('DriverStartIo', LPVOID),
		('DriverUnload', LPVOID),
		('MajorFunction', LPVOID * IRP_MJ_MAXIMUM_FUNCTION),
	)

# IoQueryFullDriverPath
# IoQueryFullDriverPath



from ctypes import *
from ctypes.wintypes import *

OBJ_CASE_INSENSITIVE = 0x00000040
STANDARD_RIGHTS_READ = 0x00020000
DIRECTORY_QUERY      = 0x00000001

def NT_SUCCESS(status):
	if (status >= 0 and status <= 0x3FFFFFFF) or (status >= 0x40000000 and status <= 0x7FFFFFFF):
		return 1
	else:
		return 0

class UNICODE_STRING(Structure):
	_fields_ = [("Length", USHORT),
				("MaximumLength", USHORT),
				("Buffer", c_wchar_p)]

prototype_RtlInitUnicodeString = WINFUNCTYPE(None, POINTER(UNICODE_STRING), c_wchar_p)
paramflags_RtlInitUnicodeString = (1, "DestinationString", 0), (1, "SourceString", "")
RtlInitUnicodeString = prototype_RtlInitUnicodeString(("RtlInitUnicodeString", windll.ntdll), paramflags_RtlInitUnicodeString)

class OBJECT_ATTRIBUTES(Structure):
	_fields_ = [("Length", ULONG),
				("RootDirectory", HANDLE),
				("ObjectName", POINTER(UNICODE_STRING)),
				("Attributes", ULONG),
				("SecurityDescriptor", c_void_p),
				("SecurityQualityOfService", c_void_p)]

prototype_NtOpenDirectoryObject = WINFUNCTYPE(c_uint, POINTER(HANDLE), DWORD, POINTER(OBJECT_ATTRIBUTES))
paramflags_NtOpenDirectoryObject = (1, "DirectoryHandle", None), (1, "DesiredAccess", 1), (1, "ObjectAttributes", None)
NtOpenDirectoryObject = prototype_NtOpenDirectoryObject(("NtOpenDirectoryObject", windll.ntdll), paramflags_NtOpenDirectoryObject)

class OBJECT_DIRECTORY_INFORMATION(Structure):
	_fields_ = [("Name", UNICODE_STRING),
				("TypeName", UNICODE_STRING)]

prototype_NtQueryDirectoryObject = WINFUNCTYPE(c_uint, HANDLE, c_void_p, ULONG, BOOLEAN, BOOLEAN, POINTER(ULONG), POINTER(ULONG))
paramflags_NtQueryDirectoryObject = (1, "DirectoryHandle"), (1, "Buffer"), (1, "Length"), (1, "ReturnSingleEntry"), (1, "RestartScan"), (1, "Context"), (1, "ReturnLength")
NtQueryDirectoryObject = prototype_NtQueryDirectoryObject(("NtQueryDirectoryObject", windll.ntdll), paramflags_NtQueryDirectoryObject)

def InitializeObjectAttributes(p, n, a, r, s):
	p.Length = sizeof(OBJECT_ATTRIBUTES)
	p.RootDirectory = r
	p.Attributes = a
	p.ObjectName = n
	p.SecurityDescriptor = s
	p.SecurityQualityOfService = None


def NativeDir(path):
	return_list = []

	UName = UNICODE_STRING()
	ObjectAttributes = OBJECT_ATTRIBUTES()
	hObject = HANDLE()

	RtlInitUnicodeString(byref(UName), path)
	InitializeObjectAttributes(ObjectAttributes, pointer(UName), OBJ_CASE_INSENSITIVE, c_void_p(), None)
	status = NtOpenDirectoryObject(byref(hObject), STANDARD_RIGHTS_READ | DIRECTORY_QUERY, byref(ObjectAttributes))

	if NT_SUCCESS(status):
		index = ULONG(0)
		dw = ULONG()
		data = (c_wchar * 1024)()
		while 1:
			memset(data, 1024, 0)
			object_directory_information = cast(data, POINTER(OBJECT_DIRECTORY_INFORMATION))
			status = NtQueryDirectoryObject(hObject, object_directory_information, 1024, c_byte(1), c_byte(0), pointer(index), pointer(dw))
			if NT_SUCCESS(status):
				return_list.append(object_directory_information.contents.Name.Buffer)
			else:
				break
	return return_list

def get_drive_list():
	devices = NativeDir("\\Device")
	for d in devices:
		if d.startswith("CdRom"):
			print("\\Devices\\"+d)

get_drive_list()



