from icecream import ic
import time


class Callcounter:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        ic(f"Function '{self.func.__name__}' has been called {self.count} times.")
        return self.func(*args, **kwargs)


class Cache:
    def __init__(self, func):
        self.func = func
        ic("init")
        

    def __call__(self, *args, **kwargs):
        ic("call")
        key = (args, frozenset(kwargs.items()))
        ic(key)
        if key in self.cache:
            ic("Cache hit")
            return self.cache[key]
        else:
            result = self.func(*args, **kwargs)
            self.cache[key] = result
            self.history.append(("calc",args, kwargs, self))
        return result
    

        

@Cache
def complicated_calculation(x):
    print(f"Performing complicated calculation for {x}...")
    return x * x

result = complicated_calculation(5)
print(f"Result: {result}")

  
