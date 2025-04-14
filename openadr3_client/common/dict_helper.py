from collections.abc import Callable
from typing import Dict

def union_with[K, V](merge_func: Callable[[V, V], V], first_dict: Dict[K, V], second_dict: Dict[K, V]):
    result = dict(first_dict)
    for key in second_dict:
        if first_value := result.get(key):
            result[key] = merge_func(first_value, second_dict[key])
        else:
              result[key] = second_dict[key]
    return result