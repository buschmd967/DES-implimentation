from multiprocessing.sharedctypes import Value
from operator import xor
from socket import socket
import sys
from math import ceil
from tkinter import getint
from typing import Dict, List, Tuple
from des_tables import *
from time import sleep


# Large help from https://page.math.tu-berlin.de/~kant/teaching/hess/krypto-ws2006/des.htm

# Get binary string to be expected length
def padBits(bits, l=64):
    while(len(bits) < l):
       bits = "0" + bits
    return bits

# Change data to binary string, then permute given table from des_tables.py
def permute(data: int, table:List[int], pad=64) -> int:
    out = []
    bits = bin(data)[2:]
    bits = padBits(bits, pad)
    for i in range(len(table)):
        out.append(bits[table[i]-1])
    outBits = "".join(out)
    return(int(outBits, 2))

# Shift start bit of binary string to end
def shiftKeys(upper: str, lower: str, n: int) -> Tuple[str, str]:
    for i in range(n):
        upper = upper[1:] + upper[0]
        lower = lower[1:] + lower[0]
    return upper, lower

# Get C0 - C15 and D0 - D15. Notation taken from DES writeup noted above
def getSubkeys(key: int) -> Dict[str, List[str]]:
    keys = {"C":[], "D":[] }
    key = permute(key, PC1)
    key = bin(key)[2:]
    key = padBits(key, 56)

    # Split into upper and lower halves
    upper = key[0:28]
    lower = key[28:]

    # Shift and add to corresponding list
    for i in range(16):
        upper, lower = shiftKeys(upper, lower, SHIFT[i])
        keys["C"].append(upper)
        keys["D"].append(lower)
        
    return keys
        
# Take string key and convert to usable int. Truncates key to first 4 characters, as DES takes in 64-bit key
def getIntKey(key:str) -> int:
    key_trunc = key[:4]
    key_enc = key_trunc.encode()
    return int.from_bytes(key_enc, byteorder='big')

# Generate keys for encryption + decryption from integer key
def getKeys(key: int) -> Dict:
    subkeys = getSubkeys(key)
    keys = []
    for i in range(16):
        #concat upper and lower parts
        key_concat = subkeys["C"][i] + subkeys["D"][i]
        #change to integer for permute function
        key_concat_int = int(key_concat, 2)
        #permute using PC2
        key_int = permute(key_concat_int, PC2, 56)
        #format and append to keys
        key = padBits(bin(key_int)[2:], 48)
        keys.append(key)
    return keys

# Sbox function
def S(input, box) -> str:
    input = padBits(bin(input)[2:], 6)
    i = input[0] + input[-1]
    i = int(i, 2)
    j = input[1:5]
    j = int(j, 2)
    out = box[i * 16 + j]
    out = padBits(bin(out).replace("0b",""), 4)
    return out

# fbox function
def f(right: str, key: str)-> int:
    right = permute(int(right, 2), ESEL, 32)
    key = int(key, 2)
    data_xor = xor(key, right)
    data = padBits(bin(data_xor)[2:], 48)
    out = ""
    for i in range(len(data)//6):
        #break into 6-bit chunks
        box_in = data[i*6:(i+1)*6]
        #perform corresponding sbox function (returns string of bits)
        box_out = S(int(box_in, 2), SBOXES[i])
        out += box_out
    return permute(int(out, 2), P, 32)
    
# main xor chain. Since the only difference between encrypting and decrypting 
# is the order in which the sboxes are applied, a reverse flag is used to distinguish
def xorChain(left: str, right: str, keys: List[str], reverse=False) -> int:
    for i in range(16):

        # perform fbox operation
        if(reverse):
            f_out = f(right, keys[15-i])
        else:
            f_out = f(right, keys[i])
        
        newLeft = right
        right = xor(int(left, 2), f_out)
        right = padBits(bin(right)[2:], 32)
        left = newLeft
    out = right + left
    return out


# convert string message to list of 64-bit integers
def messageToBlocks(message: str) -> List[int]:
    message = message.encode()
    chunkSize = 8

    blocks = []

    for i in range(ceil(len(message) / chunkSize)):
        chunk = message[chunkSize * i: chunkSize * i+chunkSize]
        block = int.from_bytes(chunk, byteorder='big')
        blocks.append(block)
    
    return blocks
    
# convert list of 64-bit integers back to human-readable string. Returns None if it encounteres an error
# (error usually caused by incorrect key)
def blocksToMessage(blocks: List[int]) -> str:
    message = ""
    for block in blocks:
        bytes = block.to_bytes(8, byteorder='big')
        try:
            message += bytes.decode()
        except UnicodeDecodeError:
            return None
    return message

# encrypt integer block of message
def encryptBlock(block: int, keys:Dict) -> int:
    #permute using Initial Permutation table
    ip = permute(block, IP)
    ip = padBits(bin(ip)[2:], 64)

    #get upper and lower halves
    upper = ip[:32]
    lower = ip[32:]

    #do main part of DES
    ciphertext = xorChain(upper, lower, keys)

    #undo initial permutation
    return permute(int(ciphertext, 2), IP_INV)


# encrypt entire message by splitting into blocks, then encrypting each block
def encrypt(message: str, key:str):
    # get keys first
    keys = getKeys(getIntKey(key))
    #convert message into 64-bit integers
    blocks = messageToBlocks(message)

    ciphertexts = []
    for block in blocks:
        #encrypt each block
        ciphertexts.append(encryptBlock(block, keys))
        
    return ciphertexts

# decrypt single block
def decryptBlock(block:int, keys:Dict) -> int:
    # perform Initial Permutation
    ip = permute(block, IP)
    ip = padBits(bin(ip)[2:], 64)

    # Get halves
    upper = ip[:32]
    lower = ip[32:]

    # Do main DES
    decrypted = xorChain(upper, lower, keys, True)

    #undo initial permutation
    return permute(int(decrypted, 2), IP_INV)

# given list of blocks, convert into plaintext message
def decrypt(blocks:List[int], key: str) -> str:
    #Get keys
    keys = getKeys(getIntKey(key))

    outBlocks = []
    for block in blocks:
        # decrypt each block
        outBlocks.append(decryptBlock(int(block), keys))
    
    #convert to plaintext message
    message = blocksToMessage(outBlocks)
    if(message == None):
        # message is none if the decrypted blocks are not valid ascii characters
        message = "ERROR: message not in ascii format. Is your key correct?"
    return message

def getDesMessage(s: socket, key):
    # print("recieving numOfBlocks")
    d = s.recv(1024).decode()
    possibleNumOfBLocks = d.split("|")[0]
    # print(f"got d: {possibleNumOfBLocks}")
    numOfBlocks = decrypt([int(possibleNumOfBLocks)], key).replace("\x00", "")
    numOfBlocks = int(numOfBlocks)
    # print(numOfBlocks)
    # print(f"in getDESMESSAGE: {data=}")

    strblocks = d
    while(len(strblocks.split("|")) < numOfBlocks+1):
        chunk = s.recv(1024).decode()
        strblocks += chunk
        # print(f"blocks recieved so far: {len(strblocks.split('|'))} / {numOfBlocks}")
    # print("Got all blocks")

    blocks = []
    splitBlocks = strblocks.split('|')
    for i in range(len(splitBlocks)):
        if i != 0:
            b = splitBlocks[i]
            if(b != ""):
                blocks.append(b)
    
    message = decrypt(blocks, key)

    message = message.replace("\x00", "")
    return message

def sendDESMessage(s: socket, message: str, key: str):
    if(message[-1] != "\n"):
        message += "\n"
    blocks = encrypt(message, key)
    numOfBlocks = len(blocks) + 1
    # print(f"blocks to send: {blocks}")
    # print(f"numOfBlocks: {numOfBlocks}")
    m = encrypt(str(numOfBlocks), key)[0]
    m = (str(m) + "|").encode()
    # print(f"sending encrypted numOfBytes: {m}")
    s.send(m)
    for block in blocks:
        m = (str(block) + "|").encode()
        # print(f"sending block: {m}")
        s.send(m)
    # print("all blocks sent")


def test():
    # ciphertexts = encrypt("guest\n", "ABCD")
    # print(ciphertexts)
    print(decrypt([3995267046004588734, 9252507308338199152, 10278278148011571393], "ABCD"))
    # message = decrypt(ciphertexts, "ABCD")
    # print(message)


if __name__ == "__main__":
    # encrypt("AAAAAAAA", "A")
    test()

