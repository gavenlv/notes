import pytest
from chapter2.stateful_counter import Counter


@pytest.fixture
def counter():
    # 每个测试都会得到一个新的 Counter 实例，保证隔离
    return Counter()
