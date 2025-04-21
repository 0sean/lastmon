import ST7789
import threading
import os
import sentry_sdk
from dotenv import load_dotenv

from display_thread import display_thread
from button_thread import button_thread

load_dotenv()

username = os.getenv('LASTFM_USERNAME')
api_key = os.getenv('LASTFM_API_KEY')
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
chromecast_name = os.getenv('CHROMECAST_NAME')
chromecast_enabled = chromecast_name is not None
sentry_dsn = os.getenv('SENTRY_DSN')
sentry_enabled = sentry_dsn is not None

if sentry_enabled:
    sentry_sdk.init(
        dsn=sentry_dsn,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
        enable_tracing=True
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

gif = 0
gifname = ""
            
if __name__ == "__main__":
    print("Starting threads")
    dt = threading.Thread(target=display_thread, args=(disp, api_key, username, spotify_client_id, spotify_client_secret, sentry_enabled))
    dt.start()
    bt = threading.Thread(target=button_thread, args=(disp, chromecast_enabled, chromecast_name))
    bt.start()