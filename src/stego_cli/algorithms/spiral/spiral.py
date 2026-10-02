def spiral_coords(width, height):
    left, right = 0, width - 1
    top, bottom = 0, height - 1
    while left <= right and top <= bottom:
        for x in range(left, right + 1):
            yield (x, top)
        top += 1
        for y in range(top, bottom + 1):
            yield (right, y)
        right -= 1
        if top <= bottom:
            for x in range(right, left - 1, -1):
                yield (x, bottom)
            bottom -= 1
        if left <= right:
            for y in range(bottom, top - 1, -1):
                yield (left, y)
            left += 1