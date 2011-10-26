import sys, os
sys.path.append(os.path.join(os.getcwd(), 'build', 'lib.win32-2.7'))
import ntfslink as nt
print nt.junction('C:\Temp', 'temp')
print nt.symlink('src\\ntfslink.h', 'test.h')
print nt.readlink('temp')
print nt.isjunction('temp')
print nt.unlink('temp')
print nt.unlink('test.h')
print nt.isjunction('temp')