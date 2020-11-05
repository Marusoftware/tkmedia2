import media
import tkinter

m = media.Video_beta()
m.openfile("/home/maruo/ミュージック/悲愴.mp4")
r = tkinter.Tk()
b1 = tkinter.Button(r, text="exit", command=lambda: m._ffmpeg.command_q.put("exit"))
b2 = tkinter.Button(r, text="stop", command=lambda: m._ffmpeg.command_q.put("wait"))
b1.pack()
b2.pack()
m.player_canvas(r)
r.mainloop()