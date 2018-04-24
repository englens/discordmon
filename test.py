import math
def answer(area):
    output = []
    current = int(math.floor(math.sqrt(area)))
    while(area > 0):
        if area - current**2 >= 0:
            output.append(current**2)
            area -= current**2
        if current > 1:
            current -= 1
    return output