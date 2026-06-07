class Singleton(type):
    _instance_registry: dict[type, type] = {}

    def __call__(cls, *args, **kwargs) -> type:
        if cls not in cls._instance_registry:
            cls._instance_registry[cls] = super().__call__(*args, **kwargs)
        return cls._instance_registry[cls]
