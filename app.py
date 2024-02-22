import pylast, time, requests
from PIL import Image
from io import BytesIO
import ST7789
import RPi.GPIO as GPIO
import threading
import os
import base64
import pychromecast
import sentry_sdk

username = "***REMOVED***"
api_key = "***REMOVED***"
spotify_client_id = "***REMOVED***"
spotify_client_secret = "***REMOVED***"

sentry_sdk.init(
    dsn="***REMOVED***",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    enable_tracing=True
)

network = pylast.LastFMNetwork(
    api_key=api_key
)

disp = ST7789.ST7789(
    width=320,
    height=240,
    rotation=0,
    port=0,
    cs=1,
    dc=9,
    backlight=13,
    spi_speed_hz=60 * 1000 * 1000
)

disp.begin()

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP) # X
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Y
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP) # A
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP) # B

chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["Bedroom speaker"])
cast = chromecasts[0]
cast.wait()
mc = cast.media_controller

gif = 0
gifname = ""

def display_thread():
    global gif
    global gifname
    while True:
        print("Checking")
        track = network.get_user(username).get_now_playing()
        if track is not None:
            artist = track.get_artist().get_name()
            sentry_sdk.set_context("track", {
                "track_artist": artist,
                "track_title": track.title,
            })
            print(track.artist, "-", track.title)
            image_url = track.get_album().get_cover_image(pylast.SIZE_EXTRA_LARGE)
            if image_url is None:
                spotify_token = requests.post("https://accounts.spotify.com/api/token", data={
                    "grant_type": "client_credentials",
                }, headers={
                    "Authorization": "Basic " + base64.b64encode((spotify_client_id + ":" + spotify_client_secret).encode()).decode()
                }).json()["access_token"]
                spotify_track = requests.get("https://api.spotify.com/v1/search", params={
                    "q": "artist:" + artist + " track:" + track.get_title(),
                    "type": "track",
                }, headers={
                    "Authorization": "Bearer " + spotify_token,
                }).json()["tracks"]["items"][0]
                image_url = spotify_track["album"]["images"][0]["url"]
            image = requests.get(image_url)
            art = Image.open(BytesIO(image.content))
            if image_url.endswith(".gif"):
                if gifname != image_url:
                    gif = art
                    gifname = image_url
                    gt = threading.Thread(target=gif_thread, args=(image_url,))
                    gt.start()
            else:
                gif = 0
                gifname = ""
                art = art.resize((240, 240))
                img = Image.new("RGB", size = (320, 240), color = (0, 0, 0))
                img.paste(art, (40, 0))
                disp.display(img)
            time.sleep(5)
        else:
            sentry_sdk.set_context("track", {
                "artist": "-",
                "title": "-",
            })
            print("No track playing")
            albums = network.get_user(username).get_top_albums(pylast.PERIOD_1MONTH, 9)
            collage = Image.new("RGB", (900, 900))
            for i, album in enumerate(albums):
                image = requests.get(album.item.get_cover_image(pylast.SIZE_EXTRA_LARGE))
                art = Image.open(BytesIO(image.content))
                collage.paste(art, (i % 3 * 300, i // 3 * 300))
            collage = collage.resize((240, 240))
            img = Image.new("RGB", size = (320, 240), color = (0, 0, 0))
            img.paste(collage, (40, 0))
            disp.display(img)
            time.sleep(5)

def button_thread():
    while True:
        if not GPIO.input(16):
            print("Shutdown button pressed")
            img = Image.new("RGB", size = (320, 240), color = (0, 0, 0))
            disp.display(img)
            os.system("sudo shutdown now")
            time.sleep(0.5)
        if not GPIO.input(24):
            print("Play/pause button pressed")
            if mc.status.player_is_playing:
                mc.pause()
            else:
                mc.play()
            time.sleep(0.5)
        if not GPIO.input(5):
            print("Next button pressed")
            mc.queue_next()
            time.sleep(0.5)
        if not GPIO.input(6):
            print("Previous button pressed")
            mc.queue_prev()
            time.sleep(0.5)

def gif_thread(image_url):
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
        # time.sleep(0.02)
        frame += 1
            
if __name__ == "__main__":
    print("Starting threads")
    dt = threading.Thread(target=display_thread)
    dt.start()
    bt = threading.Thread(target=button_thread)
    bt.start()