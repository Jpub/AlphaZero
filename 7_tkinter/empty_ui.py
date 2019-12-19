import tkinter as tk


# 빈 UI 생성
class EmptyUI(tk.Frame):
    # 초기화
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        # 타이틀 표시
        self.master.title('Hello World')

        # 캔버스 생성
        self.c = tk.Canvas(self, width = 240, height = 240, highlightthickness = 0)
        self.c.pack()


# 빈 UI 실행
f = EmptyUI()
f.pack()
f.mainloop()