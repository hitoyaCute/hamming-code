# hamming code
from typing import Any
from random import randrange as Rrange
import random
import json
# with open("random state.json","w") as file:
#     json.dump(random.getstate(),file)
with open("random state.json","r") as file:
    random.setstate(tuple([tuple(dat) if isinstance(dat,(tuple,list)) else dat for dat in json.load(file)]))

def main() -> None:
    # exit()
    data = 101010101010101010101010101010101010101010101010101010101010101010101010101019
    #creates error resistant data
    data = generate(data)
    print(data,"healty data")

    #perform n random bit flip

    #count of times to perform bit flip
    n = 5
    le = len(bin(data)[3:])
    le += 16-(le%16) if le%16 else 0
    for _ in range(n):
        data = bin(data)[3:]
        data = int("1"+bit_flip(data,le),2)
    print(data,"faulty data")

    #try to correct the data
    print(retrieve(data),end="\n\n\n")

def generate(data:int) -> str:
    """generate a error ressistant data"""
    #convert to workable binary
    data = list(bin(data)[2:])[::-1]
    #slice into chunks
    data = wrap(data ,11)

    outp = []

    #process
    le = len(data)-1
    for i,chunk in enumerate(data):
        #prepare the blanks
        if le != i:
            chunk = list_rjust([int(x) for x in list(chunk)],11,0)
        else:
            chunk = list_ljust([int(x) for x in list(chunk)],11,0)
        a,*chunk = chunk
        b = poprange(chunk,0,3)
        c = poprange(chunk,0,3)
        d = chunk
        chunk = [
            [0,0,0,a],
            [0] + b  ,
            [0] + c  ,
                d     ]
        chunk[2][0] = sum(chunk[2]+chunk[3])%2
        chunk[1][0] = sum(chunk[1]+chunk[3])%2
        chunk2 = rotate_matrix(chunk)
        chunk[0][2] = sum(chunk2[0]+chunk2[1])%2
        chunk[0][1] = sum(chunk2[0]+chunk2[2])%2
        chunk[0][0] = sum(list_flat(chunk))%2
        outp.append("".join([str(i) for l in chunk for i in l]))
    le = len(outp)
    dat = "".join(["1"]+[outp[i][j] for j in range(16) for i in range(le)])
    return int(dat,2)
"""
chunk    chunk 2
a 123b   bbbb   0011  0011
b 4bbb   3bbb   0101  0100
c 5bbb   2bbb   1111  1111
d bbbb   145b   0110  0110
"""
def retrieve(data:int) -> int:
    """check the data for correction and return a error free data"""
    data = bin(data)[3:]
    le = len(data)
    le += 16-(le%16) if le%16 else 0

    data = wrap([int(x) for x in data],le//16)
    data = [[data[j][i] for j in range(16)] for i in range(le//16)]
    print(int("".join([str(dat) for x in data for dat in x]),2),le/16)

    outp = []
    for i,chunk in enumerate(data):
        chunk = wrap(chunk,4)
        chunk90 = rotate_matrix(chunk)
        
        #perform a test
        test5 = chunk[2][0] != (sum(chunk[2]+chunk[3]) - chunk[2][0])%2
        test4 = chunk[1][0] != (sum(chunk[1]+chunk[3]) - chunk[1][0])%2
        test3 = chunk[0][2] != (sum(chunk90[0]+chunk90[1]) - chunk[0][2])%2
        test2 = chunk[0][1] != (sum(chunk90[0]+chunk90[2]) - chunk[0][1])%2
        

        er = [int(x) for x in (test2,test3,test4,test5)]
        if sum(er):
            
            y = er[0]+(er[1]*2)
            x = er[2]+(er[3]*2)
            matrix_print(chunk)

            chunk[x][y] ^= 1
            chunk90 = rotate_matrix(chunk)

            finalcheck = (
            chunk[2][0] != (sum(chunk[2]+chunk[3]) - chunk[2][0])%2 or
            chunk[1][0] != (sum(chunk[1]+chunk[3]) - chunk[1][0])%2 or
            chunk[0][2] != (sum(chunk90[0]+chunk90[1]) - chunk[0][2])%2 or
            chunk[0][1] != (sum(chunk90[0]+chunk90[2]) - chunk[0][1])%2)
            print(x,y,chunk[0][0] != (sum(list_flat(chunk)) - chunk[0][0])%2,finalcheck,er ,end=" ,")
            # matrix_print(chunk)
            if (chunk[0][0] != (sum(list_flat(chunk)) - chunk[0][0])%2 and finalcheck) or finalcheck:
                print()
                matrix_print(chunk)
                
                raise Exception(f"there so manny issue on {i} that seems to be hard to fix")
        chunk = list_flat(chunk)
        for i in (8,4,2,1,0):
            del chunk[i]
        outp.extend(["1" if x else "0" for x in chunk])
    # print(outp,int("10",2),bin(2))
    return int("".join(outp[::-1]),2)
        


# helper functions
def bit_flip(s:bin,le=0) -> bin:
    """performs 1 random bit flip"""
    s = [int(x) for x in s.rjust(le,"0")]
    i = Rrange(0,len(s))
    s[i] ^= 1
    # print("flipped:",i)
    return "".join([str(a) for a in s])
def matrix_print(matrix:list[list[Any]]):
    """just for debugging porpose"""
    for vertex in matrix:
        for item in vertex:
            print(item,end=" ")
        print()
def rotate_matrix(mat:list[list[Any]]):
    in_y = len(mat)
    in_x = len(mat[0])

    outMatrix = [ [0] * in_y for _ in range(in_x) ]
    for y in range(in_y):
        for x in range(in_x):
            outMatrix[in_x - x-1][y] = mat[y][x]
    return outMatrix
def poprange(lst:list[Any],start:int,end:int=None) -> list[Any]:
    if end == None:
        end = len(lst)
    outp = lst[start:end]
    del lst[start:end]
    return outp
def wrap(items:list ,n:int) -> list[list[Any]]:
    """wrap for list"""
    x = 0
    out = []
    for i in range(0, len(items), n):
        out.append(items[x:i+n])
        x = i+n

    le = len(out)
    # del items[le:]
    # for i in range(le):
    #     items[i] = out[i]
    return out #len(out[-1]) != n
def list_rjust(items:list ,n:int ,filler = 0):
    re = n - len(items)
    if re > 0:
        items = [filler]*re + items
    return items
def list_ljust(items:list ,n:int ,filler = 0):
    re = n - len(items)
    if re > 0:
        items.extend([filler]*re)
    return items
def list_flat(lst:list[list[Any]]) -> list[Any]:
    out = []
    for lis in lst.copy():
        out.extend(lis)
    return out


if __name__ == "__main__":
    main()
