# 🎧 Lastmon
<img align="right" width="400" height="511" src="https://github.com/user-attachments/assets/de92c5a7-cfb6-4f85-9a46-455bfc080580">
<h4>Display your now playing/top albums and control your music</h4>
<ul>
  <li>Connects to your Last.fm account to display your now playing, no matter which device you're on</li>
  <li>Fetches album art from Spotify if it can't be found on Last.fm</li>
  <li>Displays your top listened albums in the last month when nothing is playing</li>
  <li>Uses a Raspberry Pi Zero and a <a href="https://shop.pimoroni.com/products/display-hat-mini">Pimoroni Display HAT Mini</a></li>
  <li>Optionally, if your music is playing on a Chromecast-enabled device, control your music with the built-in <br>buttons</li>
</ul>
<br>
<blockquote>❗ If you're buying a new Pi for this project, you'll probably want to buy one with pre-soldered headers, unless you want to solder them yourself.</blockquote>
<blockquote>❓ May also work with other ST7789-based 320x240 displays such as <a href="https://www.adafruit.com/product/4311">this one</a></blockquote>
<br>

## 💿 Setup
Assuming you have your Pi set up with Python and your Display HAT Mini installed, clone the repository and:
1. Install dependencies `pip install -r requirements.txt`
2. Create a `.env` file in the root of the repository and add the following environment variables:
   - `LASTFM_USERNAME` - your Last.fm username
   - `LASTFM_API_KEY` - create a Last.fm app [here](https://www.last.fm/api/accounts)
   - `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` - create a Spotify app [here](https://developer.spotify.com/dashboard)
   - (optional) `CHROMECAST_NAME` - if you'd like to control a Chromecast-enabled device with the built-in buttons, set this to the device's name.
   - (optional) `SENTRY_DSN` - if you'd like to know when errors occur, create a Sentry project [here](https://sentry.io/projects/new/) (select Python)

Once set up, you can run Lastmon by running `python app.py`.
> **⁉️ You'll probably want to use PM2/a system service/something similar to run Lastmon on startup.**
