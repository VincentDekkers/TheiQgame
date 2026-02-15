import cv2
import numpy as np
import files.twodimentional as twodimentional
import time as t
import struct
import threading
import socket
import copy
from tkinter import simpledialog

class TheiQgame:
    def __init__(self, port=62743):
        self.host = simpledialog.askstring(title="IP", prompt="IP:")
        self.port = port

        self.kill = False

        self.socket = None
        self.justresetlevel = False
        self.mode = 0 
        self.records = self.loadbesttimes()
        self.level = [-1,0]
        self.itemsinlevel = []
        self.name = 'IQgame'
        self.grid = twodimentional.getboard()
        self.pieces = list(twodimentional.getpieces())
        self.colors = twodimentional.colors()
        self.colors = tuple((color[2], color[1], color[0]) for color in self.colors)
        self.arr = np.zeros((800,1200,3),dtype=np.uint8)
        self.arr -= 1
        self.placedpieces = []
        self.selected = [-1,0]
        self.prevselected = None
        self.levelgrid = [[0 for _ in range(11)] for _ in range(5)]
        self.player = None
        
        self.clicking = False
        self.prevmousepos = None
        self.dragging = False
        self.firstdrag = True
        self.piecelayer = None
        self.position = None
        self.printpiece = False

    
    def update(self, x,y,selected, pieces, grid):
        if selected[1]:
            selected[1] = 0
            self.arr[732:759,908:1180] = (255,255,255)
        if self.player:
            cv2.putText(self.arr, f'Player {self.player}',(950,100),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,255),2)
        if (200 < y < 500):
            newselected = 2*(x // 200) + (y-200) // 150
            if newselected not in self.placedpieces:
                self.removepiecefromscreen(self.arr, 200*(x//200), 150*((y-200)//150)+200, 200, 150, (255,255,255))
                if newselected == selected[0]:
                    self.prevselected = self.selected[0]
                    origin = ((x//200)*200+5,((y-200)//150)*150+205,)
                    self.position = (int((50/35)*origin[0]-(15/35)*x),int((50/35)*origin[1]-(15/35)*y),)
                    self.putpieceonscreen(self.arr, pieces[newselected],200*(x//200)+5, 150*((y-200)//150)+205, 35,35, 4,(0,0,0), self.colors[newselected])
                    selected[0] = -1
                    self.updatepiecelayer()
                    self.position = None
                elif selected[0] == -1:
                    self.putpieceonscreen(self.arr, pieces[newselected],200*(x//200)+5, 150*((y-200)//150)+205, 35,35, 4,(0,0,150),self.colors[newselected])
                    selected[0] = newselected
                    self.updatepiecelayer()
                    origin = ((x//200)*200+5,((y-200)//150)*150+205,)
                    self.position = (int((50/35)*origin[0]-(15/35)*x),int((50/35)*origin[1]-(15/35)*y),)
                else:
                    self.removepiecefromscreen(self.arr, 200*(selected[0]//2), 150*(selected[0]%2)+200, 200,150,(255,255,255))
                    self.putpieceonscreen(self.arr, pieces[newselected],200*(x//200)+5, 150*((y-200)//150)+205, 35,35, 4,(0,0,150),self.colors[newselected])
                    self.putpieceonscreen(self.arr, pieces[selected[0]],200*(selected[0]//2)+5, 150*(selected[0]%2)+205, 35,35, 4,(0,0,0), self.colors[selected[0]])
                    selected[0] = newselected
                    self.updatepiecelayer()
                    origin = ((x//200)*200+5,((y-200)//150)*150+205,)
                    self.position = (int((50/35)*origin[0]-(15/35)*x),int((50/35)*origin[1]-(15/35)*y),)
        elif (325<x<924) and (501<y<749):
            if x > 874 and not self.mode:
                return
            xlocation = (x-325)//50
            ylocation = (y-500)//50
            if selected[0] != -1:
                test = twodimentional.putpieceonboard(grid, pieces[selected[0]],xlocation,ylocation)
                if type(test) == list:
                    self.placedpieces.append(selected[0])
                    if len(self.placedpieces) == 12 and self.level[0] != -1:
                        stop = t.time()
                        time = stop - self.level[1]
                        if time < self.records[self.level[0]]:
                            self.records[self.level[0]] = time
                            printcolor = (0,200,0)
                            self.writebesttimes(self.records)
                        else:
                            printcolor = (0,0,200)
                        self.send(time)
                        cv2.putText(self.arr, f'{time:.2f}',(50,775),cv2.FONT_HERSHEY_SIMPLEX,2,printcolor,2)
                        for item in self.placedpieces:
                            if item not in self.itemsinlevel:
                                self.itemsinlevel.append(item)
                    if not self.mode:
                        test = twodimentional.putpieceonboard(twodimentional.getboard(), pieces[selected[0]],xlocation,ylocation)
                    else:
                        test = twodimentional.putpieceonboard(twodimentional.omasboard(), pieces[selected[0]],xlocation,ylocation)
                    self.addmatrices(grid, test, selected[0])
                    self.putgridonscreen(self.arr, grid, self.colors, 4, 325, 500, 50, 50, (255,255,255))
                    self.removepiecefromscreen(self.arr, 200*(selected[0]//2), 150*(selected[0]%2)+200, 200,150,(255,255,255))
                    selected[0] = -1 
                    self.updatepiecelayer()
                    self.position = None
                else:
                    removeditem = grid[ylocation][xlocation]
                    if removeditem != 0 and not self.dragging:
                        removedindex = removeditem - 10
                        removedlocation = self.removefrommatrix(grid, removeditem)
                        self.placedpieces.remove(removedindex)
                        self.putgridonscreen(self.arr, grid, self.colors, 4, 325, 500, 50, 50, (255,255,255))
                        self.putpieceonscreen(self.arr, pieces[removedindex],200*(removedindex//2)+5, 150*(removedindex%2)+205, 35,35, 4,(0,0,150), self.colors[removedindex])
                        self.removepiecefromscreen(self.arr, 200*(selected[0]//2), 150*(selected[0]%2)+200, 200,150,(255,255,255))
                        self.putpieceonscreen(self.arr, pieces[selected[0]],200*(selected[0]//2)+5, 150*(selected[0]%2)+205, 35,35, 4,(0,0,0), self.colors[selected[0]])
                        selected[0] = removedindex
                        self.updatepiecelayer()
                        self.position = (325+50*removedlocation[1],500+50*removedlocation[0],)
                        if removedindex in self.itemsinlevel:
                            self.endlevel(self.arr, self.level)
            else:
                removeditem = grid[ylocation][xlocation]
                if removeditem != 0 and not self.dragging:
                    removedindex = removeditem - 10
                    removedlocation = self.removefrommatrix(grid, removeditem)
                    self.placedpieces.remove(removedindex)
                    self.putgridonscreen(self.arr, grid, self.colors, 4, 325, 500, 50, 50, (255,255,255))
                    self.putpieceonscreen(self.arr, pieces[removedindex],200*(removedindex//2)+5, 150*(removedindex%2)+205, 35,35, 4,(0,0,150), self.colors[removedindex])
                    selected[0] = removedindex
                    self.updatepiecelayer()
                    self.position = (325+50*removedlocation[1],500+50*removedlocation[0],)
                    if removedindex in self.itemsinlevel:
                        self.endlevel(self.arr, self.level)
        elif (940<x<1120) and (650<y<710):
            self.solve(self.arr, grid, pieces, self.placedpieces)
            self.putgridonscreen(self.arr, grid, self.colors, 4, 325, 500, 50, 50, (255,255,255))
            self.endlevel(self.arr, self.level)
        elif (940<x<1120) and (550<y<610):
            self.justresetlevel = True
            self.newlevel()
            
    def updatepiecelayer(self):
        if self.selected[0] == -1:
            self.piecelayer = None
            self.position = None
        else:
            piece = self.pieces[self.selected[0]]
            color = self.colors[self.selected[0]]
            self.piecelayer = np.zeros((len(piece)*50, len(piece[0])*50,3),dtype=np.uint8) - 1
            for i, row in enumerate(piece):
                for j,el in enumerate(row):
                    if el == 1:
                        self.piecelayer[50*i:50*(i+1),50*j:50*(j+1)] = (0,0,0)
                        self.piecelayer[50*i+2:50*(i+1)-2,50*j+2:50*(j+1)-2] = color
        
    def dragpiece(self,x,y):
        if self.selected[0] == -1 and self.prevselected != None:
            self.update(x,y,self.selected, self.pieces, self.grid)
        if self.firstdrag:
            self.firstdrag = False
            self.printpiece = True
            if self.selected[0] != -1:
                self.removepiecefromscreen(self.arr, 200*(self.selected[0]//2), 150*(self.selected[0]%2)+200, 200,150,(255,255,255))
        if self.position != None:
            self.position = (self.position[0]+x-self.prevmousepos[0],self.position[1]+y-self.prevmousepos[1],)
            self.prevmousepos = (x,y,)
            
    def release(self,x,y):
        self.clicking = False
        self.printpiece = False
        self.prevmousepos = None
        self.prevselected = None
        if self.dragging and self.selected[0] != -1 and (300<self.position[0]<899) and (476<self.position[1]<724):
            self.update(self.position[0]+25,self.position[1]+25,self.selected,self.pieces,self.grid)
        if self.selected[0] != -1:
            self.putpieceonscreen(self.arr, self.pieces[self.selected[0]],200*(self.selected[0]//2)+5, 150*(self.selected[0]%2)+205, 35,35, 4,(0,0,150), self.colors[self.selected[0]])
        self.dragging = False
        self.firstdrag = True
        
    def newlevel(self):
        self.clear(self.arr, self.pieces, self.grid, self.colors, self.selected, self.placedpieces, self.itemsinlevel)
        self.endlevel(self.arr,self.level)
        self.copygrids(self.grid, self.levelgrid)
        self.putgridonscreen(self.arr, self.grid, self.colors, 4, 325, 500, 50, 50, (255,255,255))
        if self.host:
            cv2.putText(self.arr, 'Time:',(10,700),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,0),2)
            cv2.putText(self.arr, 'Record:',(10,550),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,0),2)
            listofelements = [el for row in self.levelgrid for el in row]
            for i in range(10,22):
                if i in listofelements:
                    self.placedpieces.append(i-10)
                    self.itemsinlevel.append(i-10)
                    self.removepiecefromscreen(self.arr, 200*((i-10)//2), 150*((i-10)%2)+200, 200,150,(255,255,255))
            cv2.putText(self.arr, f'{self.records[(10-len(self.itemsinlevel))//2]:.2f}',(50,625),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,200),2)
            self.rotatepieces()
            self.level[0] = (10-len(self.itemsinlevel))//2
            if not self.justresetlevel:
                self.level[1] = t.time()
            else:
                self.justresetlevel = False
        
    def rotatepieces(self):
        usedpieces = list(set([num for row in self.grid for num in row]))
        try:
            usedpieces.remove(0)
        except:
            pass
        data = self.generatedatausedpieces(self.levelgrid, usedpieces)
        for pieceindex, (offsetx, offsety, _) in zip(self.itemsinlevel,data):
            possibilities = twodimentional.possibilitiesperpiece(self.pieces[pieceindex])
            for possibility in possibilities:
                if self.checkpossibility(offsetx, offsety, possibility, pieceindex):
                    self.pieces[pieceindex] = possibility
                    break
        
    def checkpossibility(self, offsetx, offsety, possibility, pieceindex):
        offset = twodimentional.calculateoffset(possibility)
        try:
            for i,row in enumerate(possibility):
                for j, el in enumerate(row):
                    if el == 1:
                        if self.grid[offsety + i - offset][offsetx + j] != pieceindex + 10:
                            return False
            else:
                return True
        except:
            return False
        
    def endlevel(self, arr, level):
        level[0] = -1
        arr[500:800,0:325] = (255,255,255)
        
    def clear(self, arr, pieces, grid, colors, selected, placedpieces, itemsinlevel):
        length = len(placedpieces)
        for _ in range(length):
            placedpieces.pop()
        length = len(itemsinlevel)
        for _ in range(length):
            itemsinlevel.pop()
        selected[0] = -1
        self.updatepiecelayer()
        self.position = None
        self.cleargrid(grid)
        self.putpiecesonscreen(arr, pieces, colors, (35,35), 4, (0,0,0))
        self.putgridonscreen(arr, grid, colors, 4, 325, 500, 50, 50, (255,255,255))    

    def solve(self, arr, grid, pieces, placedpieces):
        self.selected[0] = -1
        self.updatepiecelayer()
        self.position = None
        self.level[1] = 0
        usedpieces = list(set([num for row in grid for num in row]))
        try:
            usedpieces.remove(0)
        except:
            return
        datausedpieces = self.generatedatausedpieces(grid, usedpieces)
        usedpieces = [num - 10 for num in usedpieces]
        if not self.mode:
            newboard = twodimentional.getboard()
        else:
            newboard = twodimentional.omasboard()
        solution = twodimentional.preamble(newboard,pieces,usedpieces,datausedpieces, offset=10, mode=self.mode)
        for i,piece in enumerate(usedpieces):
            if piece not in placedpieces:
                placedpieces.append(piece)
                self.removepiecefromscreen(arr, 200*(piece//2), 150*(piece%2)+200, 200,150,(255,255,255))
        if len(placedpieces) < 12:
            cv2.putText(arr, 'No solutions from this position',(920,750),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,200),2)
            self.selected[1] = 1
        self.copygrids(grid, solution)
        
    def copygrids(self,grid, solution):            
        for i in range(5):
            for j in range(len(grid[0])):
                grid[i][j] = solution[i][j]
    
    def transformgrid(self,grid, order):
        for i,row in enumerate(grid):
            for j, el in enumerate(row):
                if el != 0:
                    grid[i][j] = order[el-10] + 10       
        
    def generatedatausedpieces(self,grid, usedpieces):
        datausedpieces = []
        for usedpiece in usedpieces:
            found = False
            for i in range(len(grid[0])):
                if found:
                    break
                for j in range(5):
                    if grid[j][i] == usedpiece:
                        found = True
                        datausedpieces.append([i,j,0])
                        break
        return datausedpieces

    def cleargrid(self,grid):
        ii = len(grid)
        jj = len(grid[0])
        for i in range(ii):
            for j in range(jj):
                grid[i][j] = 0

                
    def removefrommatrix(self,grid, item):
        mini = minj = 13
        for i,row in enumerate(grid):
            for j,el in enumerate(row):
                if el == item:
                    grid[i][j] = 0
                    if i < mini:
                        mini = i
                    if j < minj:
                        minj = j
        return (mini,minj,)
                
    def addmatrices(self,grid, test, num):
        for i,row in enumerate(grid):
            for j,el in enumerate(row):
                grid[i][j] = el + test[i][j]*(10+num)

    def rotate(self,selected, pieces):
        oldpiece = pieces[selected[0]]
        newpiece = twodimentional.rotate(oldpiece, 1)
        pieces[selected[0]] = newpiece
        if not self.dragging:
            self.removepiecefromscreen(self.arr, 200*(selected[0]//2), 150*(selected[0]%2)+200, 200,150,(255,255,255))
            self.putpieceonscreen(self.arr, pieces[selected[0]],200*(selected[0]//2)+5, 150*(selected[0]%2)+205, 35,35, 4,(0,0,150), self.colors[selected[0]])
        self.updatepiecelayer()
        if self.prevmousepos:
            self.position = (self.prevmousepos[0]+self.position[1]-self.prevmousepos[1], self.prevmousepos[1]-self.position[0]+self.prevmousepos[0]-len(self.piecelayer),)
        
        
    def flip(self,selected, pieces):
        oldpiece = pieces[selected[0]]
        newpiece = twodimentional.flip(oldpiece)
        pieces[selected[0]] = newpiece
        if not self.dragging:
            self.removepiecefromscreen(self.arr, 200*(selected[0]//2), 150*(selected[0]%2)+200, 200,150,(255,255,255))
            self.putpieceonscreen(self.arr, pieces[selected[0]],200*(selected[0]//2)+5, 150*(selected[0]%2)+205, 35,35, 4,(0,0,150), self.colors[selected[0]])
        self.updatepiecelayer()
        if self.prevmousepos:
            self.position = (self.prevmousepos[0] - len(self.piecelayer[0]) + (self.prevmousepos[0]-self.position[0]), self.position[1],)
    
            
    def click_event(self,event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.update(x,y,self.selected, self.pieces, self.grid)
            self.clicking = True
            self.prevmousepos = (x,y,)
        elif event == cv2.EVENT_MOUSEMOVE and self.clicking:
            self.dragging = True
            self.dragpiece(x,y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.release(x,y)
        elif event == cv2.EVENT_MOUSEWHEEL:
            if self.selected[0] != -1:
                self.rotate(self.selected, self.pieces)
        elif event == cv2.EVENT_RBUTTONDOWN:
            if self.selected[0] != -1:
                self.flip(self.selected, self.pieces)
                

    def creategrid(self,arr, startingpoint, sizecell, widthborder, gridcolor):
        starty, startx = startingpoint
        sizey, sizex = sizecell
        xlength = len(self.grid[0])*sizex
        ylength = 5*sizey
        for i in range(6):
            yval = starty + i*sizey
            for j in range(xlength+widthborder):
                for k in range(widthborder):
                    arr[yval+k][startx+j] = gridcolor
        for j in range(len(self.grid[0])+1):
            xval = startx + j*sizex
            for i in range(ylength):
                for k in range(widthborder):
                    arr[starty + i][xval + k] = gridcolor

    def putblockonscreen(self,arr,x,y,widthborder,bordercolor,sizex,sizey,color):
        arr[y:y+sizey,x:x+sizex] = bordercolor
        arr[y+widthborder//2:y+sizey-widthborder//2,x+widthborder//2:x+sizex-widthborder//2] = color
        
    def putgridonscreen(self,arr, grid, colors, widthborder, startx, starty, sizex, sizey, backgroundcolor):
        h = widthborder//2
        for i, row in enumerate(grid):
            for j, el in enumerate(row):
                if el == 0:
                    arr[starty+i*sizey+h:starty+(i+1)*sizey,startx+j*sizex+h:startx+(j+1)*sizex] = backgroundcolor
                else:
                    arr[starty+i*sizey+h:starty+(i+1)*sizey,startx+j*sizex+h:startx+(j+1)*sizex] = colors[el-10]
        
    def removepiecefromscreen(self,arr,startx, starty, sizex, sizey, backgroundcolor):
        arr[starty:starty+sizey,startx:startx+sizex] = backgroundcolor
        if starty == 350 and startx == 1000 and self.mode == 1:
            arr[490:540,995:1047] = backgroundcolor

    def putpiecesonscreen(self,arr, pieces, colors, sizecell, widthborder, bordercolor):
        ystep = 150
        xstep = 200
        sizey, sizex = sizecell
        for i in range(6):
            for j in range(2):
                piece = pieces[i*2+j]
                color = colors[i*2+j]
                startx, starty = i * xstep + 5, j * ystep + 205
                self.putpieceonscreen(arr, piece, startx, starty, sizex, sizey, widthborder, bordercolor, color)
                
    def putpieceonscreen(self,arr, piece, startx, starty, sizex, sizey, widthborder, bordercolor, color):    
        for k,row in enumerate(piece):
            for l,el in enumerate(row):
                if el:
                    self.putblockonscreen(arr,startx+l*sizey,starty+k*sizex,widthborder,bordercolor,sizex,sizey,color)
        
    def loadbesttimes(self,):
        try:
            data = []
            with open(f'files/{"omas" if self.mode else ""}records.py','r') as file:
                for record in file.readlines():
                    data.append(float(record[:-1]))
        except:
            data = [9999.99]*5
        return data
    
    def send(self, time):
        tosend = self.serialize(time)
        if self.socket:
            self.socket.sendall(tosend)    
            
    def serialize(self, time):
        return struct.pack('7s', f'{time:07.2f}'.encode())
            
    def writebesttimes(self,records):
        with open(f'files/{"omas" if self.mode else ""}records.py','w') as file:
            file.writelines([str(record)+'\n' for record in records])
            
    def changemode(self):
        self.arr[200:550,0:1200] = (255,255,255)
        self.arr[500:800,0:940] = (255,255,255)
        if self.mode == 1:
            self.grid = twodimentional.omasboard()
            self.pieces = list(twodimentional.getomaspieces())
        elif self.mode == 0:
            self.grid = twodimentional.getboard()
            self.pieces = list(twodimentional.getpieces())
        self.records = self.loadbesttimes()
        self.creategrid(self.arr, (500,325), (50,50), 3, (0,0,0))
        self.putpiecesonscreen(self.arr, self.pieces, self.colors, (35,35), 4, (0,0,0))

    def deserialize(self, data):
        update_format = '123s'
        if len(data) >= struct.calcsize(update_format):
            message = struct.unpack_from(update_format, data, 0)[0]
            message = message.decode()
            self.levelgrid = [[int(message[2*((11 + int(message[-1]))*i+j):2*((11 + int(message[-1]))*i+j)+2]) for j in range(11 + int(message[-1]))] for i in range(5)]
            self.player = int(message[-3:-1])+1
            if self.mode != int(message[-1]):
                self.mode = int(message[-1])
                self.changemode()
            if int(message[0]) != 0:
                self.newlevel()

    def run_listener(self):
        if self.host:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
                s.connect((self.host, self.port))
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
                s.settimeout(1)
                print('connected', s)
                self.socket = s
                while not self.kill:
                    try:
                        data = self.socket.recv(4096)
                        if len(data):
                            self.deserialize(data)
                    except socket.timeout:
                        pass
                    t.sleep(0.001)
    
    def await_kill(self):
        self.kill = True

    def generateframe(self):
        if self.position != None and self.printpiece:
            tempframe = copy.deepcopy(self.arr)
            xstart, ystart = self.position
            lowy=lowx=highy=highx=False
            xstartpiece = ystartpiece = 0
            if ystart < 0:
                lowy=True
                ystartpiece = - ystart
            elif ystart+len(self.piecelayer) > 800:
                highy = True
            if xstart < 0:
                lowx = True
                xstartpiece = - xstart
            elif xstart+len(self.piecelayer[0]) > 1200:
                highx = True
            for i in range(ystart if not lowy else 0,ystart+len(self.piecelayer) if not highy else 800):
                for j in range(xstart if not lowx else 0,xstart+len(self.piecelayer[0]) if not highx else 1200):
                    if tuple(self.piecelayer[ystartpiece+i-ystart if not lowy else ystartpiece+i][xstartpiece+j-xstart if not lowx else xstartpiece + j]) != (255,255,255):
                        tempframe[i][j] = self.piecelayer[ystartpiece+i-ystart if not lowy else ystartpiece+i][xstartpiece+j-xstart if not lowx else xstartpiece + j]
            cv2.imshow(self.name, tempframe)
        else:
            cv2.imshow(self.name, self.arr)
            
    def run(self):
        threading.Thread(target=self.run_listener).start()
        self.creategrid(self.arr, (500,325), (50,50), 3, (0,0,0))
        self.putpiecesonscreen(self.arr, self.pieces, self.colors, (35,35), 4, (0,0,0))
        
        self.arr[650:710,940:1120] = (0,0,0)
        self.arr[653:707,943:1117] = (100,255,100)
        cv2.putText(self.arr, 'Solve',(950,700),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,0),2)
        
        self.arr[550:610,940:1120] = (0,0,0)
        self.arr[553:607,943:1117] = (100,100,255)
        cv2.putText(self.arr, 'Reset',(942,600),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,0),2)
        
        cv2.putText(self.arr, 'The iQgame',(200,100),cv2.FONT_HERSHEY_SIMPLEX,4,(0,0,0),2)
        self.arr[110:112,70:1130] = (0,0,0)

        cv2.imshow(self.name,self.arr)
        cv2.setMouseCallback(self.name, self.click_event)
        try:
            while cv2.getWindowProperty(self.name, 0) >= 0:
                self.generateframe()
                key = cv2.waitKey(1)
                if key == ord('r'):
                    if self.selected[0] != -1:
                        self.rotate(self.selected, self.pieces)
                elif key == ord('f'):
                    if self.selected[0] != -1:
                        self.flip(self.selected, self.pieces)
                t.sleep(0.02)
        except cv2.error:
            self.await_kill()
        
if __name__ == '__main__': 
    TheiQgame().run()