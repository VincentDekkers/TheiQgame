import cv2
import numpy as np
import files.twodimentional as twodimentional
import time as t

def update(x,y,selected, pieces, grid):
    if selected[1]:
        selected[1] = 0
        arr[732:759,908:1180] = (255,255,255)
    if (200< y < 500):
        newselected = 2*(x // 200) + (y-200) // 150
        if newselected not in placedpieces:
            removepiecefromscreen(arr, 200*(x//200), 150*((y-200)//150)+200, 200, 150, (255,255,255))
            if newselected == selected[0]:
                putpieceonscreen(arr, pieces[newselected],200*(x//200)+5, 150*((y-200)//150)+205, 35,35, 4,(0,0,0), colors[newselected])
                selected[0] = -1
            elif selected[0] == -1:
                putpieceonscreen(arr, pieces[newselected],200*(x//200)+5, 150*((y-200)//150)+205, 35,35, 4,(0,0,150),colors[newselected])
                selected[0] = newselected
            else:
                removepiecefromscreen(arr, 200*(selected[0]//2), 150*(selected[0]%2)+200, 200,150,(255,255,255))
                putpieceonscreen(arr, pieces[newselected],200*(x//200)+5, 150*((y-200)//150)+205, 35,35, 4,(0,0,150),colors[newselected])
                putpieceonscreen(arr, pieces[selected[0]],200*(selected[0]//2)+5, 150*(selected[0]%2)+205, 35,35, 4,(0,0,0), colors[selected[0]])
                selected[0] = newselected
    elif (325<x<874) and (501<y<749):
        xlocation = (x-325)//50
        ylocation = (y-500)//50
        if selected[0] != -1:
            test = twodimentional.putpieceonboard(grid, pieces[selected[0]],xlocation,ylocation)
            if type(test) == list:
                placedpieces.append(selected[0])
                if len(placedpieces) == 12 and level[0] != -1:
                    stop = t.time()
                    time = stop - level[1]
                    if time < records[level[0]]:
                        records[level[0]] = time
                        printcolor = (0,200,0)
                        writebesttimes(records)
                    else:
                        printcolor = (0,0,200)
                    cv2.putText(arr, f'{time:.2f}',(50,775),cv2.FONT_HERSHEY_SIMPLEX,2,printcolor,2)
                    for item in placedpieces:
                        if item not in itemsinlevel:
                            itemsinlevel.append(item)
                test = twodimentional.putpieceonboard(twodimentional.board(), pieces[selected[0]],xlocation,ylocation)
                addmatrices(grid, test, selected[0])
                putgridonscreen(arr, grid, colors, 4, 325, 500, 50, 50, (255,255,255))
                removepiecefromscreen(arr, 200*(selected[0]//2), 150*(selected[0]%2)+200, 200,150,(255,255,255))
                selected[0] = -1 
            else:
                removeditem = grid[ylocation][xlocation]
                if removeditem != 0:
                    removedindex = removeditem - 10
                    removefrommatrix(grid, removeditem)
                    placedpieces.remove(removedindex)
                    putgridonscreen(arr, grid, colors, 4, 325, 500, 50, 50, (255,255,255))
                    putpieceonscreen(arr, pieces[removedindex],200*(removedindex//2)+5, 150*(removedindex%2)+205, 35,35, 4,(0,0,150), colors[removedindex])
                    removepiecefromscreen(arr, 200*(selected[0]//2), 150*(selected[0]%2)+200, 200,150,(255,255,255))
                    putpieceonscreen(arr, pieces[selected[0]],200*(selected[0]//2)+5, 150*(selected[0]%2)+205, 35,35, 4,(0,0,0), colors[selected[0]])
                    selected[0] = removedindex
                    if removedindex in itemsinlevel:
                        endlevel(arr, level)
        else:
            removeditem = grid[ylocation][xlocation]
            if removeditem != 0:
                removedindex = removeditem - 10
                removefrommatrix(grid, removeditem)
                placedpieces.remove(removedindex)
                putgridonscreen(arr, grid, colors, 4, 325, 500, 50, 50, (255,255,255))
                putpieceonscreen(arr, pieces[removedindex],200*(removedindex//2)+5, 150*(removedindex%2)+205, 35,35, 4,(0,0,150), colors[removedindex])
                selected[0] = removedindex
                if removedindex in itemsinlevel:
                    endlevel(arr, level)
    elif (940<x<1120) and (650<y<710):
        solve(arr, grid, pieces, placedpieces)
        putgridonscreen(arr, grid, colors, 4, 325, 500, 50, 50, (255,255,255))
        endlevel(arr, level)
    elif (940<x<1120) and (550<y<610):
        clear(arr, pieces, grid, colors, selected, placedpieces, itemsinlevel)
        endlevel(arr, level)
    elif (140<y<190) and (115<x<1085):
        button = (x-115)//200 if (x-115)%200<170 else -1
        if button != -1:
            clear(arr, pieces, grid, colors, selected, placedpieces, itemsinlevel)
            endlevel(arr,level)
            solution, newpcs, orderpcs, datanewpcs, ordernewpcs = twodimentional.generaterandomsolution(10)
            for _ in range(2*button+2):
                datanewpcs.pop()
                removefrommatrix(solution, orderpcs.pop() + 10)
            for piecenum in orderpcs:
                pieces[ordernewpcs[piecenum]] = newpcs[piecenum]
                removepiecefromscreen(arr, 200*(ordernewpcs[piecenum]//2), 150*(ordernewpcs[piecenum]%2)+200, 200,150,(255,255,255))
                placedpieces.append(ordernewpcs[piecenum])
                itemsinlevel.append(ordernewpcs[piecenum])
            transformgrid(solution, ordernewpcs)
            copygrids(grid, solution)
            putgridonscreen(arr, grid, colors, 4, 325, 500, 50, 50, (255,255,255))
            cv2.putText(arr, 'Time:',(10,700),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,0),2)
            cv2.putText(arr, 'Record:',(10,550),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,0),2)
            cv2.putText(arr, f'{records[button]:.2f}',(50,625),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,200),2)
            level[0] = button
            level[1] = t.time()
    cv2.imshow(name,arr)
    
def endlevel(arr, level):
    level[0] = -1
    level[1] = 0
    arr[500:800,0:325] = (255,255,255)
    
def clear(arr, pieces, grid, colors, selected, placedpieces, itemsinlevel):
    length = len(placedpieces)
    for _ in range(length):
        placedpieces.pop()
    length = len(itemsinlevel)
    for _ in range(length):
        itemsinlevel.pop()
    selected[0] = -1
    cleargrid(grid)
    putpiecesonscreen(arr, pieces, colors, (35,35), 4, (0,0,0))
    putgridonscreen(arr, grid, colors, 4, 325, 500, 50, 50, (255,255,255))    

def solve(arr, grid, pieces, placedpieces):
    usedpieces = list(set([num for row in grid for num in row]))
    try:
        usedpieces.remove(0)
    except:
        return
    datausedpieces = generatedatausedpieces(grid, usedpieces)
    usedpieces = [num - 10 for num in usedpieces]
    newboard = twodimentional.board()
    solution = twodimentional.preamble(newboard,pieces,usedpieces,datausedpieces, offset=10)
    for i,piece in enumerate(usedpieces):
        if piece not in placedpieces:
            placedpieces.append(piece)
            removepiecefromscreen(arr, 200*(piece//2), 150*(piece%2)+200, 200,150,(255,255,255))
    if len(placedpieces) < 12:
        cv2.putText(arr, 'No solutions from this position',(920,750),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,200),2)
        selected[1] = 1
    copygrids(grid, solution)
    
def copygrids(grid, solution):            
    for i in range(5):
        for j in range(11):
            grid[i][j] = solution[i][j]
 
def transformgrid(grid, order):
    for i,row in enumerate(grid):
        for j, el in enumerate(row):
            if el != 0:
                grid[i][j] = order[el-10] + 10       
    
def generatedatausedpieces(grid, usedpieces):
    datausedpieces = []
    for usedpiece in usedpieces:
        found = False
        for i in range(11):
            if found:
                break
            for j in range(5):
                if grid[j][i] == usedpiece:
                    found = True
                    datausedpieces.append([i,j,0])
                    break
    return datausedpieces

def cleargrid(grid):
    ii = len(grid)
    jj = len(grid[0])
    for i in range(ii):
        for j in range(jj):
            grid[i][j] = 0

            
def removefrommatrix(grid, item):
    for i,row in enumerate(grid):
        for j,el in enumerate(row):
            if el == item:
                grid[i][j] = 0
            
def addmatrices(grid, test, num):
    for i,row in enumerate(grid):
        for j,el in enumerate(row):
            grid[i][j] = el + test[i][j]*(10+num)

def rotate(selected, pieces):
    oldpiece = pieces[selected[0]]
    newpiece = twodimentional.rotate(oldpiece, 1)
    pieces[selected[0]] = newpiece
    removepiecefromscreen(arr, 200*(selected[0]//2), 150*(selected[0]%2)+200, 200,150,(255,255,255))
    putpieceonscreen(arr, pieces[selected[0]],200*(selected[0]//2)+5, 150*(selected[0]%2)+205, 35,35, 4,(0,0,150), colors[selected[0]])
    cv2.imshow(name, arr)
    
def flip(selected, pieces):
    oldpiece = pieces[selected[0]]
    newpiece = twodimentional.flip(oldpiece)
    pieces[selected[0]] = newpiece
    removepiecefromscreen(arr, 200*(selected[0]//2), 150*(selected[0]%2)+200, 200,150,(255,255,255))
    putpieceonscreen(arr, pieces[selected[0]],200*(selected[0]//2)+5, 150*(selected[0]%2)+205, 35,35, 4,(0,0,150), colors[selected[0]])
    cv2.imshow(name, arr)
        
def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        update(x,y,selected, pieces, grid)
    elif event == cv2.EVENT_MOUSEWHEEL:
        if selected[0] != -1:
            rotate(selected, pieces)
    elif event == cv2.EVENT_RBUTTONDOWN:
        if selected[0] != -1:
            flip(selected, pieces)
            

def creategrid(arr, startingpoint, sizecell, widthborder, gridcolor):
    starty, startx = startingpoint
    sizey, sizex = sizecell
    xlength = 11*sizex
    ylength = 5*sizey
    for i in range(6):
        yval = starty + i*sizey
        for j in range(xlength+widthborder):
            for k in range(widthborder):
                arr[yval+k][startx+j] = gridcolor
    for j in range(12):
        xval = startx + j*sizex
        for i in range(ylength):
            for k in range(widthborder):
                arr[starty + i][xval + k] = gridcolor

def putblockonscreen(arr,x,y,widthborder,bordercolor,sizex,sizey,color):
    arr[y:y+sizey,x:x+sizex] = bordercolor
    arr[y+widthborder//2:y+sizey-widthborder//2,x+widthborder//2:x+sizex-widthborder//2] = color
    
def putgridonscreen(arr, grid, colors, widthborder, startx, starty, sizex, sizey, backgroundcolor):
    h = widthborder//2
    for i, row in enumerate(grid):
        for j, el in enumerate(row):
            if el == 0:
                arr[starty+i*sizey+h:starty+(i+1)*sizey,startx+j*sizex+h:startx+(j+1)*sizex] = backgroundcolor
            else:
                arr[starty+i*sizey+h:starty+(i+1)*sizey,startx+j*sizex+h:startx+(j+1)*sizex] = colors[el-10]
    
def removepiecefromscreen(arr,startx, starty, sizex, sizey, backgroundcolor):
    arr[starty:starty+sizey,startx:startx+sizex] = backgroundcolor

def putpiecesonscreen(arr, pieces, colors, sizecell, widthborder, bordercolor):
    ystep = 150
    xstep = 200
    sizey, sizex = sizecell
    for i in range(6):
        for j in range(2):
            piece = pieces[i*2+j]
            color = colors[i*2+j]
            startx, starty = i * xstep + 5, j * ystep + 205
            putpieceonscreen(arr, piece, startx, starty, sizex, sizey, widthborder, bordercolor, color)
            
def putpieceonscreen(arr, piece, startx, starty, sizex, sizey, widthborder, bordercolor, color):    
    for k,row in enumerate(piece):
        for l,el in enumerate(row):
            if el:
                putblockonscreen(arr,startx+l*sizey,starty+k*sizex,widthborder,bordercolor,sizex,sizey,color)
       
def loadbesttimes():
    data = []
    with open('files/records.py','r') as file:
        for record in file.readlines():
            data.append(float(record[:-1]))
    return data
        
def writebesttimes(records):
    with open('files/records.py','w') as file:
        file.writelines([str(record)+'\n' for record in records])
                    
if __name__ == '__main__': 
    records = loadbesttimes()
    level = [-1,0]
    itemsinlevel = []
    name = 'IQgame'
    grid = twodimentional.board()
    pieces = list(twodimentional.getpieces())
    colors = twodimentional.colors()
    colors = tuple((color[2], color[1], color[0]) for color in colors)
    arr = np.zeros((800,1200,3),dtype=np.uint8)
    arr -= 1
    placedpieces = []
    cv2.imshow(name,arr)
    creategrid(arr, (500,325), (50,50), 3, (0,0,0))
    putpiecesonscreen(arr, pieces, colors, (35,35), 4, (0,0,0))
    
    arr[650:710,940:1120] = (0,0,0)
    arr[653:707,943:1117] = (100,255,100)
    cv2.putText(arr, 'Solve',(950,700),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,0),2)
    
    arr[550:610,940:1120] = (0,0,0)
    arr[553:607,943:1117] = (100,100,255)
    cv2.putText(arr, 'Reset',(942,600),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,0),2)
    
    cv2.putText(arr, 'The iQgame',(200,100),cv2.FONT_HERSHEY_SIMPLEX,4,(0,0,0),2)
    arr[110:112,70:1130] = (0,0,0)
    
    buttoncolors = [(102,255,102),(0,200,255),(0,0,255),(204,0,0),(153,0,153)]
    buttonnames = ['Starter','Junior','Expert','Master','Wizard']
    for i,(buttoncolor, buttonname) in enumerate(zip(buttoncolors, buttonnames)):
        arr[140:190,200*i+115:200*(i+1)-30+115] = (0,0,0)
        arr[142:188,200*i+2+115:200*(i+1)-32+115] = buttoncolor
        cv2.putText(arr, buttonname,(200*i+5+115,180),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,0),2)        
    
    cv2.imshow(name,arr)
    selected = [-1,0]
    cv2.setMouseCallback(name, click_event)
    cv2.waitKey(0)