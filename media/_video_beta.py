from . import _ffmpeg
import tkinter
import threading
import time
from PIL import ImageTk

class Video():
    def __init__(self):
        self._ffmpeg = _ffmpeg.VIDEO()
    def openfile(self, filename):
        self._ffmpeg.OPEN(filename, "r")
        self._ffmpeg.LOAD(pipe_stderr=False)
    def player_canvas(self, master, zoom=1, debug=0):
        self.canvas = tkinter.Canvas(master)
        self.canvas.pack(fill="both", expand=True)
        self.start_time=time.time()
        self.frame_now = 0
        self.wait_time = 1 / self._ffmpeg.info["fps"] * 1000 * zoom
        self._player_canvas()
        self.aid = ""
        #self.thread = threading.Thread(target=self._player_canvas)
        #self.thread.start()
    def _player_canvas(self):
        if self.frame_now*self.wait_time >= time.time()-self.start_time:
            if self.frame_now != 0:
                self.canvas.delete("image")
            try:
                image = self._ffmpeg.READ(block=False)
                self.image = ImageTk.PhotoImage(image,master=self.canvas)
                image.close()
            except:
                pass
            else:
                #print(self._ffmpeg.buffer.qsize())
                #if self._ffmpeg.buffer.qsize() < 100:
                #    print(self._ffmpeg.command_q.qsize())
                self.canvas.create_image(0, 0, anchor="nw", image=self.image, tags="image")
                self.frame_now = self.frame_now + 1
            self.aid = self.canvas.after(int(self.wait_time), self._player_canvas)
        else:
            self._ffmpeg.READ_TK(self.canvas, block=True)
            self.frame_now = self.frame_now + 1
            self.aid = self.canvas.after(0, self._player_canvas)
        
        