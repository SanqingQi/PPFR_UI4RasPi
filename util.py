import numpy as np
import random

Q = 23740629843760239486723
BASE = 2
PRECISION_INTEGRAL = 16
PRECISION_FRACTIONAL = 32

def share(secret):
    secret=secret * BASE ** PRECISION_FRACTIONAL #把小数转换为整数
    a1=Q*random.random()
    share_1=(secret+a1*1)%Q
    share_2=(secret+a1*2)%Q
    share_1=share_1.astype('float64')
    share_2=share_2.astype('float64')
    return share_1,share_2

def decode(share_1,share_2):
    result=share_1*2-share_2
    map_negative_range = np.vectorize(lambda element: element if element <= Q / 2 else element - Q)
    return map_negative_range(result) / BASE ** PRECISION_FRACTIONAL
