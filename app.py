# -*- coding: utf-8 -*-

import sys
import requests
import os

from glob import iglob

from os.path import expandvars
from urllib.parse import quote

from enum import IntEnum, unique
from subprocess import Popen

class RobloxAPI:
    def __init__(self, cookie):
        self.sess = requests.Session()
        self.sess.cookies[".ROBLOSECURITY"] = cookie

    @staticmethod
    def csrf_token() -> str:
        resp = requests.post("https://auth.roblox.com/v2/login")
        return resp.headers["X-CSRF-TOKEN"]

    @staticmethod
    def username_info(user) -> dict:
        resp = requests.get("http://api.roblox.com/users/get-by-username", params={ "username": user })
        return resp.json()

    def game_authentication(self, place_id) -> str:
        resp = self.sess.get("https://www.roblox.com/game-auth/getauthticket", headers={ "RBX-For-Gameauth": "true",
                                                                                         "Referer": "https://www.roblox.com/games/{game_id}" })
        return resp.text

    def post_with_token(self, url, data=None, json=None, **kwargs) -> requests.Response:
        kwargs.update({ "headers": { "X-CSRF-TOKEN": self.csrf_token() } })
        return self.sess.post(url, data, json, **kwargs)

    def get_user_presence(self, *args) -> dict:
        return self.post_with_token("https://presence.roblox.com/v1/presence/users", json={ "userIds": args }).json()


@unique
class Status(IntEnum):
    OFFLINE = 0
    ONLINE = 1
    PLAYING = 2


def user_presence(rb, uid) -> dict:
    users = rb.get_user_presence(uid).get("userPresences")

    if not users:
        sys.exit("Error: invalid auth")

    return users[0]

def player_path() -> str:
    return "C:\\Users\\admin\\AppData\\Local\\Roblox\\Versions\\version-91f017face444efd\\RobloxPlayerLauncher.exe"

def load_player(auth, place_id):
    url = quote(f"https://assetgame.roblox.com/game/PlaceLauncher.ashx?request=RequestGameJob&placeId={place_id}")
    arg = f"roblox-player:1+launchmode:play+gameinfo:{auth}+placelauncherurl:{url}"
    print(arg)
    os.system("cd C:\\Users\\admin\\AppData\\Local\\Roblox\\Versions\\version-91f017face444efd")
    try:
        Popen([ "RobloxPlayerLauncher.exe", arg ], shell=False)
    except FileNotFoundError:
        sys.exit("Error: latest version of Roblox not found")

def join_game(rb, place_id) -> bool:
    auth = rb.game_authentication(place_id)
    load_player(auth, place_id)

    return True

def init():
    cookie = input("Enter ROBLOSECURITY: ")
    rb = RobloxAPI(cookie)

    place_id = input("Enter Place ID: ")
    
    join_game(rb, place_id)

if __name__ == "__main__":
    try:
        init()
    except KeyboardInterrupt:
        pass
