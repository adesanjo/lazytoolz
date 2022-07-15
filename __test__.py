from .lazytoolz.lazylist import LazyList

def main():
    print(LazyList(1).cycle().take(5) == LazyList.repeat(1).take(5))

if __name__ == "__main__":
    main()
