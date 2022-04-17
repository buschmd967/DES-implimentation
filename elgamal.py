from utility import *
import random

def getPrime(k):
    upper = pow(2, k+1)
    lower = (upper >> 2) + 1 #make sure it's odd
    
    p = random.randrange(lower, upper, 2)
    print("Finding p ", end="")
    while(not isPrime(p, k)):
        p = random.randrange(lower, upper, 2)
        while(p % 5 == 0):
            p = random.randrange(lower, upper, 2)
        print(".", end="", flush=True)
    print()
    return p


# Taken from https://www.geeksforgeeks.org/primitive-root-of-a-prime-number-n-modulo-n/
# def getGenerator(p):
    # TODO
    


def test():
    # p = getPrime(4)
    p = 19
    a = []
    for i in range(500):
        x = getGenerator(p)
        if x not in a:
            a.append(x)
    a.sort()
    print(a)

if __name__ == "__main__":
    test()