from functools import wraps as _wraps


def deprecated(f):
    @_wraps(f)
    def wrapper(*args, **kwargs):
        from utils import logger as _logger
        _logger.warning(f"Method {f.__name__} has been deprecated and will be removed soon.")
        return f(*args, **kwargs)
    return wrapper
