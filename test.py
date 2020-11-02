import media, tkinter, time

def command():
    if vid.playing == -1:
        vid.playoncanvas(root.f)
        root.b.configure(text="stop")
        vid.playing = 1
    elif vid.playing == 0:
        vid.release(0)
        vid.goto(int(time.time() - vid.time))
        root.b.configure(text="stop")
        vid.playing = 1
    else:
        vid.stop()
        root.b.configure(text="start")
        vid.playing = 0

root = tkinter.Tk()
vid = media.video.New_Video()
vid.playing = -1
vid.time = time.time()
vid.openfile("/home/maruo/test.mts")
root.f = tkinter.Canvas(root, height=100, width=100)
root.f.pack(fill="both",expand=True)
root.b = tkinter.Button(root,text="start",command=command)
root.b.pack(fill="both")
#vid.playoncanvas(root.f)
root.mainloop()
