import json
import sys
import tweepy
import os
import discord
import asyncio
import time
from discord.ext.commands import Bot

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
charts_channel_id = config["charts_channel_id"]

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)
user = api.get_user(screen_name=USER_TO_SNITCH)

client = discord.Client()
intents = discord.Intents.default()
bot = Bot(command_prefix=config["bot_prefix"], intents=intents)


def alert_found(text):
    text = text.replace("#alert", "").strip()
    text = text.replace("#Alert", "").strip()
    text = text.replace("#ALERT", "").strip()
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


async def send_to_alert(embed):
    await client.get_channel(alert_channel_id).send(content="@everyone", embed=embed)
    return


async def send_to_all(embed):
    await client.get_channel(all_channel_id).send(content="@everyone", embed=embed)
    return


async def send_to_one(text):
    await client.get_channel(all_channel_id).send(content=f"@everyone\n{text}")
    return


@client.event
async def on_ready():
    print('Logged in as ' + client.user.name)
    print("Starting to fetch the last tweet from the " + USER_TO_SNITCH + " account")

    last_tweet = config["last_tweet_id"]

    while True:
        current_last_tweet = \
            api.user_timeline(screen_name=USER_TO_SNITCH, count=1, include_rts=False, tweet_mode='extended')[0]
        if (int(current_last_tweet.id_str) > int(last_tweet)) and (not current_last_tweet.full_text.startswith('RT')):
            config["last_tweet_id"] = current_last_tweet.id_str
            last_tweet = config["last_tweet_id"]
            with open("config.json", "w") as outfile:
                json.dump(config, outfile)
            text = current_last_tweet.full_text
            if "#chart" not in text and "#CHART" not in text and "#Chart" not in text:
                if "#alert" in text or "#Alert" in text or "#ALERT" in text:
                    embed = alert_found(text)
                    await asyncio.gather(send_to_alert(embed), send_to_all(embed))
                else:
                    await asyncio.gather(send_to_one(current_last_tweet.full_text))
            else:
                media_link = current_last_tweet.extended_entities["media"][0]["media_url_https"]
                text = current_last_tweet.full_text.split()
                text.pop()
                text = " ".join(text)
                text = text.replace("#Charts", "").strip()
                text = text.replace("#CHARTS", "").strip()
                text = text.replace("#charts", "").strip()
                text = text.replace("#chart", "").strip()
                text = text.replace("#Chart", "").strip()
                text = text.replace("#CHART", "").strip()
                if text == "":
                    text = " "
                media_embed = discord.Embed(color=0xffd500, description=f"**{text}**").set_image(url=media_link)
                await asyncio.gather(client.get_channel(charts_channel_id).send(content="@everyone", embed=media_embed))
        time.sleep(10)


client.run(DISCORD_BOT_TOKEN)
