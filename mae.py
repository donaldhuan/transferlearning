from rec import *


def mae(intensity):
    result = transfer(intensity)
    test = result[1]
    training = result[0]
    _mae = 0
    for t in test:
        _mae += abs(training[t[0] - 1][t[1] - 1] - t[2])
    return _mae * 1.0 / len(test)

if __name__ = "__main__":
    a = mae(50)
    print a
