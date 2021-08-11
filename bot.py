from discord.ext import commands, tasks
from discord.ext.commands import Bot
import json
import random
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

# intents = discord.Intents.default()
# bot = Bot(command_prefix=config["bot_prefix"], intents=intents)
#
#
# @tasks.loop(minutes=1.0)
# async def status_task():  # to set a bot's status
#     statuses = ["with you!", "with Dream of the Endless!", f"{config['bot_prefix']}help", "with humans!"]
#     await bot.change_presence(activity=discord.Game(random.choice(statuses)))
#
#
# @bot.event
# async def on_message(message):  # executed when a message is sent by someone
#     if message.author == bot.user or message.author.bot:
#         return
#     await bot.process_commands(message)
#
#
# @bot.event
# async def on_command_completion(ctx):  # command executed successfully
#     fullCommandName = ctx.command.qualified_name
#     split = fullCommandName.split(" ")
#     executedCommand = str(split[0])
#     print(
#         f"Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})")
#
#
# @bot.event
# async def on_command_error(context, error):
#     if isinstance(error, commands.CommandOnCooldown):
#         minutes, seconds = divmod(error.retry_after, 60)
#         hours, minutes = divmod(minutes, 60)
#         hours = hours % 24
#         embed = discord.Embed(
#             title="Please slow down!",
#             description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
#             color=0x8233FF
#         )
#         await context.send(embed=embed)
#     elif isinstance(error, commands.MissingPermissions):
#         embed = discord.Embed(
#             title="Error!",
#             description="You are missing the permission `" + ", ".join(
#                 error.missing_perms) + "` to execute this command!",
#             color=0xFF3387
#         )
#         await context.send(embed=embed)
#     elif isinstance(error, commands.MissingRequiredArgument):
#         embed = discord.Embed(
#             title="Error!",
#             description=str(error).capitalize(),
#             color=0xFF5733
#         )
#         await context.send(embed=embed)
#     raise error
#

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
