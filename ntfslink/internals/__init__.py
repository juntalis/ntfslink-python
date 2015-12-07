import functools

def memoize(obj):
	"""
	From the Python Decorator Library (http://wiki.python.org/moin/PythonDecoratorLibrary):
	Cache the results of a function call with specific arguments. Note that this decorator ignores **kwargs.
	"""
	cache = obj.cache = {}

	@functools.wraps(obj)
	def memoizer(*args, **kwargs):
		if args not in cache:
			cache[args] = obj(*args, **kwargs)
		return cache[args]

	return memoizer
