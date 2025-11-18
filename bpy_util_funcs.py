# Credits: Dodylectable
def invert_uv_map(uv_set: tuple[float, float]) -> tuple[float, float]:
    return (uv_set[0], 1 - uv_set[1])