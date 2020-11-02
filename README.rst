#######
TkMedia
#######
     by Marusoftware

**********************
Tkinter Media Support.
**********************

This libraly can play audio and video(on Canvas or Frame).

=======
Example
=======

-----
Audio
-----

::

    import media
    audio = media.Audio()
    audio.openfile("/path/to/audiofile")
    audio.play()
    while True:
        if input() == "stop":
            audio.stop()

-----
Video
-----

::

    import media
    import tkinter
    root = tkinter.Tk()
    video = media.Video()
    video.openfile("/path/to/videofile")
    video.playoncanvas(root)
    root.mainloop()
    video.stop()
