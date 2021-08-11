import json
import sys
import tweepy
import os
import discord
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
discord.AllowedMentions(everyone=True)


@client.event
async def on_ready():
    print('Logged in as ' + client.user.name)
    print("Starting to fetch the last tweet from the " + USER_TO_SNITCH + " account")

    last_tweet = '0'

    while True:
        current_last_tweet = api.user_timeline(screen_name=USER_TO_SNITCH, count=1, include_rts=False, tweet_mode='extended')[0]
        if (int(current_last_tweet.id_str) > int(last_tweet)) and (not current_last_tweet.full_text.startswith('RT')):
            last_tweet = current_last_tweet.id_str
            embed = discord.Embed(color=0x5aabe8, description=f"🔔 **ALERT **{current_last_tweet.full_text.replace('#alert', '').strip()}")

            if "#alert" in current_last_tweet.full_text or "#ALERT" in current_last_tweet.full_text or "#Alert" in current_last_tweet.full_text:
                if "#alert" in current_last_tweet.full_text:
                    current_last_tweet.full_text = current_last_tweet.full_text.replace("#alert", "").strip()
                    embed = discord.Embed(color=0x5aabe8, description=f"🔔 **ALERT **{current_last_tweet.full_text}")
                elif "#Alert" in current_last_tweet.full_text:
                    current_last_tweet.full_text = current_last_tweet.full_text.replace("#Alert", "").strip()
                    embed = discord.Embed(color=0x5aabe8, description=f"🔔 **ALERT **{current_last_tweet.full_text}")
                else:
                    current_last_tweet.full_text = current_last_tweet.full_text.replace("#ALERT", "").strip()
                    embed = discord.Embed(color=0x5aabe8, description=f"🔔 **ALERT **{current_last_tweet.full_text}")

                if "SOLD" in current_last_tweet.full_text or "sold" in current_last_tweet.full_text or "Sold" in current_last_tweet.full_text:
                    if "sold" in current_last_tweet.full_text:
                        current_last_tweet.full_text = current_last_tweet.full_text.replace("sold", "").strip()
                    elif "Sold" in current_last_tweet.full_text:
                        current_last_tweet.full_text = current_last_tweet.full_text.replace("Sold", "").strip()
                    else:
                        current_last_tweet.full_text = current_last_tweet.full_text.replace("SOLD", "").strip()

                    embed = discord.Embed(color=0xff0a0a, description=f"🔔 **ALERT - SOLD - **{current_last_tweet.full_text}")

                elif "BOUGHT" in current_last_tweet.full_text or "bought" in current_last_tweet.full_text or "Bought" in current_last_tweet.full_text:
                    if "bought" in current_last_tweet.full_text:
                        current_last_tweet.full_text = current_last_tweet.full_text.replace("bought", "").strip()
                    elif "Bought" in current_last_tweet.full_text:
                        current_last_tweet.full_text = current_last_tweet.full_text.replace("Bought", "").strip()
                    else:
                        current_last_tweet.full_text = current_last_tweet.full_text.replace("BOUGHT", "").strip()
                    embed = discord.Embed(color=0x1dfc00, description=f"🔔 **ALERT - BOUGHT - **{current_last_tweet.full_text}")

                await client.get_channel(alert_channel_id).send(content="@everyone", embed=embed)
                await client.get_channel(all_channel_id).send(content="@everyone", embed=embed)
            else:
                embed = discord.Embed(color=0x5aabe8,description=current_last_tweet.full_text)
                await client.get_channel(all_channel_id).send(content=f"@everyone", embed=embed)

        time.sleep(10)


client.run(DISCORD_BOT_TOKEN)

# This URL can be used to add the bot to your server. Copy and paste the URL into your browser,
# choose a server to invite the bot to, and click “Authorize”. You need manage server permissions to do so.
# https://discord.com/api/oauth2/authorize?client_id=874182679602561095&permissions=8&scope=bot
