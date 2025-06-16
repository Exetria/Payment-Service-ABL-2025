from nameko.exceptions import registry


def remote_error(exc_path):
    """
    Decorator that registers remote exception with matching ``exc_path``
    to be deserialized to decorated exception instance, rather than
    wrapped in ``RemoteError``.
    """

    def wrapper(exc_type):
        registry[exc_path] = exc_type
        return exc_type

    return wrapper

@remote_error('payments.exceptions.NotFound')
class PaymentNotFound(Exception):
    """
    If the payments service raises a ``NotFound`` error from an RPC call,
    The ``RemoteError`` will be transformed and raised locally as this
    exception instead.
    """
    pass
