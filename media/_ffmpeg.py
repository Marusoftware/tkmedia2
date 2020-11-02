import ffmpeg, os, queue, threading
import numpy as np

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

    def OPEN(self, filename, mode):
        """
        Open Video File
        filename : filename
        mode : r(read) or w(write) or rw(both)
        """
        if mode == "w":
            self.mode = "w"
            self._ffmpeg = ffmpeg.input(self.filename)
            self.filename = filename
        elif mode == "r":
            if os.path.exists(filename):
                self.mode = "r"
                self.filename = filename
            else:
                raise FileNotFoundError
        elif mode == "rw":
            if os.path.exists(filename):
                self.mode = "rw"
                self._ffmpeg = ffmpeg.input(self.filename)
                self.filename = filename
            else:
                raise FileNotFoundError

    def LOAD(self, pipe_stdin=True, pipe_stdout=True, pipe_stderr=True):
        """
        Load Video file
        pipe_stdin , pipe_stdout , pipe_stderr : bool
        """
        if mode == "r" or mode == "rw":
            self._ffmpeg = self._ffmpeg.output('pipe:', format='rawvideo', pix_fmt='rgb24')
            self.process = self._ffmpeg.run_async(pipe_stdin=pipe_stdin, pipe_stdout=pipe_stdout, pipe_stderr=pipe_stderr)
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
                pass
            if com[0] == "wait":
                com = self.command_q.get(timeout=com[1])
            elif com[0] == "load":
                self.process.stdout.read(width * height * 3)

    def WRITE(self, pipe_stdin=True, pipe_stdout=True, pipe_stderr=True):
        """
        Write to Video File
        pipe_stdin , pipe_stdout , pipe_stderr : bool
        """
        if mode == "w" or mode == "rw":
            self.__ffmpeg = ffmpeg.input("pipe")
            return self.buffer
    def READ(self, place):
        if mode == "r" or mode == "rw":
            pass

def INFO(filename):
    return ffmpeg.probe(filename)

if __name__ == "__main__":
    in_filename = "/home/maruo/test.mts"

    probe = ffmpeg.probe(in_filename)
    for v in probe["streams"]:#get file info here. but this may be wrong.
        if v["codec_type"] == "video":
            height = v["height"]
            width = v["width"]

    process1 = (
        ffmpeg
        .input(in_filename)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
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
    in_bytes = process1.stdout.read(width * height * 3)
    #    if not in_bytes:
    #        break
    in_frame = (
        np
        .frombuffer(in_bytes, np.uint8)
        .reshape([height, width, 3])
    )
    print(in_frame)
    #    out_frame = in_frame * 0.3
    #    process2.stdin.write(
    #        frame
    #        .astype(np.uint8)
    #        .tobytes()
    #    )

    #process2.stdin.close()
    process1.wait()
    #process2.wait()
