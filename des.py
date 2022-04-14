import sys
from math import ceil
from typing import Dict, List
from des_tables import *


# Large help from https://page.math.tu-berlin.de/~kant/teaching/hess/krypto-ws2006/des.htm

def padBits(bits, l=64):
    while(len(bits) < l):
       bits = "0" + bits
    return bits

def permute(data: int, table:List[int]) -> int:
    out = []
    bits = bin(data).strip('0b')
    bits = padBits(bits)
    for i in range(len(table)):
        out.append(bits[table[i]-1])
    outBits = "".join(out)
    return(int(outBits, 2))

def shiftKeys(upper, lower, n):
    for i in range(n):
        upper = upper[1:] + upper[0]
        lower = lower[1:] + lower[0]
    return upper, lower


def getSubkeys(key: int) -> Dict:
    keys = {"C":[], "D":[] }
    key = permute(key, PC1)
    key = bin(key).strip('0b')
    key = padBits(key, 56)
    print(f"{key=}")

    upper = key[0:28]
    lower = key[28:]

    print(f"{upper=} {lower=}")
    for i in range(16):
        keys["C"].append(upper)
        keys["D"].append(lower)
        upper, lower = shiftKeys(upper, lower, SHIFT[i])

    return keys
        





def message_to_blocks(message: str) -> List[int]:
    message = message.encode()
    chunkSize = 8

    blocks = []

    for i in range(ceil(len(message) / chunkSize)):
        chunk = message[chunkSize * i: chunkSize * i+chunkSize]
        block = int.from_bytes(chunk, byteorder='big')
        blocks.append(block)
        # blocks.append(1383827165325090801)
    
    return blocks
    

def encrypt(message: str, key:str):
    blocks = message_to_blocks(message)
    # p = permute(blocks[0], IP)
    # print(bin(blocks[0]))
    key = 1383827165325090801
    getSubkeys(key)
    # print(bin(p))
    # pInv = permute(p, IP_INV)
    # print(bin(pInv))


def test():
    print(padBits(bin(1383827165325090801).strip('0b')))
    keys = getSubkeys(1383827165325090801)
    print(keys["C"])
    print(keys["D"])

if __name__ == "__main__":
    test()
    # encrypt("AAAAAAAA", "A")
