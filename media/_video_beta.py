from . import _ffmpeg
import tkinter
import threading
import time

class Video():
    def __init__(self):
        self._ffmpeg = _ffmpeg.VIDEO()
    def openfile(self, filename):
        self._ffmpeg.OPEN(filename, "r")
        self._ffmpeg.LOAD()
    def player_canvas(self, master):
        self.canvas = tkinter.Canvas(master)
        self.canvas.pack(fill="both", expand=True)
        self.thread = threading.Thread(target=self._player_canvas)
        self.thread.start()
    def _player_canvas(self):
        start_time=time.time()
        frame_now = 0
        wait_time = 1 / self._ffmpeg.info["fps"]
        time.sleep(wait_time)
        print(wait_time)
        while 1:
            if frame_now*wait_time >= time.time()-start_time:
                if frame_now != 0:
                    self.canvas.delete("image")
                self.image = self._ffmpeg.READ_TK(self.canvas, block=True)
                self.canvas.create_image(self._ffmpeg.info["width"]/2, self._ffmpeg.info["height"]/2, image=self.image, tags="image")
                time.sleep(wait_time)
            else:
                self._ffmpeg.READ_TK(self.canvas, block=True)
            frame_now = frame_now + 1