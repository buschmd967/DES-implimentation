from typing import Tuple
from utility import *
from random import randrange



def doublePoint(P: Tuple[int, int], A: int, q: int) -> Tuple[int, int]:
    x1 = P[0]
    y1 = P[1]

    numerator = (3 * x1 * x1 + A) % q
    denominator = modInv(2 * y1, q)

    m = (numerator * denominator) % q

    x3 = (m * m - 2 * x1) % q
    y3 = -(y1 + m * (x3 - x1)) % q
    return (x3, y3)

def addPoint(P1, P2, q):
    x1 = P1[0]
    x2 = P2[0]
    y1 = P1[1]
    y2 = P2[1]

    numerator = (y2 - y1) % q
    denominator = modInv((x2 - x1) % q, q)
    m = (numerator * denominator) % q

    x3 = (m * m - (x1 + x2)) % q
    y3 = -(y1 + m * (x3 - x1)) % q

    return (x3, y3)

def modInv(e, q):
    out = pulverizer(q, e)[1]
    if(out < 0):
        out = out + q
    return out

def getFullmask(H: Tuple[int, int], N: int, A: int, q: int) -> Tuple[int, int]:
    out = (-1, -1)
    while(N > 0):
        if(N % 2 != 0):
            if out == (-1, -1):
                out = H
            else:
                if(out != H):
                    out = addPoint(out, H, q)
                else:
                    out = doublePoint(out, A, q)
            N -= 1
        else:
            N = N / 2
            H = doublePoint(H, A, q)
    return out

def getM(C: Tuple[int, int], F: Tuple[int, int], q: int):
    F = (F[0], -F[1])
    return addPoint(C, F, q)

def decrypt(C: Tuple[int, int], H: Tuple[int, int], N: int, A: int, q: int) -> Tuple[int, int]:
    F = getFullmask(H, N, A, q)
    return getM(C, F, q)

def test():
    q = 163
    A = 141
    B = 162
    G = (6, 88)
    P = doublePoint(G, A, q)
    C = (88, 71)
    H = (80, 7)
    N = 3
    print(decrypt(C, H, N, A, q))


if __name__ == "__main__":
    test()