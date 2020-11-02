import pytest
from expression.system import CancellationToken, CancellationTokenSource, ObjectDisposedException


def test_token_none_works():
    token = CancellationToken.none()
    assert isinstance(token, CancellationToken)
    assert not token.can_be_canceled
    assert not token.is_cancellation_requested


def test_token_source_works():
    source = CancellationTokenSource()
    assert not source.is_cancellation_requested

    with source as token:

        assert isinstance(token, CancellationToken)


def test_token_cancelled_source_works():
    source = CancellationTokenSource.cancelled_source()
    assert isinstance(source, CancellationTokenSource)
    assert source.is_cancellation_requested

    with pytest.raises(ObjectDisposedException):  # type: ignore
        with source as token:
            assert not token


def test_token_cancellation_works():
    source = CancellationTokenSource()
    with source as token:
        token.throw_if_cancellation_requested()

        assert token.can_be_canceled
        assert not token.is_cancellation_requested

    assert token.is_cancellation_requested
    with pytest.raises(ObjectDisposedException):  # type: ignore
        token.throw_if_cancellation_requested()


def test_token_cancellation_register_works():
    called = []
    source = CancellationTokenSource()
    with source as token:
        token.register(lambda: called.append(True))
        assert not called

    assert called


def test_token_cancellation_register_unregister_works():
    called = []
    source = CancellationTokenSource()
    with source as token:
        registration = token.register(lambda: called.append(True))
        assert not called
        registration.dispose()

    assert not called


def test_token_cancelled_register_throws():
    called = []
    source = CancellationTokenSource.cancelled_source()

    with pytest.raises(ObjectDisposedException):  # type: ignore
        with source as token:
            token.register(lambda: called.append(True))

    assert not called
