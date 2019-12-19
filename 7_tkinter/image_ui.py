import tkinter as tk
from PIL import Image, ImageTk


# 이미지 UI 정의
class ImageUI(tk.Frame):
    # 초기화
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        # 타이틀 표시
        self.master.title('이미지 그리기')

        # 이미지 로드
        image = Image.open('sample.png')
        self.images = []
        self.images.append(ImageTk.PhotoImage(image))
        self.images.append(ImageTk.PhotoImage(image.rotate(180)))

        # 캔버스 생성
        self.c = tk.Canvas(self, width = 240, height = 240, highlightthickness = 0)
        self.c.pack()

        # 화면 생성
        self.on_draw()

    # 화면 갱신
    def on_draw(self):
        # 화면 삭제
        self.c.delete('all')

        # 이미지 그리기
        self.c.create_image(10, 10, image=self.images[0],  anchor=tk.NW)

        # 반전 이미지 그리기
        self.c.create_image(10, 100, image=self.images[1],  anchor=tk.NW)


# 이미지 UI 실행
f = ImageUI()
f.pack()
f.mainloop()