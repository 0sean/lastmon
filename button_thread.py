import os, time, pychromecast
import RPi.GPIO as GPIO
from PIL import Image

def button_thread(disp, chromecast_enabled, chromecast_name):
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP) # X - Shutdown
    GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Y - Play/pause
    GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP) # A - Next
    GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP) # B - Previous

    if chromecast_enabled:
        chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[chromecast_name])
        cast = chromecasts[0]
        cast.wait()
        mc = cast.media_controller

    while True:
        if not GPIO.input(16):
            print("Shutdown button pressed")
            img = Image.new("RGB", size = (320, 240), color = (0, 0, 0))
            disp.display(img)
            os.system("sudo shutdown now")
            time.sleep(0.5)
        if not GPIO.input(24) and chromecast_enabled:
            print("Play/pause button pressed")
            if mc.status.player_is_playing:
                mc.pause()
            else:
                mc.play()
            time.sleep(0.5)
        if not GPIO.input(5) and chromecast_enabled:
            print("Next button pressed")
            mc.queue_next()
            time.sleep(0.5)
        if not GPIO.input(6) and chromecast_enabled:
            print("Previous button pressed")
            mc.queue_prev()
            time.sleep(0.5)