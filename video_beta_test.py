import media
import tkinter
import sys

def b1_handle():
    m._ffmpeg.command_q.put("exit")
    m.canvas.after_cancel(m.aid)
    r.destroy()
    sys.exit()

status = 0

def b2_handle():
    global status
    if status:
        m._ffmpeg.command_q.put("start")
        m._ffmpeg.command_q.put("load")
        m.player_canvas(r)
        b2.configure(text="stop")
        status = 0
    else:
        m._ffmpeg.command_q.put("stop")
        m.canvas.after_cancel(m.aid)
        m.canvas.destroy()
        b2.configure(text="start")
        status = 1

m = media.Video_beta()
m.openfile("/home/maruo/ミュージック/悲愴.mp4")
r = tkinter.Tk()
b1 = tkinter.Button(r, text="exit", command=b1_handle)
b2 = tkinter.Button(r, text="stop", command=b2_handle)
b1.pack()
b2.pack()
m.player_canvas(r)
r.mainloop()