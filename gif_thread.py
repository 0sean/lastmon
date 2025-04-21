from PIL import Image

def gif_thread(image_url, disp):
    global gif
    global gifname
    frame = gif.tell()
    while gif != 0 and gifname == image_url:
        print("GIF frame show ", frame)
        try:
            gif.seek(frame)
        except EOFError as error:
            print("Seeking to start")
            gif.seek(0)
            frame = 0
        current_frame = gif.copy()
        current_frame = current_frame.resize((240, 240))
        img = Image.new("RGB", size = (320, 240), color = (0, 0, 0))
        img.paste(current_frame, (40, 0))
        disp.display(img)
        frame += 1