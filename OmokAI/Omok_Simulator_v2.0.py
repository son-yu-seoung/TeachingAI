import sys
import numpy as np
import cv2
import time
import os

# GUI 설정을 위해 PyQt5 라이브러리 이용
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class MyApp(QWidget):

    def __init__(self):
        super().__init__() # QWidget의 생성자 실행

        self.initUI() 

    def initUI(self): # 이미지들 불러오고, 저장 방법 등을 정의, 오목판을 배경으로 GUI 실행

        # 바둑판 크기
        board_size = 15
        self.game_end = 0 # ?
        self.board_size = board_size # 정의된 board_size를 사용하기 때문에 변수 수정이 용이해진다
        self.board = np.zeros([board_size,board_size]) # 오목을 하기위한 보드를 생성
        self.board_history = np.zeros([board_size,board_size]) # '''
        self.cnt = 1 # cnt를 1로 초기화 


        root_path = 'training_data' # 게임의 결과를 저장할 때의 폴더명 
        time_now = time.gmtime(time.time()) # 게임을 하고있는 년, 월, 일, 시간, 분, 초를 담고 있다.
        
        
        if time_now.tm_hour <= 12: # 오후 시간
            self.save_name = str(time_now.tm_year) + '_' + str(time_now.tm_mon) + '_' + str(time_now.tm_mday) + '_' + str(time_now.tm_hour + 9) + '_' + str(time_now.tm_min) + '_' + str(time_now.tm_sec) + '.txt'
            self.save_name_png = str(time_now.tm_year) + '_' + str(time_now.tm_mon) + '_' + str(time_now.tm_mday) + '_' + str(time_now.tm_hour + 9) + '_' + str(time_now.tm_min) + '_' + str(time_now.tm_sec) + '.png'
        else: # 오전 시간
            self.save_name = str(time_now.tm_year) + '_' + str(time_now.tm_mon) + '_' + str(time_now.tm_mday) + '_' + str( time_now.tm_hour + 9 - 24) + '_' + str(time_now.tm_min) + '_' + str(time_now.tm_sec) + '.txt'
            self.save_name_png = str(time_now.tm_year) + '_' + str(time_now.tm_mon) + '_' + str(time_now.tm_mday) + '_' + str( time_now.tm_hour + 9 - 24) + '_' + str(time_now.tm_min) + '_' + str(time_now.tm_sec) + '.png'

        self.save_name = os.path.join(root_path, 'txt', self.save_name) # 경로 합치기
        self.save_name_png = os.path.join(root_path, 'img', self.save_name_png) # 경로 합치기
        
        # read image in numpy array (using cv2)
        board_cv2 = cv2.imread('Image\\board_15x15.png') # (, , 3) 3채널을 가지고 있음
        # 색상 공간 변환(Covert Color)은 본래의 색상 공간에서 다른 색상 공간으로 변화할 때 사용
        # 색상 공간 변환 함수는 데이터 타입을 같게 유지하고 채널을 변환한다.
        # cv2.cvtColor(입력 이미지, 색상 변환 코드, 출력 채널)
        # 원본 이미지 생상 공간 2 결과 이미지 색상 공간 (원본 이미지 색상 공간은 원본 이미지와 일치해야함)
        self.board_cv2 = cv2.cvtColor(board_cv2, cv2.COLOR_BGR2RGB)
        # 이 코드에서 색상 공간 변환을 하는 이유는 무엇일까?
        #  !!색상 공간을 하지 않는 등의 test를 해서 알아보자!!
        black_ball = cv2.imread('Image\\black_15x15.png')
        self.black_ball = cv2.cvtColor(black_ball, cv2.COLOR_BGR2RGB)

        white_ball = cv2.imread('Image\\white_15x15.png')
        self.white_ball = cv2.cvtColor(white_ball, cv2.COLOR_BGR2RGB)

        # numpy to QImage
        height, width, channel = self.board_cv2.shape # (681, 681, 3)
        bytesPerLine = 3 * width  # 무슨 뜻?
        print(self.board_cv2)  # board_cv2는 그냥 numpy 배열
        print(self.board_cv2.data) # <memory at 0x0000~ACE50> 코드
        # QImage(cv2.data, 가로, 세로, ???, RGB888로 설정?) <<< 질문하기
        qImg_board = QImage(self.board_cv2.data, width, height, bytesPerLine, QImage.Format_RGB888)


        self.player = 1 # 1: 흑  / 2: 백
        x = 0
        y = 0

        # QLabel은 화면에서 한줄짜리 글자를 보여주고 싶을 때 사용하는 위젯, 버튼 같은 위젯과 달리 사용자와 상호작용 하지않음
        # 단순히 텍스트나 이미지를 보여주는 용도로 사용된다.
        self.lbl_img = QLabel() # 레이블 객체 생성
        self.lbl_img.setPixmap(QPixmap(qImg_board)) # 사진을 넣음

        self.vbox = QVBoxLayout() # QVBoxLayout 클래스는 위젯을 수직 방향으로 나열
        self.vbox.addWidget(self.lbl_img) # 배경 오목판 이미지를 위젯으로 설정
        self.setLayout(self.vbox)

        self.setWindowTitle('오목 시뮬레이션') # GUI 제목
        self.move(100, 100) # 내 모니터 위의 위치
        self.resize(500,500) # GUI 크기
        self.show() # 시작 


    def game_play(self, board_img, ball, pos_y, pos_x, turn):

        ball_size = ball.shape[0] # (74, 74, 3)
        step_size = 53 # 칸 당 간격 Image J로 측정 가능
        off_set = round(ball_size/2) # 해당 칸의 -off_set위치부터 돌을 그려야한다.
        center = 424 # board의 가운데 좌표 Image J로 측정 
        # step/2+off_set+1의 공식의 출력 값으로 뭐가 나오는지 수학적으로 이해할 수 있어야 함
        # round((pos_x - off_set)/step_size) 공식도 어떤 공식인지..
        # 같은 자리에 돌이 놓아지더라도 pos_x와 pos_y는 제 각각인데 어떻게 정규화?

        # 판의 마지막 모서리에는 돌을 두지 못하게 한다.
        print(step_size/2+off_set+1)
        if pos_y < step_size/2+20 or pos_x < step_size/2+20:
            print('그곳에는 둘 수 없습니다')
            print(11)

        elif pos_y > step_size*self.board_size + 25 or pos_x > step_size*self.board_size + 25 :
            print('그곳에는 둘 수 없습니다')

        else:
            # -8은 미세한 조정을 한 것이다.
            step_y = round((pos_y - 10) / step_size) # 해당 범위 내의 클릭시 배열 위치 1~9를 반환 
            step_x = round((pos_x - 10)/ step_size) # 해당 범위의 배열 위치를 반환하는 공식
            print(step_y)
            print(step_x)

            if self.board[step_y-1,step_x-1] != 0: # 이미 돌이 있을때
                print('그곳에는 둘 수 없습니다')

            else:
                self.board[step_y-1,step_x-1] = turn # 1~9이기 때문에 -1을 해주므로 배열에 정상적으로 저장
                self.board_history[step_y-1,step_x-1] = self.cnt # 흑은 홀수, 백은 짝수가 됌
                self.cnt = self.cnt + 1 # 왜 계속 1씩 늘릴까?
                
                # 오목판 위의 돌들의 간격의 오차를 최소화 하기 위한 방법 
                if step_x > 8 and step_y <= 8: # 1사분면
                    y_step = center - step_size*(8-step_y) - off_set
                    x_step = center + step_size*(step_x-8) - off_set
                    print("1사분면 :", x_step, y_step)
                elif step_x <= 8 and step_y <= 8: # 2사분면
                    y_step = center - step_size*(8-step_y) - off_set
                    x_step = center - step_size*(8-step_x) - off_set
                    print("2사분면 :", x_step, y_step)
                elif step_x <= 8 and step_y > 8: # 3사분면
                    y_step = center + step_size*(step_y-8) - off_set
                    x_step = center - step_size*(8-step_x) - off_set
                    print("3사분면 :", x_step, y_step)
                else: # 4사분면
                    y_step = center + step_size*(step_y-8) - off_set
                    x_step = center + step_size*(step_x-8) - off_set
                    print("4사분면 :", x_step, y_step)
                
                #y_step = step_size * step_y - off_set
                #x_step = step_size * step_x - off_set
                
                board_img[y_step:y_step+ball_size,x_step:x_step+ball_size] = ball

                # 게임 결과 확인
                if self.game_rule(self.board, turn):
                    self.game_end = 1

                    print('게임이 끝났습니다.')

                    board_img = cv2.cvtColor(board_img, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(self.save_name_png, board_img) # img 저장

                    if turn == 1: # 흑백 턴 교차
                        print('흑 승리')
                        self.save_history()

                    else:
                        print('백 승리')
                        self.save_history()

                else: # 게임이 끝나지 않았다면, 턴을 바꾸어 주고 계속 진행

                    if turn == 1: # 흑백 턴 교차
                        self.player = 2
                    else:
                        self.player = 1
                                  
        return board_img


    def mousePressEvent(self, e): # 마우스를 누르는 이벤트를 감지(클릭X 누르기)

        x = e.x() # 마우스가 눌린 x좌표
        y = e.y() # 마우스가 눌린 y좌표 
        if self.game_end == 0:
            if self.player == 1: # 흑돌 차례

                self.board_cv2 = self.game_play(self.board_cv2, self.black_ball, y, x, 1) # game_play메서드 호출
            else: # 백돌 차례
                self.board_cv2 = self.game_play(self.board_cv2, self.white_ball, y, x, 2) # board_img를 반환 받음
                
           
            height, width, channel = self.board_cv2.shape
            bytesPerLine = 3 * width
            qImg_board = QImage(self.board_cv2.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.lbl_img.setPixmap(QPixmap(qImg_board)) # 변화된 img 그리기



    def game_rule(self, board, player): # 추후 오목 국룰 (렌주룰) 도입 예정
        
        game_result = 0
        diag_line = np.zeros(5)
        
        # ●●●●● 가로 5줄 
        for i_idx in range(len(board)): # 15(0~14)
            for j_idx in range(len(board)-4): # 11(0~10)
                p1 = (board[i_idx,j_idx:j_idx+5] == player)
                
                if p1.sum() == 5:
                    #print('player ', player, ' win')
                    game_result = 1
                    return game_result
        
        # 세로 5줄 
        for i_idx in range(len(board)-4):
            for j_idx in range(len(board)):
                p1 = (board[i_idx:i_idx+5,j_idx] ==player)
                
                if p1.sum() == 5:
                    #print('player ', player, ' win')
                    game_result = 1
                    return game_result
        
        # 대각 5줄 - 1
        for i_idx in range(len(board)-4):
            for j_idx in range(len(board)-4):
                diag_line[0] = board[i_idx+0,j_idx+0]
                diag_line[1] = board[i_idx+1,j_idx+1]
                diag_line[2] = board[i_idx+2,j_idx+2]
                diag_line[3] = board[i_idx+3,j_idx+3]
                diag_line[4] = board[i_idx+4,j_idx+4]    
          
                p1 = (diag_line == player)
                
                if p1.sum() == 5:
                    #print('player ', player, ' win')
                    game_result = 1
                    return game_result

        # 대각 5줄 - 반대
        for i_idx in range(len(board)-4):
            for j_idx in range(len(board)-4):
                diag_line[0] = board[i_idx+4,j_idx+0]
                diag_line[1] = board[i_idx+3,j_idx+1]
                diag_line[2] = board[i_idx+2,j_idx+2]
                diag_line[3] = board[i_idx+1,j_idx+3]
                diag_line[4] = board[i_idx+0,j_idx+4]    
          
                p1 = (diag_line == player)
                
                if p1.sum() == 5:
                    
                    game_result = 1
                    return game_result
            
        return game_result

    def save_history(self): # 일단 여기서 오류 
        # ex) save_name = training_data\\txt\\2021_6_26_9_49_48.txt
        # ex) save_name_png = training_data\\img\\2021_6_26_9_49_48.png
        result=np.array(self.board_history).flatten() # 왜 flatten()? 공간정보가 사라질텐데,,
     
        f = open(self.save_name, 'w') 

        f.write(np.array2string(result)) # 배열을 str화 해서 저장 --> why?
        f.close()

   
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())