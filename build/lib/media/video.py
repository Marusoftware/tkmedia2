import tkinter
from tkinter import ttk
import imageio
from PIL import ImageTk, Image
import time
try:
    from .audio import Audio
except:
    from audio import Audio
import threading
from imageio.plugins.ffmpeg import FfmpegFormat#old
import ffmpeg
import queue
import numpy

#stop_frag = None

class Video():
    #global stop_frag
    def __init__(self):
        self.audio = Audio()
        self.filepath = ""
        self.opened = 0
        format = FfmpegFormat(
            "ffmpeg",
            "Many video formats and cameras (via ffmpeg)",
            ".mov .avi .mpg .mpeg .mp4 .mkv .wmv .webm .mts .m2ts .m4v",
            "I",
            )
        imageio.formats.add_format(format,True)
        self.lock = threading.Lock()
        
    def openfile(self, filepath):
        try:
            self.video = imageio.get_reader(filepath)
        except imageio.core.fetching.NeedDownloadError:
            imageio.plugins.avbin.download()
            self.video = imageio.get_reader(filepath)
        self.audio.openfile(filepath)
        self.filepath = filepath
        self.opened = 1
    
    def playonframe(self, frame, place=0):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        self.frame = frame
        mode = "f"
        self.frame.vidframe = ttk.Label(self.frame)
        self.frame.vidframe.pack(fill="both",expand=True)
        self.video_thread = threading.Thread(target=self._stream,args=(place,mode))
        self.video_thread.start()
        #self.stop_frag = tkinter.BooleanVar(frame,False)

    def playoncanvas(self, canvas, place=0):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        self.frame = canvas
        mode = "c"
        self.video_thread = threading.Thread(target=self._stream,args=(place,mode))
        self.video_thread.start()
        #self.stop_frag = tkinter.BooleanVar(canvas,False)

    def release(self, place):
        self.audio.play(place=place)
        self.lock.release()
    
    def stop(self):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        self.audio.stop()
        self.lock.release()
        self.lock.acquire()
        #self.video_thread.stop()
        #self.stop_frag.set(True)
        
    def goto(self,place, frame=None):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        if type(frame) != type(None): self.frame = frame
        self.stop()
        self.play(frame=self.frame, place=place)
        self.audio.goto(place)
        
    def goto_audio(self,place):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        self.audio.goto(place)
        
    def close(self):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        self.filepath=""
        self.opened = 0
        self.stop()
    
    def _stream(self,place,mode):
        global stop_frag
        self.audio.play()
        start_time=time.time()
        sleeptime = 1/self.video.get_meta_data()["fps"]
        frame_now = 0
        for image in self.video.iter_data():
            self.lock.acquire()
            frame_now = frame_now + 1
            if frame_now*sleeptime >= place:
                if frame_now*sleeptime >= time.time()-start_time:
                    frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize((int(self.frame.winfo_width()),int(self.frame.winfo_height())),Image.BOX),master=self.frame)
                    if mode == "f":
                        self.frame.vidframe.config(image=frame_image)
                        self.frame.vidframe.image = frame_image
                    else:
                        if not frame_now > 1:
                            self.frame.delete("image")
                        self.frame.create_image(0,0,image=frame_image,tags="image",anchor="nw")
                        self.frame.image = frame_image
                    time.sleep(sleeptime)
                else:
                    pass
            else:
                pass
            self.lock.release()

class New_Video():
    def __init__(self):
        self.audio = Audio()
        self.samples = None
        self.filepath = ""
        self.place = 0
        self.file_info = {}
        self.duration_s = 0
        self.fps = 0
        self.opened = 0
        self.array_queue = queue.Queue()
        self.command_queue1 = queue.Queue()
        self.command_queue2 = queue.Queue()
        
    def openfile(self, filepath):
        if self.filepath != filepath:
            self.samples = None
        open(filepath,"rb")
        self.place=0
        self.filepath=filepath
        self.file_info = self.get_file_info()
        self.duration_s = 0
        self.fps = 0
        for v in self.file_info["streams"]:#get file info here. but this may be wrong.
            if v["codec_type"] == "video":
                self.duration_s += float(v["duration"])
                self.height = v["height"]
                self.width = v["width"]
                self.fps = eval(v["r_frame_rate"])
        self.audio.openfile(filepath)
        self.opened = 1

    def playonframe(self, frame, place=0):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        self.frame = frame
        self.type = "f"
        self.video_thread = threading.Thread(target=self._load)
        self.video_thread.start()
        self.command_queue1.put({'command' : 'play', 'place' : place})
        self.command_queue2.put({'command' : 'play', 'place' : place})

    def playoncanvas(self, frame, place=0):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        self.frame = frame
        self.type="c"
        self.command_queue1.put({'command' : 'play', 'place' : place})
        self.command_queue2.put({'command' : 'play', 'place' : place})
        self.video_load_thread = threading.Thread(target=self._load)
        self.video_load_thread.start()
        self.video_play_thread = threading.Thread(target=self._play)
        self.video_play_thread.start()        

##    def stop(self):
##        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
##        self.audio.stop()
##        self.video_thread.stop()
##        
##    def goto(self,place, frame=None):
##        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
##        if type(frame) != type(None): self.frame = frame
##        self.stop()
##        self.play(frame=self.frame, place=place)
##        self.audio.goto(place)
##        
##    def goto_audio(self,place):
##        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
##        self.audio.goto(place)
##        
##    def close(self):
##        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
##        pass
##    
    def _load(self):
        status = ""
        while 1:
            try:
                com = self.command_queue1.get(block=False)
            except queue.Empty:
                com = {'command': 'continue'}
                
            if com["command"] == "play":
                self.sub = (
                    ffmpeg
                    .input(self.filepath)
                    .output('pipe:', format='rawvideo', pix_fmt='rgb24')
                    .run_async(pipe_stdout=True)
                )
                print("start_f")
                #self.sub.stdout.seek(com["place"])
                array = numpy.frombuffer(self.sub.stdout.read(self.height*self.width*120),numpy.uint8).reshape([-1, self.height, self.width, 3])
                for i in array:
                    self.array_queue.put(Image.fromarray(i))
                status = "play"
            elif com["command"] == "continue":
                if status == "play":
                    array = numpy.frombuffer(self.sub.stdout.read(self.height*self.width*120),numpy.uint8).reshape([-1, self.height, self.width, 3])
                    for i in array:
                        self.array_queue.put(Image.fromarray(i))
                    time.sleep(0.01)
                elif status == "stop":
                    time.sleep(0.1)
            elif com["command"] == "stop":
                status = "stop"
            elif com["command"] == "move":
                while 1:
                    try:
                        self.array_queue.get(block=False)
                    except queue.Empty:
                        break
                self.sub = (
                    ffmpeg
                    .input(self.filepath)
                    .output('pipe:', format='rawvideo', pix_fmt='rgb24')
                    .run_async(pipe_stdout=True)
                )
                #self.sub.stdout.seek(com["place"]*self.height*self.width*12)
                array = numpy.frombuffer(self.sub.stdout.read(self.height*self.width*1200),numpy.uint8).reshape([-1, height, width, 3])
                for i in array:
                    self.array_queue.put(Image.fromarray(i))
            elif com["command"] == "close":
                while 1:
                    try:
                        self.array_queue.get(block=False)
                    except queue.Empty:
                        break
                self.sub.poll()
                if type(self.sub.returncode) == type(None):
                    self.sub.kill()
                break
    def _play(self):
        status = ""
        while 1:
            try:
                com = self.command_queue2.get(block=False)
            except queue.Empty:
                com = {'command': 'continue'}
            if com["command"] == "play":
                status = "play"
                sleeptime = 1/self.fps
                #frame_now = int(com["place"]*self.fps)
                frame_now=0
                image = self.array_queue.get()
                start_time=time.time()
                self.audio.play(place=com["place"])
                if frame_now*sleeptime >= place:
                    if frame_now*sleeptime >= time.time()-start_time:
                   インタラクティブセッションの表現には、プロンプトと、Pythonコードが表示する出力も含める必要があります。インタラクティブセッション用の特別なマークアップはありません。最後の行の後、もしくは出力を書いているところには、”未使用の”プロンプトは置いてはいけません。下記の例は しないほうがいいもの の例です。:     frame_image = ImageTk.PhotoImage(image.resize((int(self.frame.winfo_width()),int(self.frame.winfo_height())),Image.BOX),master=self.frame)
                        if self.type == "f":
                            self.frame.config(image=frame_image)
                            self.frame.image = frame_image
                        else:
                            if not frame_now > 1:
                                self.frame.delete("image")
                            self.frame.create_image(0,0,image=frame_image,tags="image",anchor="nw")
                            self.frame.image = frame_image
                        time.sleep(sleeptime)
                    else:
                        pass
                else:
                    pass
                frame_now = frame_now + 1
            elif com["command"] == "continue":
                if status == "play":
                    image = self.array_queue.get()
                    if frame_now*sleeptime >= place:
                        if frame_now*sleeptime >= time.time()-start_time:
                            frame_image = ImageTk.PhotoImage(image.resize((int(self.frame.winfo_width()),int(self.frame.winfo_height())),Image.BOX),master=self.frame)
                            if self.type == "f":
                                self.frame.config(image=frame_image)
                                self.frame.image = frame_image
                            else:
                                if not frame_now > 1:
                                    self.frame.delete("image")
                                self.frame.create_image(0,0,image=frame_image,tags="image",anchor="nw")
                                self.frame.image = frame_image
                            time.sleep(sleeptime)
                        else:
                            pass
                    else:
                        pass
                    frame_now = frame_now + 1
                elif status == "stop":
                    time.sleep(0.1)
            elif com["command"] == "close":
                break
            else:
                print(com)
            self.command_queue2.task_done()
    def get_file_info(self,filepath=None, key=None, cmd="ffprobe"):
        if filepath == None:
            info = ffmpeg.probe(self.filepath, cmd=cmd)
        else:
            info = ffmpeg.probe(filepath, cmd=cmd)
        if key == None:
            return info
        else:
            return info[key]
