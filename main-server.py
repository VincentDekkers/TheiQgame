import cv2
import numpy as np
import files.twodimentional as twodimentional
import time as t
import struct
import socket
import threading

class TheiQgame:
    def __init__(self, port=62743):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = port

        self.kill = False
        self.thread_count = 0
        self.players = []
        self.itemsinlevel = []
        self.name = 'IQgame'
        self.grid = twodimentional.getboard()
        self.pieces = list(twodimentional.getpieces())
        self.arr = np.zeros((800,1200,3),dtype=np.uint8)
        self.arr -= 1
        self.ranking = []
        self.points = []
        self.placedpieces = []
        self.selected = [-1,0]
        self.finishedplayers = []
        self.mode = 0 # 0 for regular and 1 for omas
        self.buffer = []
        
    
    def update(self, x,y):
        if (140<y<190) and (115<x<1085):
            button = (x-115)//200 if (x-115)%200<170 else -1
            if button != -1:
                self.ranking = []
                self.finishedplayers = []
                self.clear()
                while len(self.buffer) == 0:
                    t.sleep(0.05)
                solution, newpcs, orderpcs, datanewpcs, ordernewpcs = self.buffer.pop()
                for _ in range(2*button+2):
                    datanewpcs.pop()
                    self.removefrommatrix(solution, orderpcs.pop() + 10)
                for piecenum in orderpcs:
                    self.pieces[ordernewpcs[piecenum]] = newpcs[piecenum]
                    self.placedpieces.append(ordernewpcs[piecenum])
                    self.itemsinlevel.append(ordernewpcs[piecenum])
                self.transformgrid(solution, ordernewpcs)
                self.copygrids(solution)
                self.send()
        elif (1020<x<1120) and (50<y<90):
            self.switchmode()
        
    def switchmode(self):
        if self.mode == 0:
            self.mode = 1
            self.arr[52:88,1022:1118] = (255,255,255)
            cv2.putText(self.arr, 'Hard', (1033,80),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)
            self.grid = twodimentional.omasboard()
            self.pieces = list(twodimentional.getomaspieces())
        elif self.mode == 1:
            self.mode = 0
            self.arr[52:88,1022:1118] = (255,255,255)
            cv2.putText(self.arr, 'Easy', (1033,80),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)
            self.grid = twodimentional.getboard()
            self.pieces = list(twodimentional.getpieces())
        self.buffer = []
        self.send()
        
    def writerecords(self):
        self.arr[260:700,0:1200] = (255,255,255)
        standings = [(points, player) for player, points in enumerate(self.points)]
        standings.sort(reverse=True)
        starty = 300
        for i,(points,player) in enumerate(standings):
            if starty+50*i < 750:
                cv2.putText(self.arr, f'Player {player + 1}: {points}', (50,starty+50*i),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,0),2)
        for i, (time, player) in enumerate(self.ranking):
            if starty+50*i < 750:
                cv2.putText(self.arr, f'Player {player + 1}: {float(time):7.2f}', (650,starty+50*i),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,0),2)

        
    def clear(self):
        length = len(self.placedpieces)
        for _ in range(length):
            self.placedpieces.pop()
        length = len(self.itemsinlevel)
        for _ in range(length):
            self.itemsinlevel.pop()
        self.cleargrid()  

        
    def copygrids(self, solution):            
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                self.grid[i][j] = solution[i][j]
    
    def transformgrid(self, grid, order):
        for i,row in enumerate(grid):
            for j, el in enumerate(row):
                if el != 0:
                    grid[i][j] = order[el-10] + 10       

    def cleargrid(self):
        ii = len(self.grid)
        jj = len(self.grid[0])
        for i in range(ii):
            for j in range(jj):
                self.grid[i][j] = 0
                
    def removefrommatrix(self,grid, item):
        for i,row in enumerate(grid):
            for j,el in enumerate(row):
                if el == item:
                    grid[i][j] = 0      
            
    def click_event(self,event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.update(x,y)
            
    def send(self):
        for id,player_conn in enumerate(self.players):
            try:
                tosend = self.serialize(id)
                player_conn.sendall(tosend)
            except OSError:
                pass        
            
    def serialize(self, id):
        return struct.pack('123s', (''.join([''.join([str(el) if el != 0 else '00' for el in row]) for row in self.grid])+f'{"0"*10 if not self.mode else ""}'+f'{id:2d}'+str(self.mode)).encode())
            
    def run_listener(self, conn):
        self.thread_count += 1
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        conn.settimeout(1)
        with conn:
            while not self.kill:
                try:
                    data = conn.recv(4096)
                    if len(data):
                        self.deserialize(data, conn)
                except socket.timeout:
                    pass
                except (ConnectionAbortedError, ConnectionResetError):
                    break
                t.sleep(0.001)
        self.thread_count -= 1
        
    def deserialize(self, data, conn):
        update_format = '7s'
        if len(data) >= struct.calcsize(update_format):
            message = struct.unpack_from(update_format, data, 0)[0]
            message = message.decode()
            if float(message) < 10000 and conn not in self.finishedplayers:
                self.finishedplayers.append(conn)
                self.ranking.append((message,self.players.index(conn)))
                if len(self.ranking) == 1:
                    self.points[self.players.index(conn)] += 1
            
    def connection_listen_loop(self):
        self.thread_count += 1
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            s.bind((self.host, self.port))

            while not self.kill:
                s.settimeout(1)
                s.listen()
                try:
                    conn, addr = s.accept()
                    print('new connection:', conn, addr)
                    self.players.append(conn)
                    self.points.append(0)
                    threading.Thread(target=self.run_listener, args=(conn,)).start()
                except socket.timeout:
                    continue
                t.sleep(0.01)
        self.thread_count -= 1

    def await_kill(self):
        self.kill = True
        while self.thread_count:
            t.sleep(0.01)
            
    def buffermaker(self):
        self.thread_count += 1
        while not self.kill:
            if len(self.buffer) < 3:
                if self.mode == 0:
                    self.buffer.append(twodimentional.generaterandomsolution(10))
                elif self.mode == 1:
                    self.buffer.append(twodimentional.generaterandomsolution(10,self.mode))
            t.sleep(0.1)
        self.thread_count -= 1
            
    def run(self):
        threading.Thread(target=self.connection_listen_loop).start()
        threading.Thread(target=self.buffermaker).start()
        cv2.putText(self.arr, self.host, (870,790), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 2)
        cv2.putText(self.arr, 'The iQgame',(200,100),cv2.FONT_HERSHEY_SIMPLEX,4,(0,0,0),2)
        self.arr[110:112,70:1130] = (0,0,0)
        
        buttoncolors = [(102,255,102),(0,200,255),(0,0,255),(204,0,0),(153,0,153)]
        buttonnames = ['Starter','Junior','Expert','Master','Wizard']
        for i,(buttoncolor, buttonname) in enumerate(zip(buttoncolors, buttonnames)):
            self.arr[140:190,200*i+115:200*(i+1)-30+115] = (0,0,0)
            self.arr[142:188,200*i+2+115:200*(i+1)-32+115] = buttoncolor
            cv2.putText(self.arr, buttonname,(200*i+5+115,180),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,0),2) 
        
        cv2.putText(self.arr, 'Mode:', (1000,40), cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),1)
        self.arr[50:90,1020:1120] = (0,0,0)
        self.arr[52:88,1022:1118] = (255,255,255)
        cv2.putText(self.arr, 'Easy', (1033,80),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)
               
        cv2.putText(self.arr, 'Points:', (50,250),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,0),2)
        cv2.putText(self.arr, 'This round:', (650,250),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,0),2)
        cv2.imshow(self.name,self.arr)
        cv2.setMouseCallback(self.name, self.click_event)
        try:
            while cv2.getWindowProperty(self.name, 0) >= 0:
                self.writerecords()
                cv2.imshow(self.name,self.arr)
                _ = cv2.waitKey(1)
                t.sleep(0.05)
        except cv2.error:
            self.await_kill()
                    
if __name__ == '__main__': 
    TheiQgame().run()