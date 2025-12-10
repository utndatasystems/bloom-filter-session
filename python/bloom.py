bloom_store = set()


def insert(value: str) -> bool:
    """Insert a value into the in-memory set."""
    bloom_store.add(str(value))
    return True


def lookup(value: str) -> bool:
    """Return True if the value is present."""
    return str(value) in bloom_store
