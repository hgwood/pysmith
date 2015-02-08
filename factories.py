from ast import *
from inspect import isclass, isfunction, getargspec
from itertools import dropwhile
import random
import string
from asthelpers import *
from decorators import *
import rules

# Dispatchers

def new(kind, context):
#	if isinstance(kind, type):
#		kind = kind.__name__
	new_thing = globals()['new_' + kind.lower()]
	return new_thing(context)

# Module

@post(not_none)
def new_module(context):
	body = new_body(context)
	var_per_print = 10
	names = context.all_names
	from itertools import islice
	for i in xrange(0, len(names), var_per_print):
		po = [Name(n) for n in islice(names, i, i + var_per_print)]
		body.append(Print(None, po, True))
	return Module(body)

# Statements

default_statement = Assign([Name('x')], Num(1))

def random_statement(context):
	kind = rules.pick_kind_of_statement(context)
	return new(kind, context)

def new_statement(context):
	return try_(random_statement, context, default_statement)

def new_assignment(context):
	target = new_name(context)
	value = new_expression(context)
	if target and value:
		return Assign([target], value)

def new_aug_assignment(context):
	operator = rules.pick_binary_operator(context)
	not_type = lambda x: not isinstance(x, type) # to avoid slot wrappers
	target = Name(rules.pick_name(context, operator.left_predicates + [not_type]))
	value = new_expression(context)
	if target and value:
		return AugAssign(target, operator.name, value)

def new_class_def(context):
	name = new_identifier(context)
	base = rules.pick_name(context, [lambda x: isclass(x)])
	bases = [Name(base)] if base is not None else []
	class_context = context.spawn_closed_child()
	body = new_body(class_context)
	return ClassDef(name, bases, body, [])

def new_function_def(context):
	# TODO: rewrite that garbage!
	name = new_identifier(context)
	arguments = new_arguments(context)
	function_context = context.spawn_closed_child(arguments.args)
	body = new_body(function_context)
	body += [Return(new_expression(function_context))]
	arguments = Arguments(arguments.names, arguments.defaults, arguments.varargs, arguments.kwargs)
	return FunctionDef(name, arguments, body, [])	

def new_if(context):
	test = try_(new_boolean_operation, context, default_expression, context.evaluate)
	if_context = context.spawn_open_child()
	body = new_body(if_context)
	else_context = context.spawn_open_child()
	orelse = new_body(else_context)
	return If(test, body, orelse)

def new_for_loop(context):
	target = new_name(context)
	iter = rules.pick_name(context, lambda x: hasattr(x, '__iter__'))
	for_context = context.spawn_open_child({target.id:0})
	# TODO

def new_while_loop(context):
	test = try_(new_boolean_operation, context, default_expression, context.evaluate)
	guard = new_name(context)
	guard_cond = Compare(guard, [Lt], [Num(10)]) # put limit in rules
	guard_incr = AugAssign(guard, Add, Num(1))
	guarded_test = BoolOp(ast.And, [test, guard_cond])
	while_context = context.spawn_open_child()
	body = new_body(while_context)
	body.append(guard_incr)
	else_context = context.spawn_open_child()
	orelse = new_body(else_context)
	return While(guarded_test, body, orelse)

# Expressions

default_expression = Num(1)

def random_expression(context):
	kind = rules.pick_kind_of_expression(context)
	return new(kind, context)

def new_expression(context):
	return try_(random_expression, context, default_expression)

def new_binary_operation(context):
	operator = rules.pick_binary_operator(context)
	not_type = lambda x: not isinstance(x, type) # to avoid slot wrappers
	left = rules.pick_name(context, operator.left_predicates + [not_type])
	right = rules.pick_name(context, operator.right_predicates + [not_type])
	if left and right:
		return BinOp(Name(left), operator.name, Name(right))

def new_boolean_operation(context):
	operator = rules.pick_boolean_operator(context)
	number_of_operands = rules.pick_number_of_boolean_operands(context)
	operands = ntimes(number_of_operands, new_expression, context)
	return BoolOp(operator, operands)

def new_call(context):
	callee = rules.pick_name(context, [lambda x: isfunction(x)])
#	argspec = getargspec(callee)
#	number_of_args = len(argspec.args) - len(argspec.defaults)
#	values = ntimes(number_of_args, new_expression, context)
	if callee:
		return Call(Name(callee), [])

def new_variable(context):
	name = rules.pick_name(context)
	if name:
		return Name(name)

def new_name(context):
	return Name(new_identifier(context))

# Constants

def new_constant(context):
	kind = rules.pick_kind_of_constant(context)
	return new(kind, context)

def new_integer(context):
	return Num(rules.pick_integer(context))

def new_float(context):
	return Num(rules.pick_float(context))

def new_string(context):
	return Str('a')

def new_list(context):
	return List([])

def new_tuple(context):
	return Tuple(())

# Identifiers

@post(not_none)
def new_identifier(context):
	"""
	Create a new identifier or return an existing one.
	"""
	def random_identifier(length):
		random_letter = lambda: random.choice(string.ascii_lowercase)
		name = ''.join(random_letter() for _ in xrange(length)) + '_'
		return name
	if not context.has_names or rules.should_be_new_name(context):
		return random_identifier(rules.pick_length_of_name(context))
	else:
		return rules.pick_name(context)

# Partial constructs

@post(nonzero)
def new_body(context):
	statements = []
	while rules.should_add_another_statement(context):
		statement = new_statement(context)
		if context.run(statement) or rules.can_raise(context):
			statements.append(statement)
	if not statements:
		statements.append(Pass())
	return statements

def new_arguments(context):
	class Arguments(object):
		def __init__(self):
			number_of_arguments = rules.pick_number_of_function_arguments(context)
			names = ntimes_unique(number_of_arguments, new_identifier, context)
			from copy import copy
			self.names = copy(names)
			values = ntimes(number_of_arguments, new_constant, context)
			self.defaults = list(dropwhile(lambda _: not rules.argument_should_have_default_value(context), values))
			self.varargs = None
			self.kwargs = None
			if rules.function_should_have_variable_arguments(context):
				self.varargs = new_identifier(context)
				names.append(self.varargs)
				values.append(List([]))
			if rules.function_should_have_keyword_arguments(context):
				self.kwargs = new_identifier(context)
				names.append(self.kwargs)
				values.append(Dict([], []))
			self.args = dict(zip(names, values)) 
	return Arguments()

# Helpers

def try_(new_function, context, default, transform=lambda x: x):
	tresult = None
	attempt = 0
	while not tresult and attempt < rules.give_up_threshold(context):
		result = new_function(context)
		tresult = transform(result)
		attempt += 1
	return result or default

def ntimes(n, func, *args):
	return [func(*args) for _ in xrange(n)]

def ntimes_unique(n, func, *args):
	results = []
	while len(results) < n:
		result = func(*args)
		if result not in results:
			results.append(result)
	assert len(results) == n
	return results