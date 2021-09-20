import json
import sys
import tweepy
import os
import discord
import asyncio
import psycopg2
from discord.ext import tasks

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


@tasks.loop(seconds=10)
async def fetch():
    last_tweet = (await asyncio.gather(get_last_tweet_id()))[0]
    current_last_tweet = \
        api.user_timeline(screen_name=USER_TO_SNITCH, count=1, include_rts=False, tweet_mode='extended')[0]
    if (int(current_last_tweet.id_str) > int(last_tweet)) and (
            not current_last_tweet.full_text.startswith('RT')):
        text = current_last_tweet.full_text
        if "#chart" not in text and "#CHART" not in text and "#Chart" not in text:
            if "#alert" in text or "#Alert" in text or "#ALERT" in text:
                embed = alert_found(text)
                await asyncio.gather(send_to_alert(embed, int(current_last_tweet.id_str)),
                                     send_to_all(embed, int(current_last_tweet.id_str)))
            else:
                await asyncio.gather(send_to_one(current_last_tweet.full_text, int(current_last_tweet.id_str)))
        else:
            await asyncio.gather(chart_found(current_last_tweet))
        await asyncio.gather(set_last_tweet_id(current_last_tweet.id_str))


@client.event
async def on_ready():
    if not fetch.is_running():
        fetch.start()
    print('Logged in as ' + client.user.name)
    print("Starting to fetch the last tweet from the " + USER_TO_SNITCH + " account")


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


async def send_to_alert(embed, tweet_id):
    await client.get_channel(alert_channel_id).send(content="@everyone", embed=embed)
    print(f"Sent tweet {tweet_id} to alert channel")
    return


async def send_to_all(embed, tweet_id):
    await client.get_channel(all_channel_id).send(content="@everyone", embed=embed)
    print(f"Sent tweet {tweet_id} to all channel")
    return


async def send_to_one(text, tweet_id):
    await client.get_channel(all_channel_id).send(content=f"@everyone\n{text}")
    print(f"Sent tweet {tweet_id} to all channel")
    return


async def get_last_tweet_id():
    db = psycopg2.connect(database="d9d007debv37l9", user="mnfhmnmwqklmna",
                          password="807464a720386343baf66c7fb867987a2b79b587f0bd141209e762ea9171ede2",
                          host="ec2-44-194-112-166.compute-1.amazonaws.com", port=5432)
    cur = db.cursor()
    cur.execute("SELECT * FROM public.last_tweet;")
    return cur.fetchone()[0]


async def set_last_tweet_id(tweet_id):
    db = psycopg2.connect(database="d9d007debv37l9", user="mnfhmnmwqklmna",
                          password="807464a720386343baf66c7fb867987a2b79b587f0bd141209e762ea9171ede2",
                          host="ec2-44-194-112-166.compute-1.amazonaws.com", port=5432)
    cur = db.cursor()
    cur.execute(f"UPDATE public.last_tweet SET tweet_id={tweet_id.strip()};")
    db.commit()
    cur.close()
    db.close()


async def chart_found(current_last_tweet):
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
    await client.get_channel(charts_channel_id).send(content="@everyone", embed=media_embed)
    return


client.run(DISCORD_BOT_TOKEN)
