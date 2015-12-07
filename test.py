import os, tempfile
from ntfslink import hardlinks, symlinks, junctions, cyglinks

_noext = lambda filepath: os.path.splitext(filepath)[0]

# Shorten up path function calls
sm = staticmethod
fs = type('FS', tuple(), {
	'dirname': sm(os.path.dirname),
	'basename': sm(os.path.basename),
	'splitext': sm(os.path.splitext),
	'abspath': sm(os.path.abspath),
	'relpath': sm(os.path.relpath),
	'join': sm(os.path.join),
	'isfile': sm(os.path.isfile),
	'isdir': sm(os.path.isdir),
	'isabs': sm(os.path.isabs),
	'isrel': sm(lambda filepath: \
		not os.path.isabs(filepath)),
	'exists': sm(os.path.exists),
	'noext': sm(lambda filepath: \
		os.path.splitext(filepath)[0]),
	'ext': sm(lambda filepath: \
		os.path.splitext(filepath)[-1]),
	'reldir': sm(lambda dirpath, target: \
		os.path.relpath(os.path.dirname(target), start=dirpath)),
	'dname': sm(lambda filepath: \
		os.path.dirname(os.path.abspath(filepath))),
	'bname': sm(lambda filepath: \
		_noext(os.path.basename(filepath)))
})()

# dirworkspace = tempfile.mkdtemp()
# hardlinks.example(os.path.abspath(__file__))
rootdir = fs.dname(__file__)
testsdir = fs.join(rootdir, 'tests')
for cygpath in os.listdir(testsdir):
	cygpath = fs.join(testsdir, cygpath)
	print cygpath, '=>', cyglinks.read(cygpath)
# symlinks.create('ntfslink
