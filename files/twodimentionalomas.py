from copy import deepcopy
from functools import lru_cache
import random

def flip(piece):
    return tuple(tuple(ball for ball in row[::-1]) for row in piece)

def rotate(piece, rotations):
    for _ in range(rotations):
        lengthy = len(piece)
        lengthx = len(piece[0])
        piece = tuple(tuple(piece[j][lengthx-i-1] for j in range(lengthy)) for i in range(lengthx))
    return piece

def possibilitiesperpiece(piece):
    flippedpiece = flip(piece)
    possibilities = []
    for i in range(4):
        possibilities.append(rotate(piece,i))
        possibilities.append(rotate(flippedpiece,i))
    possibilities = tuple(set([rotation for rotation in possibilities if calculateoffset(rotation) != None]))
    return possibilities

def allpieces(pieces):
    return tuple(possibilitiesperpiece(piece) for piece in pieces)

def putpieceonboard(board, piece, x, y):
    if x < 0 or y < 0: return False
    tempboard = deepcopy(board)
    for i, row in enumerate(piece):
        for j, el in enumerate(row):
            try:
                if tempboard[i+y][j + x]*el:
                    return False
                else:
                    tempboard[i+y][j + x] += el
            except:
                return False
    return tempboard

@lru_cache(128)
def calculateoffset(piece):
    for i in range(len(piece)):
        if piece[i][0] == 1:
            return i    

def buildstartposition(board, pieces, usedpieces, datausedpieces):
    for pieceindex,data in zip(usedpieces,datausedpieces):
        piece = rotate(pieces[pieceindex],data[2]//2)
        if data[2] % 2 == 1:
            piece = flip(piece)
        offset = calculateoffset(piece)
        board = putpieceonboard(board,piece,data[0],data[1]-offset)
        if not board:
            print("Wrong starting position!")
            exit()
    return board

def findnextzero(board, lastzero):
    for i in range(lastzero // 5, 12):
        for j in range(5):
            if board[j][i] == 0:
                return i * 5 + j

def findsolution(board, allpieces, usedpieces, datausedpieces, lastzero):
    if len(usedpieces) == 12:
        return
    for i,shape in enumerate(allpieces):
        if i in usedpieces:
            continue
        else:
            for j,rotation in enumerate(shape):
                test = putpieceonboard(board, rotation, lastzero // 5, (lastzero % 5) - calculateoffset(rotation))
                if type(test) == list:
                    usedpieces.append(i)
                    datausedpieces.append([lastzero // 5, lastzero % 5, j])
                    newzero = findnextzero(test, lastzero)
                    findsolution(test, allpieces, usedpieces, datausedpieces, newzero)
                    if len(usedpieces) == 12:
                        return
                    else:
                        usedpieces.pop()
                        datausedpieces.pop()
    else:
        return 
  
def showsolution(pieces, usedpieces, datausedpieces, startpieces, allpieces, offset = 0):
    tempboard = [[0 for _ in range(12)] for _ in range(5)]
    for h,pieceindex in enumerate(usedpieces):
        if pieceindex in startpieces:
            piece = rotate(pieces[pieceindex], datausedpieces[h][2]//2)
            if datausedpieces[h][2] % 2 == 1:
                piece = flip(piece)
        else:
            piece = allpieces[pieceindex][datausedpieces[h][2]]
        pieces[pieceindex] = piece
        x = datausedpieces[h][0]
        y = datausedpieces[h][1] - calculateoffset(piece)
        for i, row in enumerate(piece):
            for j, el in enumerate(row):
                tempboard[i+y][j + x] += el*(pieceindex + offset)
    return tempboard
    
def preamble(board, pieces, usedpieces, datausedpieces, offset = 0):
    allpieces = [possibilitiesperpiece(piece) for piece in pieces]
    board = buildstartposition(board, pieces, usedpieces, datausedpieces)
    startpieces = usedpieces.copy()
    findsolution(board, allpieces, usedpieces, datausedpieces, findnextzero(board,0))
    solution = showsolution(pieces,usedpieces,datausedpieces, startpieces, allpieces, offset)
    return solution

def getpieces():
    pieces = (((1,0,0),(1,1,1),(0,0,1)), 
            ((1,0,0),(1,1,1),(1,0,0)),
            ((0,1,0),(1,1,1),(1,0,0)), 
            ((1,1,1),(1,1,0)), 
            ((1,1,1),(1,0,1)), 
            ((0,1,0),(1,1,1),(0,1,0)), 
            ((1,1,1),(1,0,0),(1,0,0)), 
            ((1,1,0),(0,1,1),(0,0,1)),  
            ((1,0),(1,0),(1,1),(0,1)), 
            ((1,0),(1,0),(1,1),(1,0)), 
            ((1,0),(1,0),(1,0),(1,1)), 
            ((1,),(1,),(1,),(1,),(1,)),
    )
    return pieces

def colors():
    return ((200,200,200), #0
            (100,255,100), #1
            (255,165,000), #2
            (255,000,000), #3
            (255,255,000), #4
            (150,150,150), #5
            (000,255,255), #6
            (255,000,255), #7
            (100,000,100), #8
            (255,200,200), #9
            (000,000,255), #10
            (000,150,000), #11
            )

def board():
    board = [[0 for _ in range(12)] for _ in range(5)]
    return board

def generaterandomsolution(offset = 0):
    usedpieces = []
    datausedpieces = []
    pieces = list(getpieces())
    orderpieces = list(zip(list(range(len(pieces))), pieces))
    random.shuffle(orderpieces)
    pieces = [item[1] for item in orderpieces]
    orderpieces = [item[0] for item in orderpieces]
    solution = preamble(board(), pieces, usedpieces, datausedpieces, offset)
    return (solution, pieces, usedpieces, datausedpieces, orderpieces)

if __name__ == '__main__':
    # usedpieces = [9,0,2,11,3,8,5,1]
    # datausedpieces = [[0,0,0],[0,4,1],[1,0,0],[2,1,2],[2,2,5],[2,4,2],[4,2,0],[7,0,0]]

    # usedpieces = [3]
    # datausedpieces = [[0,0,0]]
    # pieces = list(pieces())
    # solution = preamble(board(), pieces, usedpieces, datausedpieces)
    solution, _,_,_,_ = generaterandomsolution()
    form = '{:4}'*12
    print(*[form.format(*i) for i in solution], sep='\n')