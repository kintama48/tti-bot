import json
import sys
import tweepy
import os
import discord
import asyncio
import time

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

API_KEY = config["API_key"]
API_SECRET = config["API_secret"]
ACCESS_KEY = config["access_key"]
ACCESS_SECRET = config["access_secret"]
USER_TO_SNITCH = config["user_handle"]
DISCORD_BOT_TOKEN = config["token"]
alert_channel_id = config["alert_channel_id"]
all_channel_id = config["all_channel_id"]

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)
user = api.get_user(screen_name=USER_TO_SNITCH)

client = discord.Client()


def alert_found(text):
    text = text.replace("#alert", "").strip()
    text = text.replace("#Alert", "").strip()
    text = text.replace("#ALERT", "").strip()
    print("Inside alert_found")
    if "SOLD" in text or "sold" in text or "Sold" in text:
        text = text.replace("sold", "").strip()
        text = text.replace("Sold", "").strip()
        text = text.replace("SOLD", "").strip()
        return discord.Embed(color=0xff0a0a, description=f"🔔 **ALERT - SOLD - **{text}")

    if "BOUGHT" in text or "bought" in text or "Bought" in text:
        text = text.replace("bought", "").strip()
        text = text.replace("Bought", "").strip()
        text = text.replace("BOUGHT", "").strip()
        return discord.Embed(color=0x1dfc00, description=f"🔔 **ALERT - BOUGHT - **{text}")
    return discord.Embed(color=0x5aabe8, description=f"🔔 **ALERT - **{text}")


async def send_to_alert_channel(embed):
    print("Inside send_to_alert")
    await client.get_channel(alert_channel_id).send(content="@everyone", embed=embed)
    return


async def send_to_all_channel(embed):
    print("Inside send_to_all")
    await client.get_channel(all_channel_id).send(content="@everyone", embed=embed)
    return


async def send_to_one_channel(text):
    print("Inside send to one")
    await client.get_channel(all_channel_id).send(content=f"@everyone\n{text}")
    return

@client.event
async def on_ready():
    print('Logged in as ' + client.user.name)
    print("Starting to fetch the last tweet from the " + USER_TO_SNITCH + " account")

    last_tweet = '0'

    while True:
        try:
            current_last_tweet = \
                api.user_timeline(screen_name=USER_TO_SNITCH, count=1, include_rts=False, tweet_mode='extended')[0]
            if (int(current_last_tweet.id_str) > int(last_tweet)) and (
            not current_last_tweet.full_text.startswith('RT')):
                last_tweet = current_last_tweet.id_str
                text = current_last_tweet.full_text
                if "#alert" in text or "#Alert" in text or "#ALERT" in text:
                    print("Inside if on_ready")
                    embed = alert_found(text)
                    await asyncio.gather(send_to_alert_channel(embed), send_to_all_channel(embed))
                else:
                    print("Inside else on_ready")
                    await send_to_one_channel(current_last_tweet.full_text)
            time.sleep(10)
        except IndexError:
            await client.get_channel(all_channel_id).send(embed=discord.Embed(color=0xff0a0a, description="**ERROR: User timeline empty. Kindly tweet something within 40 seconds.\nThe bot will try to wake up again in 40 seconds.**"))
            time.sleep(40)

client.run(DISCORD_BOT_TOKEN)
