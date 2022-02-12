from pymongo import MongoClient
from discord.ext import commands
import discord

# .env setup
from os import getenv
from dotenv import load_dotenv
load_dotenv()

client = commands.Bot(command_prefix=['.'], help_command=None)
mongo_client = MongoClient(getenv('MONGO_LINK'))
collections = mongo_client.data.schools
discordCache = mongo_client.data.discord
discordPopulationCache = mongo_client.data.discord_population


@client.event
async def on_ready():
    print("bot is ready")


@client.slash_command(name="attendance", guild_ids=['821868761329696769'])
async def attendance(ctx):
    await ctx.respond(embed=discord.Embed.from_dict(list(discordCache.find()[0].values())[-1]))


@client.slash_command(name="population", guild_ids=['821868761329696769'])
async def population(ctx):
    await ctx.respond(embed=discord.Embed.from_dict(list(discordPopulationCache.find()[0].values())[-1]))


client.run(getenv('BOT_TOKEN'))
