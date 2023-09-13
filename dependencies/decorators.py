import time


def log_outputs(func):
    def wrapper(*args, **kwargs):
        outputs_path = "outputs"
        output = func(*args, **kwargs)
        filename = f'{outputs_path} {func.__name__} {time.ctime().replace(":", "-")}.txt'
        with open(filename, 'w') as file:
            file.write(str(output))
        return output
    return wrapper


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        output = func(*args, **kwargs)
        end_time = time.time()
        print(f'function {func.__name__} finished in {end_time-start_time} seconds')
        return output
    return wrapper
