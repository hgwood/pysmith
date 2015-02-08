import random
from bisect import bisect


def _random(max=1):
	return random.uniform(0, max)

def random_integer(min, max):
	return random.randint(min, max)

def random_float(min, max):
	return random.uniform(min, max)

def truth(probability):
	"""
	Return ``True`` if an event with given probability should happen or not.
	
	"""
	assert probability >= 0 and probability <= 1
	return _random() < probability

def pick(values, weights=None):
	"""
	Pick the value of a random variable of given probability distribution.
	The weights don't have to add up to 1. If ommited, all weight are assumed 
	to be equal. `values` can be a dict mapping values to weights.
	
	"""
	if isinstance(values, frozenset):
		pass
	if not values:
		return
	def accumulate(iterable):
		sum = 0
		for item in iterable:
			sum += item
			yield sum
	if hasattr(values, 'keys') and hasattr(values, 'values'):
		weights = values.values()
		values = list(values.keys())
	else:
		values = list(values)
	if weights == None:
		return random.choice(values)
	scale = list(accumulate(weights))
	if scale[-1] == 0: 
		raise ValueError('All weights cannot be 0')
	r = _random(scale[-1])
	index = bisect(scale, r)
	return values[index]

class Probability(object):
	
	def __init__(self, value):
		if value < 0 or value > 1:
			raise ValueError("value must be between 0 and 1")
		self.value = value
	
	def __nonzero__(self):
		return truth(self.value)