from chapter2.stateful_counter import Counter


def test_counter_inc_reset():
    c = Counter()
    assert c.inc() == 1
    assert c.inc() == 2
    c.reset()
    assert c.inc() == 1
