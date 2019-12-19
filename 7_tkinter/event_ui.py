import tkinter as tk
from PIL import Image, ImageTk


# 이벤트 UI 정의
class EventUI(tk.Frame):
    # 초기화
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        # 타이틀 표시
        self.master.title('이벤트 처리')

        # 클릭 위치
        self.x = 0
        self.y = 0

        # 캔버스 생성
        self.c = tk.Canvas(self, width = 240, height = 240, highlightthickness = 0)
        self.c.bind('<Button-1>', self.on_click)  # 클릭 판정 추가
        self.c.pack()

        # 화면 갱신
        self.on_draw()

    # 클릭 시 호출
    def on_click(self, event):
        self.x = event.x
        self.y = event.y
        self.on_draw()

    # 화면 갱신
    def on_draw(self):
        # 그림 삭제
        self.c.delete('all')

        # 문자열 표시
        str = '클릭 위치 {},{}'.format(self.x, self.y)
        self.c.create_text(10, 10, text = str, font='courier 16', anchor = tk.NW)


# 이벤트 UI 실행
f = EventUI()
f.pack()
f.mainloop()