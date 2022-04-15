from operator import xor
import sys
from math import ceil
from typing import Dict, List
from des_tables import *


# Large help from https://page.math.tu-berlin.de/~kant/teaching/hess/krypto-ws2006/des.htm

def padBits(bits, l=64):
    while(len(bits) < l):
       bits = "0" + bits
    return bits

def permute(data: int, table:List[int], pad=64) -> int:
    out = []
    bits = bin(data)[2:]
    bits = padBits(bits, pad)
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
    key = bin(key)[2:]
    key = padBits(key, 56)
    # print(f"{key=}")

    upper = key[0:28]
    lower = key[28:]

    # print(f"{upper=} {lower=}")
    for i in range(16):
        upper, lower = shiftKeys(upper, lower, SHIFT[i])
        keys["C"].append(upper)
        keys["D"].append(lower)
        

    return keys
        

def getKeys(key: int) -> Dict:
    subkeys = getSubkeys(key)
    keys = []
    for i in range(16):
        key_concat = subkeys["C"][i] + subkeys["D"][i]
        key_concat_int = int(key_concat, 2)
        key_int = permute(key_concat_int, PC2, 56)
        key = padBits(bin(key_int)[2:], 48)
        keys.append(key)
    return keys
    
def S(input, box):
    input = padBits(bin(input)[2:], 6)
    i = input[0] + input[-1]
    i = int(i, 2)
    j = input[1:5]
    j = int(j, 2)
    out = box[i * 16 + j]
    out = padBits(bin(out).replace("0b",""), 4)
    return out

def f(right: str, key: str):
    right = permute(int(right, 2), ESEL, 32)
    # right = int(right, 2)
    key = int(key, 2)
    data_xor = xor(key, right)
    data = padBits(bin(data_xor)[2:], 48)
    out = ""
    for i in range(len(data)//6):
        box_in = data[i*6:(i+1)*6]
        box_out = S(int(box_in, 2), SBOXES[i])
        out += box_out
    return permute(int(out, 2), P, 32)
    
        


def getCiphertext(left: str, right: str, keys: List[str]) -> int:
    for i in range(16):
        newLeft = right
        f_out = f(right, keys[i])
        right = xor(int(left, 2), f_out)
        right = padBits(bin(right)[2:], 32)
        left = newLeft
    out = right + left
    print(out)
    out = permute(int(out, 2), IP_INV)
    return out

def messageToBlocks(message: str) -> List[int]:
    message = message.encode()
    chunkSize = 8

    blocks = []

    for i in range(ceil(len(message) / chunkSize)):
        chunk = message[chunkSize * i: chunkSize * i+chunkSize]
        block = int.from_bytes(chunk, byteorder='big')
        blocks.append(block)
        # blocks.append(1383827165325090801)
    
    return blocks
    

def encryptBlock(block: str, keys:Dict) -> int:

    
    


    
    ip = permute(block, IP)
    ip = padBits(bin(ip)[2:], 64)
    # print(bin(blocks[0]))
    # print(bin(p))
    upper = ip[:32]
    lower = ip[32:]
    ciphertext = getCiphertext(upper, lower, keys)
    
    
def encrypt(message: str, key:str):
    key = 1383827165325090801
    keys = getKeys(key)

    blocks = messageToBlocks(message)
    blocks = [81985529216486895]

    ciphertexts = []
    for block in blocks:
        ciphertexts.append(encryptBlock(block, keys))



def test():
    # print(padBits(bin(1383827165325090801).strip('0b')))
    keys = getKeys(1383827165325090801)
    # print(keys["C"])
    # print(keys["D"])
    print(keys)

if __name__ == "__main__":
    # test()
    encrypt("AAAAAAAA", "A")
