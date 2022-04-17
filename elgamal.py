from math import ceil
from pydoc import plain
from typing import Tuple
from utility import *
import random

# returns safe prime
def getPrime(k):
    upper = pow(2, k+1)
    lower = (upper >> 2) + 1 #make sure it's odd
    
    p = random.randrange(lower, upper, 2)
    print("Finding p ", end="")
    while(not isPrime(p, k) and p < upper and p >= lower and (p-1) % 2 == 0):
        p = random.randrange(lower, upper, 2)
        while(p % 5 == 0):
            p = random.randrange(lower, upper, 2)
        print(".", end="", flush=True)
    print()
    return p


def getGenerator(p):
    guess = random.randrange(1, p)
    q = (p-1)//2
    while True:
        if(guess%p == 1 or guess%p == -1 or pow(guess, q, p) == 1):
            guess = random.randrange(1, p)
        else:
            break
    return guess

def getSecretExponent(p):
    return random.randrange(2, p)

def getPublicValue(generator, secret, p):
    return pow(generator, secret, p)
    
def getKeys(k):
    p = getPrime(k)
    g = getGenerator(p)
    b = getSecretExponent(p)
    a = getPublicValue(g, b, p)
    return p, g, b, a





def encrypt(message: int, a: int, g: int, p: int):
    B = getSecretExponent(p)
    halfmask = pow(g, B, p)
    fullmask = pow(a, B, p)
    y = (message * fullmask) % p
    return(y, halfmask)

def decrypt(y, b, halfmask, p):
    fullmask = pow(halfmask, b, p)
    return (y * modInv(fullmask, p)) % p


def encryptMessage(message: str, k: int):
    p, g, b, a = getKeys(k)
    m = message.encode()
    m = int.from_bytes(m, byteorder='big')
    return {"secret": b, "public": (p, encrypt(m, a, g, p))}


# Takes in c, of form: (prime, (cipher, halfmask))
def decryptMessage(c: Tuple[int, Tuple[int, int]], b: int):
    p, (c, halfmask) = c
    m = decrypt(c, b, halfmask, p)
    byteNumber = ceil(len(bin(m).replace("0b", "")) / 8)
    plaintext_bytes = m.to_bytes(byteNumber, byteorder='big')
    return plaintext_bytes.decode()

def test():
    message = "ABCD"

    for i in range(100):
        c = encryptMessage(message, 32)
        b = c["secret"]
        c = c["public"]
        if(message != decryptMessage(c, b)):
            print("Error")
            break
    


if __name__ == "__main__":
    test()