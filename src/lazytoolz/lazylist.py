from __future__ import annotations
from typing import TypeVar, Generic, Callable, Iterable, Iterator, Generator

from itertools import tee

T = TypeVar("T")
T1 = TypeVar("T1")

class LazyList(Iterable, Generic[T]):
    """
    Lazily evaluated immutable iterable object to which a number of transformations can be applied.
    """
    def __init__(self, *iterables: Iterable[T] | T):
        if len(iterables) == 1:
            if isinstance(iterables[0], Iterable):
                self._iterable = iterables[0]
            else:
                self._iterable = iterables
        else:
            def inner(iterables: tuple[Iterable[T] | T, ...]) -> Generator[T]:
                for iterable in iterables:
                    if isinstance(iterable, Iterable):
                        for el in iterable:
                            yield el
                    else:
                        yield iterable
            self._iterable = inner(iterables)
    
    @classmethod
    def naturals(cls) -> LazyList[int]:
        """
        Increasing sequence of natural numbers starting from 0.
        """
        def inner() -> Generator[int]:
            value = 0
            while True:
                yield value
                value += 1
        return LazyList(tee(inner())[1])
    
    @classmethod
    def repeat(cls, value: T, n: int | None = None) -> LazyList[T]:
        """
        Repeat a value n times. If n is None, the value will be repeated infinitely.
        """
        def inner(value: T, n: int | None) -> Generator[T]:
            i = 0
            while n is None or i < n:
                i += 1
                yield value
        return LazyList(tee(inner(value, n))[1])
    
    def cycle(self, n: int | None = None) -> LazyList[T]:
        """
        Cycle through a LazyList n times. If n is None, the LazyList will be cycled through infinitely.
        """
        def inner(lazyList: LazyList[T], n: int | None) -> Generator[T]:
            i = 0
            while n is None or i < n:
                i += 1
                for el in lazyList:
                    yield el
        return LazyList(tee(inner(self, n))[1])
    
    def __mul__(self, n: int) -> LazyList[T]:
        return self.cycle(n)
    
    def take(self, n: int) -> LazyList[T]:
        """
        Returns a LazyList with the n first items.
        """
        def inner( n: int, lazyList: LazyList[T]) -> Generator[T]:
            i = n
            for el in lazyList:
                if i <= 0:
                    break
                i -= 1
                yield el
        return LazyList(tee(inner(n, self))[1])
    
    def drop(self, n: int) -> LazyList[T]:
        """
        Returns a LazyList without the n first items.
        """
        def inner(n: int, lazyList: LazyList[T]) -> Generator[T]:
            i = n
            for el in lazyList:
                if i > 0:
                    i -= 1
                    continue
                yield el
        return LazyList(tee(inner(n, self))[1])

    def map(self, f: Callable[[T], T1]) -> LazyList[T1]:
        """
        Returns a LazyList with a function applied to all elements.
        """
        return LazyList(tee(f(el) for el in self)[1])
    
    def filter(self, f: Callable[[T], bool]) -> LazyList[T]:
        """
        Returns a LazyList containing only the elements for which a function returns True.
        """
        return LazyList(tee(el for el in self if f(el))[1])
    
    def reduce(self, f: Callable[[T, T], T], start: T | None = None) -> T | None:
        """
        Reduces an entire LazyList down to a single value using the supplied function. If applied on an infinite LazyList, this will loop infinitely and never return.
        """
        acc = start
        it = tee(self)[1]
        try:
            acc = next(it)
        except StopIteration:
            return acc
        for el in it:
            acc = f(acc, el)
        return acc
    
    def __eq__(self, other: LazyList[T]) -> bool:
        it = iter(other)
        for el in self:
            try:
                if el != next(it):
                    return False
            except StopIteration:
                return False
        try:
            next(it)
            return False
        except StopIteration:
            pass
        return True
    
    def concat(self, other: LazyList[T]) -> LazyList[T]:
        """
        Concatenates two LazyLists.
        """
        def inner(lla: LazyList[T], llb: LazyList[T]) -> Generator[T]:
            for el in lla:
                yield el
            for el in llb:
                yield el
        return LazyList(tee(inner(self, other))[1])
    
    def __add__(self, other: LazyList[T]) -> LazyList[T]:
        return self.extend(other)
    
    def __iter__(self) -> _LazyListIterator[T]:
        return _LazyListIterator(self)
    
    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        res = []
        it = tee(self._iterable)[1]
        try:
            for _ in range(10):
                res.append(next(it))
            next(it)
            isTruncated = True
        except StopIteration:
            isTruncated = False
        return f"LazyList({', '.join(repr(el) for el in res)}{', [...]' * isTruncated})"

class _LazyListIterator(Iterator, Generic[T]):
    def __init__(self, lazyList: LazyList[T]):
        self._iter = tee(lazyList._iterable)[1]
    
    def __next__(self):
        return next(self._iter)
