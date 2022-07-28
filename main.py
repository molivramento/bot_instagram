import os
import time
from dotenv import load_dotenv
from random import randint
from instagrapi import Client
from instagrapi.types import UserShort

load_dotenv()

IG_USERNAME = os.getenv('ACCOUNT_USERNAME')
IG_PASSWORD = os.getenv('ACCOUNT_PASSWORD')
IG_CREDENTIAL_PATH = './ig_settings.json'


class Bot:
    def __init__(self):
        self._cl = Client()
        if os.path.exists('IG_CREDENTIAL_PATH'):
            self._cl.load_settings(IG_CREDENTIAL_PATH)
            self._cl.login(IG_USERNAME, IG_PASSWORD)
        else:
            self._cl.login(IG_USERNAME, IG_PASSWORD)
            self._cl.dump_settings(IG_CREDENTIAL_PATH)
        self.main_id = self._cl.user_id

    def follow_by_username(self, username: str) -> bool:
        user_id = self._cl.user_id_from_username(username)
        return self._cl.user_follow(user_id)

    def unfollow_by_username(self, username) -> bool:
        user_id = self._cl.user_id_from_username(username)
        return self._cl.user_unfollow(user_id)

    def unfollow_by_id(self, id_in) -> bool:
        return self._cl.user_unfollow(id_in)

    def get_followers(self, amount: int = 0) -> dict[int, UserShort]:
        return self._cl.user_followers_v1(user_id=self.main_id, amount=amount)

    def get_followers_username(self, unsername: str, amount: int = 0) -> list[str]:
        user_id = self._cl.user_id_from_username(unsername)
        followers = self._cl.user_followers(user_id, amount=amount)
        return [user.username for user in followers.values()]

    def get_following(self, amount: int = 0) -> list[str]:  # dict[int, UserShort]:
        return self._cl.user_following(self._cl.user_id, amount=amount)

    def get_following_usernames(self, amount: int = 0) -> list[str]:
        following = self._cl.user_following(self._cl.user_id, amount=amount)
        return [user.username for user in following.values()]

    def run_unfollow(self):
        usernames = Bot.get_following(self)
        for u in usernames:
            Bot.unfollow_by_id(self, u)
            print(f'unfollowed {u}')
            time.sleep(randint(400, 680))


    def run(self):
        usernames = Bot.get_followers(self, self._cl.user_id)
        for u in usernames:
            scanning = str(u.username)
            print(f'Scaning {scanning}')
            with open('./scanned_user.txt', 'r+') as su:
                followers = Bot.get_followers_username(self, scanning)
                for f in followers:
                    working = f
                    print(f'Working {working}')
                    user_id = self._cl.user_id_from_username(working)
                    info = self._cl.user_info_v1(user_id=user_id)
                    with open('./try_follow.txt', 'r+') as tf:
                        if (not info.is_business
                                and info.following_count > 20
                                and not info.is_private
                                and u not in tf):
                            if Bot.follow_by_username(self, working):
                                print(f'Following {working}')
                                time.sleep(randint(200, 380))
                            else:
                                print(f'Skip {working}')
                                time.sleep(30)
                        tf.write(working + '\n')
                        print(f'Added in try_follow.txt')
                su.write(scanning + '\n')
                print(f'{scanning} Added in scanned_user.txt')


if __name__ == '__main__':
    bot = Bot()
    bot.run_unfollow()