from __future__ import division
from copy import copy
from operators import binary_operators, boolean_operators
import roulette
from roulette import Probability

def argument_should_have_default_value(context):
	return Probability(0.5)

def can_raise(context):
	"""Return True if generated programs can raise errors, False otherwise."""
	return False

def function_should_have_variable_arguments(context):
	return Probability(0.5)

def function_should_have_keyword_arguments(context):
	return Probability(0.5)

def give_up_threshold(context):
	"""
	Return the number of attemps the generator should make to generate 
	a construct before falling back to the default for that construct.
	
	"""
	return 10

def pick_binary_operator(context):
	return roulette.pick(binary_operators)

def pick_boolean_operator(context):
	return roulette.pick(boolean_operators)

def pick_integer(context):
	min = -100
	max = 100
	return roulette.random_integer(min, max)

def pick_float(context):
	min = -1
	max = 1
	return roulette.random_float(min, max)

def pick_kind_of_constant(context):
	distribution = {
		'integer': 1,
		'float': 1,
		'string': 1,
		'list': 1,
		'tuple': 1,}
	#return roulette.pick(distribution)
	return 'integer'

def pick_kind_of_expression(context):
	distribution = {
		'binary_operation': 1,
		'boolean_operation': 1,
		'call': 1,
		'variable': 1,
		'constant': 1,}
	if not context.has_names:
		return 'constant'
	distribution = copy(distribution)
	distribution['boolean_operation'] = distribution['boolean_operation'] / (context.depth / 10)
	return roulette.pick(distribution)

def pick_kind_of_statement(context):
	distribution = {
		'assignment': 1,
		'aug_assignment': 1,
		'if': 0,
		# The Python ast module expects expressions to be encapsulated in a 
		# Expr object when they are used as statements, but not otherwise.
		# Since PySmith does not make that distinction, it cannot generate 
		# expressions as statements as long as it uses the ast module.
		'expression': 0, 
		'function_def': 0,
		'class_def': 0}
	distribution = copy(distribution)
	distribution['function_def'] = distribution['function_def'] / (context.depth / 6)
	distribution['if'] = distribution['if'] / (context.depth / 6)
	distribution['class_def'] = distribution['class_def'] / (context.depth / 6)
	return roulette.pick(distribution)

def pick_name(context, predicates=None):
	"""
	Pick a name of the context. If ``member`` is provided, the value associated
	with the returned name has a member called ``member``.
	This function may return None.
	
	"""
	should_use_global = Probability(0.05)
	def global_or_local(context, *args):
		global_names = context.global_names(*args)
		local_names = context.local_names(*args)
		if global_names and (not local_names or should_use_global):
			return global_names
		return local_names or None
	names = global_or_local(context, predicates)
	return roulette.pick(names)

def pick_length_of_name(context):
	return 3

def pick_number_of_boolean_operands(context):
	return roulette.random_integer(2, 3)

def pick_number_of_function_arguments(context):
	return roulette.random_integer(0, 7)

def should_add_another_statement(context):
	max_number_of_statements = 3
	return context.number_of_statements < max_number_of_statements

def should_be_new_name(context):
	max_number_of_names = 300
	should_be_new_name = Probability(0.99)
	under_limit = context.number_of_names < max_number_of_names
	return under_limit and should_be_new_name
		

