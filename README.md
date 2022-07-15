# Lazy Toolz

```
pip install lazytools
```

## Examples

This package adds lazily evaluated immutable objects.

```python
from lazytoolz import LazyList

myList = LazyList([1, 2, 3])

myNumbers = LazyList(4, 5, 6)

myRange = LazyList(range(7, 1000000))

allNumbers = myList + myNumbers + myRange

print(allNumbers.drop(2).map(lambda x: x ** 2).filter(lambda x: x % 3 == 0).take(10))
```

```
LazyList(9, 36, 81, 144, 225, 324, 441, 576, 729, 900)
```
