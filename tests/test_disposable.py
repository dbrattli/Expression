import pytest
from fslash.system import Disposable, ObjectDisposedException


def test_disposable_works():
    called = []
    disp = Disposable(lambda: called.append(True))

    with disp:
        assert not called

    assert called


def test_disposable_disposed():
    called = []
    disp = Disposable(lambda: called.append(True))
    disp.dispose()
    assert called

    with pytest.raises(ObjectDisposedException):  # type: ignore
        with disp:
            assert not called

    assert called


def test_disposable_disposed_twice_calls_once():
    called = []
    disp = Disposable(lambda: called.append(True))
    disp.dispose()
    disp.dispose()

    assert len(called) == 1
