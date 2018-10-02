import math

def scaling7(value):
    
    tanhData =math.tanh((value-20)*0.03)
    result = (tanhData + 1) * 20

    return result
