from ast import AST
from copy import copy
from inspect import stack
from os import linesep as newline
from codegen import to_source

def root(use_builtins=True):
	if not use_builtins:
		return Context()
	# Retrieving builtins
	globals_ = {}
	exec '' in globals_
	builtins = globals_['__builtins__']
	# Let's remove annoying stuff
	del builtins['input']
	del builtins['raw_input']
	# WindowsError is not defined on non-Windows distribution
	# It also seems to be missing in the Jython 2.5.2 Windows distribution,
	# although the documentation mentions it.
	# Anyway we might as well delete it.
	if 'WindowsError' in builtins:
		del builtins['WindowsError']
	globals_.update(builtins)
	return Context(globals_)

class Context(object):
	
	def __init__(self, global_names=None, local_names=None):
		self._globals = global_names or {}
		self._locals = local_names or {}
		self._number_of_lines = 0
		self._number_of_statements = 0
	
	@property
	def all_names(self):
		return frozenset(self._globals.keys() + self._locals.keys())
	
	@property
	def depth(self):
		return len(stack())
	
	@property
	def has_names(self):
		return self._globals or self._locals

	@property
	def number_of_names(self):
		return len(self._globals) + len(self._locals)
	
	@property
	def number_of_statements(self):
		return self._number_of_statements
	
	def evaluate(self, expression):
		assert expression is not None
		if isinstance(expression, AST):
			expression_code = to_source(expression)
		try:
			eval(expression_code, self._globals, self._locals)
		except Exception, e:
			print 'Expression raised error:', str(e), 'in', expression_code
		else:
			return expression
	
	def global_names(self, predicates=None):
		return self._filter(self._globals, predicates or [])
	
	def local_names(self, predicates=None):
		return self._filter(self._locals, predicates or [])
	
	def run(self, statement):
		"""
		Run the given statement inside this context. Return the statement if the 
		execution did not raise any error, ``None`` otherwise.
		
		"""
		assert statement is not None
		if isinstance(statement, AST):
			statement_code = to_source(statement)
		try:
			exec statement_code in self._globals, self._locals
		except Exception, e:
			print 'Statement raised error:', str(e), 'in', statement_code, 'in context', id(self)
			return
		self._number_of_statements += 1
		self._number_of_lines += statement_code.count(newline)
		return statement
		# TODO : number of lines
	
	def spawn_closed_child(self, local_names=None):
		#copy_of_locals = copy(self._locals)
		#copy_of_locals.update(additional_local_names or {})
		#child = Context(copy(self._globals), copy_of_locals)
		#print 'Spawning context', id(child), 'from context', id(self)
		#print 'Names passed:', [n for n in self.all_names if n.endswith('_')]
		return Context(copy(self._globals), local_names)
	
	def spawn_open_child(self, additional_local_names=None):
		copy_of_locals = copy(self._locals)
		copy_of_locals.update(additional_local_names or {})
		return Context(copy(self._globals), copy_of_locals)

	def _filter(self, names, predicates):
		assert names is not None
		assert predicates is not None
		if not predicates:
			return names.keys()
		names = (n for n,v in names.iteritems() if all(p(v) for p in predicates))
		return frozenset(names)
