import pylast, requests, base64, time, threading, sentry_sdk
from PIL import Image
from io import BytesIO

from gif_thread import gif_thread

def display_thread(disp, api_key, username, spotify_client_id, spotify_client_secret, sentry_enabled):
    network = pylast.LastFMNetwork(
        api_key=api_key
    )

    while True:
        print("Checking")
        try:
            track = network.get_user(username).get_now_playing()
            if track is not None:
                artist = track.get_artist().get_name()
                if sentry_enabled:
                    sentry_sdk.set_context("track", {
                        "track_artist": artist,
                        "track_title": track.title,
                    })
                print(track.artist, "-", track.title)
                image_url = get_track_image(track, spotify_client_id, spotify_client_secret)
                display_image(disp, image_url)
                time.sleep(5)
            else:
                if sentry_enabled:
                    sentry_sdk.set_context("track", {
                        "artist": "-",
                        "title": "-",
                    })
                print("No track playing")
                img = generate_collage(network, username, spotify_client_id, spotify_client_secret)
                disp.display(img)
                time.sleep(5)
        except:
            print("Error in display thread, trying again")

def get_spotify_token(spotify_client_id, spotify_client_secret):
    return requests.post("https://accounts.spotify.com/api/token", data={
            "grant_type": "client_credentials",
        }, headers={
            "Authorization": "Basic " + base64.b64encode((spotify_client_id + ":" + spotify_client_secret).encode()).decode()
        }).json()["access_token"]

def search_spotify(token, type, q):
    return requests.get("https://api.spotify.com/v1/search", params={
                "q": q,
                "type": type,
            }, headers={
                "Authorization": "Bearer " + token,
            }).json()[f"{type}s"]["items"]

def get_track_image(track, spotify_client_id, spotify_client_secret):
    image_url = track.get_album().get_cover_image(pylast.SIZE_EXTRA_LARGE)
    if image_url is None:
        artist = track.get_artist().get_name()
        spotify_token = get_spotify_token(spotify_client_id, spotify_client_secret)
        spotify_track = search_spotify(spotify_token, "track", "artist:" + artist + " track:" + track.get_title())
        if len(spotify_track) == 0:
            image_url = None
        else:
            image_url = spotify_track[0]["album"]["images"][0]["url"]
    return image_url

def generate_collage(network, username, spotify_client_id, spotify_client_secret):
    albums = network.get_user(username).get_top_albums(pylast.PERIOD_1MONTH, 9)
    collage = Image.new("RGB", (900, 900))
    for i, album in enumerate(albums):
        image_url = album.item.get_cover_image(pylast.SIZE_EXTRA_LARGE)
        if image_url is None:
            spotify_token = get_spotify_token(spotify_client_id, spotify_client_secret)
            spotify_album = search_spotify(spotify_token, "album", "artist:" + album.item.get_artist().get_name() + " album:" + album.item.get_title())
            if len(spotify_album) == 0:
                image_url = None
            else:
                image_url = spotify_album[0]["images"][1]["url"]
        if image_url is not None:
            image = requests.get(image_url)
            art = Image.open(BytesIO(image.content))
            collage.paste(art, (i % 3 * 300, i // 3 * 300))
    collage = collage.resize((240, 240))
    img = Image.new("RGB", size = (320, 240), color = (0, 0, 0))
    img.paste(collage, (40, 0))
    return img

def display_image(disp, image_url):
    global gif
    global gifname
    if image_url is not None:
        image = requests.get(image_url)
        art = Image.open(BytesIO(image.content))
        if image_url.endswith(".gif"):
            if gifname != image_url:
                gif = art
                gifname = image_url
                gt = threading.Thread(target=gif_thread, args=(image_url, disp))
                gt.start()
        else:
            gif = 0
            gifname = ""
            art = art.resize((240, 240))
            img = Image.new("RGB", size = (320, 240), color = (0, 0, 0))
            img.paste(art, (40, 0))
            disp.display(img)