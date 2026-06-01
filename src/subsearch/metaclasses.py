class Singleton(type):
    _instances: dict[type, type] = {}

    def __call__(cls, *args, **kwargs) -> type:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
