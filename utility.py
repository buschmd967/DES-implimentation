import random
from math import isqrt

def rabinExpMod(a, b, m):
    if b==0:
        return 1
    if(b%2 == 0):
        y = rabinExpMod(a, b//2, m)
        z = pow(y, 2, m)
        return z
    else:
        y = rabinExpMod(a, b-1, m)
        return (a*y) % m


# Taken from https://www.geeksforgeeks.org/primitive-root-of-a-prime-number-n-modulo-n/
def findPrimefactors(s, n) :
 
    # Print the number of 2s that divide n
    while (n % 2 == 0) :
        s.add(2)
        n = n // 2
 
    # n must be odd at this point. So we can 
    # skip one element (Note i = i +2)
    for i in range(3, int(sqrt(n)), 2):
         
        # While i divides n, print i and divide n
        while (n % i == 0) :
 
            s.add(i)
            n = n // i
         
    # This condition is to handle the case
    # when n is a prime number greater than 2
    if (n > 2) :
        s.add(n)



def isPrime(m, k):
    for i in range(k):
        a = random.randrange(1, isqrt(m))
        r = rabinExpMod(a, m, m) 
        if(r != (a % m)):
            return False
    return True

def pulverizer(phi, e, x1 = 1, y1 = 0, x2 = 0, y2 = 1):
    Q = phi // e
    R = phi % e
    newx2 = x1 - Q * x2
    newy2 = y1 - Q * y2
    if(R == 0):
        return (x2, y2)
    return pulverizer(e, R, x2, y2, newx2, newy2)

def gcd(a, b):
    if(b == 0):
        return a
    else:
        return gcd(b, a%b)