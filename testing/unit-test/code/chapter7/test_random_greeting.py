from chapter7.random_greeting import greeting
import random


def test_greeting_with_seed():
    rng = random.Random(0)
    assert greeting(rng) == 'hello'  # deterministic for seed 0


def test_greeting_default_random():
    # Demonstrates that without controlling RNG test is potentially non-deterministic,
    # but we avoid flakiness by not asserting a specific value here; instead assert membership.
    val = greeting()
    assert val in ('hi', 'hello', 'hey')
