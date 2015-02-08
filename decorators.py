from functools import wraps

def nonzero(obj):
    return obj

def not_none(obj):
    return obj is not None

def post(*predicates):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            assert all(predicate(result) for predicate in predicates), \
                'A post-condition was not met in function ' + func.__name__
            return result
        return wrapper
    return decorator

def generator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            yield func(*args, **kwargs)
    return wrapper