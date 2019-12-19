# ====================
# 사람과 AI의 대전
# ====================

# 패키지 임포트
from game import State
from pv_mcts import pv_mcts_action
from tensorflow.keras.models import load_model
from pathlib import Path
from threading import Thread
import tkinter as tk
from PIL import Image, ImageTk

# 베스트 플레이어 모델 로드
model = load_model('./model/best.h5')


# 게임 UI 정의
class GameUI(tk.Frame):
    # 초기화
    def __init__(self, master=None, model=None):
        tk.Frame.__init__(self, master)
        self.master.title('간이 장기')

        # 게임 상태 생성
        self.state = State()
        self.select = -1  # 선택(-1: 없음, 0~11: 매스, 12~14: 획득한 말)

        # 방향 정수
        self.dxy = ((0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1))

        # PV MCTS를 활용한 행동 선택을 수행하는 함수 생성
        self.next_action = pv_mcts_action(model, 0.0)

        # 이미지 준비
        self.images = [(None, None, None, None)]
        for i in range(1, 5):
            image = Image.open('piece{}.png'.format(i))
            self.images.append((
                ImageTk.PhotoImage(image),
                ImageTk.PhotoImage(image.rotate(180)),
                ImageTk.PhotoImage(image.resize((40, 40))),
                ImageTk.PhotoImage(image.resize((40, 40)).rotate(180))))

        # 캔버스 생성
        self.c = tk.Canvas(self, width=240, height=400, highlightthickness=0)
        self.c.bind('<Button-1>', self.turn_of_human)
        self.c.pack()

        # 화면 갱신
        self.on_draw()

    # 사람의 턴
    def turn_of_human(self, event):
        # 게임 종료 시
        if self.state.is_done():
            self.state = State()
            self.on_draw()
            return

        # 선 수가 아닌 경우
        if not self.state.is_first_player():
            return

        # 획득한 말의 종류 얻기
        captures = []
        for i in range(3):
            if self.state.pieces[12 + i] >= 2: captures.append(1 + i)
            if self.state.pieces[12 + i] >= 1: captures.append(1 + i)

        # 말 선택과 이동 위치 계산(0~11: 매스. 12~13: 획득한 말)
        p = int(event.x / 80) + int((event.y - 40) / 80) * 3
        if 40 <= event.y and event.y <= 360:
            select = p
        elif event.x < len(captures) * 40 and event.y > 360:
            select = 12 + int(event.x / 40)
        else:
            return

        # 말 선택
        if self.select < 0:
            self.select = select
            self.on_draw()
            return

        # 말 선택과 이동을 행동으로 변환
        action = -1
        if select < 12:
            # 말 이동 시
            if self.select < 12:
                action = self.state.position_to_action(p, self.position_to_direction(self.select, p))
            # 획득한 말 배치 시
            else:
                action = self.state.position_to_action(p, 8 - 1 + captures[self.select - 12])

        # 합법적인 수가 아닌 경우
        if not (action in self.state.legal_actions()):
            self.select = -1
            self.on_draw()
            return

        # 다음 상태 얻기
        self.state = self.state.next(action)
        self.select = -1
        self.on_draw()

        # AI의 턴
        self.master.after(1, self.turn_of_ai)

    # AI의 턴
    def turn_of_ai(self):
        # 게임 종료 시
        if self.state.is_done():
            return

        # 행동 얻기
        action = self.next_action(self.state)

        # 다음 상태 얻기
        self.state = self.state.next(action)
        self.on_draw()

    # 말의 이동 대상 위치를 말의 이동 방향으로 변환
    def position_to_direction(self, position_src, position_dst):
        dx = position_dst % 3 - position_src % 3
        dy = int(position_dst / 3) - int(position_src / 3)
        for i in range(8):
            if self.dxy[i][0] == dx and self.dxy[i][1] == dy: return i
        return 0

    # 말 그리기
    def draw_piece(self, index, first_player, piece_type):
        x = (index % 3) * 80
        y = int(index / 3) * 80 + 40
        index = 0 if first_player else 1
        self.c.create_image(x, y, image=self.images[piece_type][index], anchor=tk.NW)

    # 획득한 말 그리기
    def draw_capture(self, first_player, pieces):
        index, x, dx, y = (2, 0, 40, 360) if first_player else (3, 200, -40, 0)
        captures = []
        for i in range(3):
            if pieces[12 + i] >= 2: captures.append(1 + i)
            if pieces[12 + i] >= 1: captures.append(1 + i)
        for i in range(len(captures)):
            self.c.create_image(x + dx * i, y, image=self.images[captures[i]][index], anchor=tk.NW)

    # 커서 그리기
    def draw_cursor(self, x, y, size):
        self.c.create_line(x + 1, y + 1, x + size - 1, y + 1, width=4.0, fill='#FF0000')
        self.c.create_line(x + 1, y + size - 1, x + size - 1, y + size - 1, width=4.0, fill='#FF0000')
        self.c.create_line(x + 1, y + 1, x + 1, y + size - 1, width=4.0, fill='#FF0000')
        self.c.create_line(x + size - 1, y + 1, x + size - 1, y + size - 1, width=4.0, fill='#FF0000')

    # 화면 갱신
    def on_draw(self):
        # 매스 눈금
        self.c.delete('all')
        self.c.create_rectangle(0, 0, 240, 400, width=0.0, fill='#EDAA56')
        for i in range(1, 3):
            self.c.create_line(i * 80 + 1, 40, i * 80, 360, width=2.0, fill='#000000')
        for i in range(5):
            self.c.create_line(0, 40 + i * 80, 240, 40 + i * 80, width=2.0, fill='#000000')

        # 말
        for p in range(12):
            p0, p1 = (p, 11 - p) if self.state.is_first_player() else (11 - p, p)
            if self.state.pieces[p0] != 0:
                self.draw_piece(p, self.state.is_first_player(), self.state.pieces[p0])
            if self.state.enemy_pieces[p1] != 0:
                self.draw_piece(p, not self.state.is_first_player(), self.state.enemy_pieces[p1])

        # 획득한 말
        self.draw_capture(self.state.is_first_player(), self.state.pieces)
        self.draw_capture(not self.state.is_first_player(), self.state.enemy_pieces)

        # 선택 커서
        if 0 <= self.select and self.select < 12:
            self.draw_cursor(int(self.select % 3) * 80, int(self.select / 3) * 80 + 40, 80)
        elif 12 <= self.select:
            self.draw_cursor((self.select - 12) * 40, 360, 40)


# 게임 UI 실행
f = GameUI(model=model)
f.pack()
f.mainloop()
