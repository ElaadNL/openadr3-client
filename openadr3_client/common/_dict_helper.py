from collections.abc import Callable


def union_with[K, V](on_collision: Callable[[V, V], V], first_dict: dict[K, V], second_dict: dict[K, V]) -> dict[K, V]:
    """Merges two dictionaries, if a key collision occurs, the func is used to resolve it."""
    result = dict(first_dict)
    for key, value in second_dict.items():
        if first_value := result.get(key):
            result[key] = on_collision(first_value, value)
        else:
            result[key] = value
    return result
