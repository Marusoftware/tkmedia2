import ffmpeg, os, queue, threading, time
import numpy as np
from PIL import ImageTk, Image

__all__ = ["VIDEO","AUDIO","INFO"]

class VIDEO():
    def __init__(self):
        self.mode = ""
        self.filename = ""
        self._ffmpeg = ""
        self.process = ""
        self.command_q = queue.Queue()
        self.buffer = queue.Queue()
        self.thread = ""
        self.info = {}
        self.probe = {}

    def OPEN(self, filename, mode):
        """
        Open Video File
        filename : filename
        mode : r(read) or w(write) or rw(both)
        """
        filename = os.path.abspath(filename)
        if "w" in mode:
            self.mode = "w"
            self.filename = filename
        if "r" in mode:
            if os.path.exists(filename):
                self.mode = "r"
                self.filename = filename
                self._ffmpeg = ffmpeg.input(self.filename)
                self.probe = INFO(filename)
                self.info = {}
                self.duration_s = 0
                for v in self.probe["streams"]:#get file info here. but this may be wrong.
                    if v["codec_type"] == "video":
                        self.duration_s += float(v["duration"])
                        self.info.update(height=v["height"])
                        self.info.update(width=v["width"])
                        self.info.update(fps=eval(v["r_frame_rate"]))
                self.info.update(duration_s=self.duration_s)
            else:
                raise FileNotFoundError
        if mode == "rw":
            self.mode = "rw"

    def LOAD(self, pipe_stdin=True, pipe_stdout=True, pipe_stderr=True):
        """
        Load Video file
        pipe_stdin , pipe_stdout , pipe_stderr : bool
        """
        if self.mode == "r" or self.mode == "rw":
            self._ffmpeg = ffmpeg.input(self.filename)
            self._ffmpeg = self._ffmpeg.output('pipe:', format='rawvideo', pix_fmt='rgba')
            self.process = self._ffmpeg.run_async(pipe_stdin=pipe_stdin, pipe_stdout=pipe_stdout, pipe_stderr=pipe_stderr)
            for i in range(100):
                self.command_q.put(["load"])
            self.thread = threading.Thread(target=self._LOAD)
            self.thread.start()

    def _LOAD(self):
        """
        DO NOT USE THIS FUNC DIRECTLY
        """
        while True:
            try:
                com = self.command_q.get_nowait()
            except queue.Empty:
                com = ["pass"]
            else:
                self.command_q.task_done()
            if com[0] == "wait":
                com = self.command_q.get(timeout=com[1])
            elif com[0] == "load":
                try :
                    self.buffer.put(Image.frombuffer("RGBA", (self.info["width"],self.info["height"]), self.process.stdout.read(self.info["width"] * self.info["height"] * 4), "raw"))
                except ValueError:
                    break
            elif com[0] == "pass":
                time.sleep(0.0001)
            elif com[0] == "exit":
                break

    def WRITE(self, pipe_stdin=True, pipe_stdout=True, pipe_stderr=True):
        """
        Write to Video File
        pipe_stdin , pipe_stdout , pipe_stderr : bool
        """
        if self.mode == "w" or self.mode == "rw":
            self.__ffmpeg = ffmpeg.input("pipe")
            return self.buffer
    
    def READ(self):
        if self.mode == "r" or self.mode == "rw":
            self.command_q.put(["load"])
            buffer = self.buffer.get_nowait()
            self.buffer.task_done()
            return buffer
    
    def READ_TK(self, master, block=False):
        if self.mode == "r" or self.mode == "rw":
            self.command_q.put(["load"])
            buffer = ImageTk.PhotoImage(self.buffer.get(block=block), master=master)
            self.buffer.task_done()
            return buffer

def INFO(filename):
    return ffmpeg.probe(filename)

if __name__ == "__main__":
    in_filename = "/home/maruo/ミュージック/悲愴.mp4"

    probe = ffmpeg.probe(in_filename)
    for v in probe["streams"]:#get file info here. but this may be wrong.
        if v["codec_type"] == "video":
            height = v["height"]
            width = v["width"]

    process1 = (
        ffmpeg
        .input(in_filename)
        .output('pipe:', format='rawvideo', pix_fmt='rgba')
        .run_async(pipe_stdout=True)
    )

    #process2 = (
    #    ffmpeg
    #    .input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(width, height))
    #    .output(out_filename, pix_fmt='yuv420p')
    #    .overwrite_output()
    #    .run_async(pipe_stdin=True)
    #)

    #while True:
    in_bytes = process1.stdout.read(width * height * 4)
    #    if not in_bytes:
    #        break
    in_frame = (
        np
        .frombuffer(in_bytes, np.uint8)
        .reshape([height, width, 4])
    )
    print(in_frame)
    print(Image.frombuffer("RGBA",(width,height),in_bytes, "raw"))
    Image.frombuffer("RGBA",(width,height),in_bytes, "raw").show()
    #    out_frame = in_frame * 0.3
    #    process2.stdin.write(
    #        frame
    #        .astype(np.uint8)
    #        .tobytes()
    #    )
    #while True:
    #    if process1.
    #process2.stdin.close()
    #process1.wait()
    #process2.wait()
