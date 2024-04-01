
def operate(func):
    def wrapper(*args, **kwargs):
        try:
            print(func.__name__, " is operating...")
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None

    return wrapper


@operate
def work(a, b):
    return a + b


if __name__ == '__main__':
    print(operate(work)("Alex", "b"))

