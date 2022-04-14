import sys
from math import ceil
from typing import List
from des_tables import *


# Large help from https://page.math.tu-berlin.de/~kant/teaching/hess/krypto-ws2006/des.htm

def permute(data: int, table:List[int]) -> int:
    out = [0 for i in range(64)]
    bits = bin(data).strip('0b')
    while(len(bits) < 64):
       bits = "0" + bits
    for i in range(len(table)):
        out[table[i] - 1] = bits[i]
    outBits = "".join(out)
    return(int(outBits, 2))



def message_to_blocks(message: str) -> List[int]:
    message = message.encode()
    chunkSize = 8

    blocks = []

    for i in range(ceil(len(message) / chunkSize)):
        chunk = message[chunkSize * i: chunkSize * i+chunkSize]
        block = int.from_bytes(chunk, byteorder='big')
        blocks.append(block)
    
    return blocks
    

def encrypt(message: str, key:str):
    blocks = message_to_blocks(message)
    p = permute(blocks[0], IP)
    print(bin(blocks[0]))
    print(bin(p))
    pInv = permute(p, IP_INV)
    print(bin(pInv))



if __name__ == "__main__":
    encrypt("AAAAAAAA", "A")
