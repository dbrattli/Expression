import pytest
from expression.system import AsyncDisposable, Disposable, ObjectDisposedException


def test_disposable_works():
    called = []
    disp = Disposable.create(lambda: called.append(True))

    with disp:
        assert not called

    assert called


def test_disposable_disposed():
    called = []
    disp = Disposable.create(lambda: called.append(True))
    disp.dispose()
    assert called

    with pytest.raises(ObjectDisposedException):  # type: ignore
        with disp:
            assert not called

    assert called


def test_disposable_disposed_twice_calls_once():
    called = []
    disp = Disposable.create(lambda: called.append(True))
    disp.dispose()
    disp.dispose()

    assert len(called) == 1


@pytest.mark.asyncio
async def test_async_disposable_works():
    called = []

    async def action():
        called.append(True)

    disp = AsyncDisposable.create(action)

    async with disp:
        assert not called

    assert called


@pytest.mark.asyncio
async def test_async_disposable_disposed():
    called = []

    async def action():
        called.append(True)

    disp = AsyncDisposable.create(action)
    await disp.dispose_async()
    assert called

    with pytest.raises(ObjectDisposedException):  # type: ignore
        async with disp:
            assert not called

    assert called


@pytest.mark.asyncio
async def test_async_disposable_disposed_twice_calls_once():
    called = []

    async def action():
        called.append(True)

    disp = AsyncDisposable.create(action)
    await disp.dispose_async()
    await disp.dispose_async()

    assert len(called) == 1
