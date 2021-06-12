import cv2
import numpy as np
from rubik_solver import utils
from RubicCube import Game

class Scanner():
    def __init__(self):
        super().__init__()
        self.condition = False
        self.state = {
            'up'   :['white','white','white','white','white','white','white','white','white',],
            'left' :['white','white','white','white','white','white','white','white','white',],
            'front':['white','white','white','white','white','white','white','white','white',],
            'right':['white','white','white','white','white','white','white','white','white',],
            'back' :['white','white','white','white','white','white','white','white','white',],
            'down' :['white','white','white','white','white','white','white','white','white',],
            }
        self.sign_conv = {
                    'green'  : 'g',
                    'white'  : 'w',
                    'blue'   : 'b',
                    'red'    : 'r',
                    'orange' : 'o',
                    'yellow' : 'y'
                }
        self.color = {
                'red'    : (0,0,255),
                'orange' : (0,165,255),
                'blue'   : (255,0,0),
                'green'  : (0,255,0),
                'white'  : (255,255,255),
                'yellow' : (0,255,255)
                }
        self.stickers = {
                'main': [
                    [200, 120], [300, 120], [400, 120],
                    [200, 220], [300, 220], [400, 220],
                    [200, 320], [300, 320], [400, 320]
                ],
                'current': [
                    [20, 20], [54, 20], [88, 20],
                    [20, 54], [54, 54], [88, 54],
                    [20, 88], [54, 88], [88, 88]
                ],
                'preview': [
                    [20, 130], [54, 130], [88, 130],
                    [20, 164], [54, 164], [88, 164],
                    [20, 198], [54, 198], [88, 198]
                ],
                'left': [
                    [50, 280], [94, 280], [138, 280],
                    [50, 324], [94, 324], [138, 324],
                    [50, 368], [94, 368], [138, 368]
                ],
                'front': [
                    [188, 280], [232, 280], [276, 280],
                    [188, 324], [232, 324], [276, 324],
                    [188, 368], [232, 368], [276, 368]
                ],
                'right': [
                    [326, 280], [370, 280], [414, 280],
                    [326, 324], [370, 324], [414, 324],
                    [326, 368], [370, 368], [414, 368]
                ],
                'up': [
                    [188, 128], [232, 128], [276, 128],
                    [188, 172], [232, 172], [276, 172],
                    [188, 216], [232, 216], [276, 216]
                ],
                'down': [
                    [188, 434], [232, 434], [276, 434],
                    [188, 478], [232, 478], [276, 478],
                    [188, 522], [232, 522], [276, 522]
                ], 
                'back': [
                    [464, 280], [508, 280], [552, 280],
                    [464, 324], [508, 324], [552, 324],
                    [464, 368], [508, 368], [552, 368]
                ],
                }
        self.textPoints =  {
                    'up'   :[['U',242, 202], ['Y',(0,0,0), 263, 208]],
                    'left' :[['L',104,354],  ['B',(255,0,0), 122, 360]],
                    'front':[['F',242, 354], ['R',(0,0,255), 260, 360]],
                    'right':[['R',380, 354], ['G',(0,225,0), 398, 360]],
                    'back' :[['B',518, 354], ['O',(0,165,255), 536, 360]],
                    'down' :[['D',242, 508], ['W',(0,0,0), 260, 514]],
                }
        self.color_detect3 = {
            'white' : [[],[],[]],
            'red' : [[],[],[]],
            'blue' : [[],[],[]],
            'green' : [[],[],[]],
            'yellow' : [[],[],[]],
            'orange' : [[],[],[]]}
        self.check_state = []
        self.font = cv2.FONT_HERSHEY_SIMPLEX  
        self.loop()

    def color_detect(self, h, s, v):
        # print(h,'\t', s,'\t', v)
        if s > 100 and h > 95 and h < 105:
            return 'blue'
        elif h < 80 and h > 60:
            return 'green'
        elif h <= 50 and h >= 20:
            return 'yellow'
        elif h <= 19 and h >= 5:
            return 'orange'
        elif h <= 4 or h >= 175:
            return 'red'
        elif s > 60:
            return 'white'
        return 'white'

    def draw_stickers(self, frame, stickers, name):
            for x,y in self.stickers[name]:
                cv2.rectangle(frame, (x,y), (x+30, y+30), (255,255,255), 2)

    def draw_preview_stickers(self, frame, stickers):
            self.stick = ['front','back','left','right','up','down']
            for name in self.stick:
                for x,y in self.stickers[name]:
                    cv2.rectangle(frame, (x,y), (x+40, y+40), (255,255,255), 2)

    def texton_preview_stickers(self, frame, stickers):
            self.stick=['front','back','left','right','up','down']
            for name in self.stick:
                for x,y in self.stickers[name]:
                    sym, x1, y1 = self.textPoints[name][0][0], self.textPoints[name][0][1], self.textPoints[name][0][2]
                    cv2.putText(self.preview, sym, (x1,y1), self.font,1,(0, 0, 0), 1, cv2.LINE_AA)  
                    sym, col, x1, y1 = self.textPoints[name][1][0], self.textPoints[name][1][1], self.textPoints[name][1][2], self.textPoints[name][1][3]             
                    cv2.putText(self.preview, sym, (x1,y1), self.font,0.5,col, 1, cv2.LINE_AA)  

    def fill_stickers(self, frame, stickers, sides):    
        for side,colors in sides.items():
            num = 0
            for x,y in self.stickers[side]:
                cv2.rectangle(frame,(x,y),(x+40,y+40), self.color[colors[num]],-1)
                num += 1  
    
    def loop(self):
        self.preview = np.zeros((700,800,3), np.uint8)

        self.cap = cv2.VideoCapture(1)
        # cv2.namedWindow('frame')
        cv2.imshow('frame', self.cap.read()[1])
        cv2.moveWindow('frame', 300, 200)
        cv2.imshow('preview', self.preview)
        cv2.moveWindow('preview', 810, 100)
    
        while True:
            self.hsv=[]
            self.current_state=[]
            self.ret, self.img = self.cap.read()
            # self.img = cv2.flip(self.img,1)
            self.frame = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
            self.mask = np.zeros(self.frame.shape, dtype = np.uint8)   

            self.draw_stickers(self.img, self.stickers, 'main')
            self.draw_stickers(self.img, self.stickers, 'current')
            self.draw_preview_stickers(self.preview, self.stickers)
            self.fill_stickers(self.preview, self.stickers, self.state)
            self.texton_preview_stickers(self.preview, self.stickers)

            for i in range(9):
                self.hsv.append(self.frame[self.stickers['main'][i][1]+10][self.stickers['main'][i][0]+10])
            
            a = 0
            for x,y in self.stickers['current']:
                self.color_name = self.color_detect(self.hsv[a][0], self.hsv[a][1], self.hsv[a][2])
                cv2.rectangle(self.img,(x,y),(x+30,y+30), self.color[self.color_name],-1)
                a += 1
                self.current_state.append(self.color_name)
            
            k = cv2.waitKey(5) & 0xFF
            if k == ord('q'):
                break      
            elif k == ord('u'):
                self.check_state.append('u')
                self.state['up'] = self.current_state
            elif k == ord('r'):
                self.check_state.append('r')
                self.state['right'] = self.current_state
            elif k == ord('l'):
                self.check_state.append('l')
                self.state['left'] = self.current_state
            elif k == ord('d'):
                self.check_state.append('d')
                self.state['down'] = self.current_state       
            elif k == ord('f'):
                self.check_state.append('f')
                self.state['front'] = self.current_state       
            elif k == ord('b'):
                self.check_state.append('b')
                self.state['back'] = self.current_state
            elif k == ord('c'):
                if len(set(self.check_state)) == 6: # <-- make this equals to
                    try:
                        self.cube_color = ''
                        for i in self.state:
                            for j in self.state[i]:
                                self.cube_color += self.sign_conv[j]
                        self.condition = True
                        # print(self.cube_color)
                        # self.cube_color = 'byobybbrororbbobrgyyywrowrygwgggobggwgwyoyrgorbowwwwry' # <-- comment this
                        self.solution_k = utils.solve(self.cube_color, 'Kociemba')
                        self.solution = [ str(x) for x in self.solution_k]
                        break
                    except:
                        print("Faces are not scanned properly")
                else:
                    print("All sides not scanned")
            cv2.imshow('preview', self.preview)
            cv2.imshow('frame', self.img[0:500,0:500])

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    
    s = Scanner()
    
    if s.condition:
        # Rubik 3D starts here
        game = Game(solution1 = s.solution)
        def update():
            game.update()
        game.run()