import random


def greeting(rng=None):
    """Return a random greeting. rng 可注入（支持 seed 或自定义随机对象）。"""
    if rng is None:
        rng = random
    options = ["hi", "hello", "hey"]
    return rng.choice(options)
