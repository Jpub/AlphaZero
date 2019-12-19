import tkinter as tk


# 그래픽 UI 정의
class GraphicUI(tk.Frame):
    # 초기화
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        # 타이틀 표시
        self.master.title('그래픽 그리기')

        # 캔버스 생성
        self.c = tk.Canvas(self, width = 240, height = 240, highlightthickness = 0)
        self.c.pack()

        # 그림 갱신
        self.on_draw()

    # 그림 갱신
    def on_draw(self):
        # 그림 클리어
        self.c.delete('all')

        # 라인 그리기
        self.c.create_line(10, 30, 230, 30, width = 2.0, fill = '#FF0000')

        # 원 그리기
        self.c.create_oval(10, 70, 50, 110, width = 2.0, outline = '#00FF00')

        # 원 채우기
        self.c.create_oval(70, 70, 110, 110, width = 0.0, fill = '#00FF00')

        # 직사각형 그리기
        self.c.create_rectangle(10, 130, 50, 170, width = 2.0, outline = '#00A0FF')

        # 직사각형 채우기
        self.c.create_rectangle(70, 130, 110, 170, width = 0.0, fill = '#00A0FF')

        # 문자열 표시
        self.c.create_text(10, 200, text = 'Hello World', font='courier 20', anchor = tk.NW)


# 그래픽 UI 실행
f = GraphicUI()
f.pack()
f.mainloop()