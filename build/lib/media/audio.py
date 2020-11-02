from ffmpeg import Error
import sounddevice
import ffmpeg
import time
import numpy
import queue

class Audio():
    def __init__(self):
        self.samples = None
        self.filepath = ""
        self.place = 0
        self.file_info = {}
        self.duration_s = 0
        self.bit_rate = 0
        self.channels = 0
        self.opened = 0
        
    def openfile(self, filepath):
        if self.filepath != filepath:
            self.samples = None
        open(filepath,"rb")
        self.place=0
        self.filepath=filepath
        self.file_info = self.get_file_info()
        self.duration_s = 0
        self.bit_rate = 0
        self.channels = 0
        self.sample_rate = 0
        for v in self.file_info["streams"]:#get file info here. but this may be wrong.
            if v["codec_type"] == "audio":
                self.duration_s += float(v["duration"])
                self.bit_rate = int(v["bit_rate"])
                self.channels = int(v["channels"])
                self.sample_rate = int(v["sample_rate"])
        self.opened = 1
        
    def openurl(self, url):
        if self.filepath != url:
            self.samples = None
        self.place=0
        self.filepath=url
        self.file_info = self.get_file_info()
        self.duration_s = 0
        self.bit_rate = 0
        self.channels = 0
        self.sample_rate = 0
        for v in self.file_info["streams"]:#get file info here. but this may be wrong.
            if v["codec_type"] == "audio":
                self.duration_s += float(v["duration"])
                self.bit_rate = int(v["bit_rate"])
                self.channels = int(v["channels"])
                self.sample_rate = int(v["sample_rate"])
        self.opened = 1
        
    def play(self, place=0, ffmpeg_cmd="ffmpeg"):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        if type(self.samples) == type(None):
            try:
                out, err = (
                    ffmpeg
                    .input(self.filepath)
                    .output('-', format='f32le', acodec='pcm_f32le', ac=self.channels, ab=self.bit_rate, ar=self.sample_rate)
                    .run(cmd=ffmpeg_cmd, capture_stdout=True, capture_stderr=True)
                )
            except Error as err:
                print(err.stderr)
                raise
            if self.channels != 1:
                self.samples = numpy.frombuffer(out, numpy.float32).reshape(-1,self.channels)
            else:
                self.samples = numpy.frombuffer(out, numpy.float32)
            if place != 0:
                sounddevice.play(self.samples[self.sample_rate*place:-1], self.sample_rate)
            else:
                sounddevice.play(self.samples, self.sample_rate)
        else:
            if place != 0:
                sounddevice.play(self.samples[self.sample_rate*place:-1], self.sample_rate)
            else:
                sounddevice.play(self.samples, self.sample_rate)

    def stop(self):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        sounddevice.stop()
        
    def goto(self, place, **args):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        self.stop()
        self.play(place=place, **args)
        
    def get_file_info(self,filepath=None, key=None, cmd="ffprobe"):
        if filepath == None:
            info = ffmpeg.probe(self.filepath, cmd=cmd)
        else:
            info = ffmpeg.probe(filepath, cmd=cmd)
        if key == None:
            return info
        else:
            return info[key]
        
##    def get_player(self):
##        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
##        return self.player
    
    def get_status(self):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        return sounddevice.get_status()
    
    def close(self):
        if not self.opened: raise IOError("File is not opened. Please use 'openfile' function before do this.")
        self = self.__init__()

def get_devicelist():
    return sounddevice.query_devices()

def get_apilist():
    return sounddevice.query_hostapis()

def get_status():
    return sounddevice.get_status()

def get_file_info(filepath,cmd="ffprobe"):
    return ffmpeg.probe(filepath, cmd=cmd)
