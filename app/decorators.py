from threading import Thread
from app import app
def async(some_function):

    def wrapper(*args, **kwargs):
        thr = Thread(target=some_function, args=args, kwargs=kwargs)
        thr.start()
    return wrapper