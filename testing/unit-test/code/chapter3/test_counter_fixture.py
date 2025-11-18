def test_counter_with_fixture(counter):
    assert counter.inc() == 1
    assert counter.inc() == 2
    counter.reset()
    assert counter.inc() == 1
