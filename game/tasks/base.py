class Task():
    pass


#TODO consider using metaclass
def register(cls):
    """decorator that allows to automatically register given class as a new task"""
    cls.register()
    return cls
