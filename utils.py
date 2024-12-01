import decorator
import time

@decorator.decorator
def timeit(func, *args, **kwargs):
    start = time.time()
    try:
        return func(*args, **kwargs)
    except Exception as e:
        raise e
    finally:
        end = time.time()
        print(f'[{func.__name__}] took {end - start:.2f} seconds')
