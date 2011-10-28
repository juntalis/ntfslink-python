import sys, os
sys.path.append(os.path.join(os.getcwd(), 'build', 'lib.win32-2.7'))
import ntcyg as cyg
#cyg.symlink('C:\\ShellEnv\\j-tree\\sbin\\python\\2.7\\python.exe', 'python')
print cyg.cygtowin('/usr/local/bin/python.exe')