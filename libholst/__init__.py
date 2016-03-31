__version__ = "0.9b"
__author__  = "Luis Rodil-Fernandez <root@derfunke.net>"


def from_lil_bytes(l):
    x = 0
    for i in range(len(l)-1, -1, -1):
        x <<= 8
        x |= l[i]
    return x

def from_big_bytes(l):
    x = 0
    for i in range(len(l)):
        x <<= 8
        x |= l[i]
    return x
