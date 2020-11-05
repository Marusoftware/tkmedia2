from .audio import Audio
from .video import Video
from ._video_beta import Video as Video_beta
import ffmpeg

__copyright__    = 'Copyright (C) 2020 Marusoftware'
__version__      = '1.0_beta'
__license__      = 'BSD-3-Clause'
__author__       = 'Marusoftware'
__author_email__ = 'marusoftware@outlook.jp'
__url__          = 'https://marusoftware.ddns.net'

#__all__ = ['audio', 'video']
__all__ = ["Audio","Video","Video_beta"]

def get_file_info(filepath,cmd="ffprobe"):
    return ffmpeg.probe(filepath, cmd=cmd)
