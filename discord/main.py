import discord
from discord.ext import commands
from pymongo import MongoClient


# .env setup
from os import getenv
from dotenv import load_dotenv

load_dotenv()

client = commands.Bot(command_prefix=['.'], help_command=None)
mongo_client = MongoClient(getenv('MONGO_LINK'))
collections = mongo_client.data.schools
discordCache = mongo_client.data.discord
discordPopulationCache = mongo_client.data.discord_population


async def find_school_place(list_dict, code):
    for i, doc in enumerate(list_dict):
        if doc['CODE'] == code:
            return i + 1
    return -1


@client.event
async def on_ready():
    print("bot is ready")


@client.slash_command(name="attendance", guild_ids=['821868761329696769'])
async def attendance(ctx):
    await ctx.respond(embed=discord.Embed.from_dict(list(discordCache.find()[0].values())[-1]))


@client.slash_command(name="population", guild_ids=['821868761329696769'])
async def population(ctx):
    await ctx.respond(embed=discord.Embed.from_dict(list(discordPopulationCache.find()[0].values())[-1]))


@client.slash_command(name='find', guild_ids=['821868761329696769'])
async def find(ctx, school_code: str):
    school = collections.find_one({'CODE': school_code})
    if not school:
        await ctx.respond(f'Your School Code of "{school_code}" isn\'t valid.'
                          f'Please make sure you are entering a valid school code.')
        return
    tuple_of_information = list(school.items())[-1]

    date = tuple_of_information[0]
    sorted_percentage = collections.find({date: {'$exists': 1}}, {'_id': 0, 'NAME': 1, 'CODE': 1, date: 1}) \
        .sort(f'{date}.PERCENTAGE', -1)
    percentage_placement = await find_school_place(sorted_percentage.clone(), school_code)
    em1 = discord.Embed(
        title=f"Search for {school_code}",
        description=""
    )
    em1.add_field(
        name=f'Percentage Data:',
        value=f'Date: {date}\n'
              f'Percentage: {tuple_of_information[1]["PERCENTAGE"]}\n'
              f'Placement: {percentage_placement} out of {len(list(sorted_percentage))}',
        inline=True,
    )
    sorted_population = collections.find({f'{date}.APPROX_TOTAL': {'$exists': 1}},
                                         {'_id': 0, 'NAME': 1, 'CODE': 1, date: 1}) \
        .sort(f'{date}.APPROX_TOTAL', -1)
    population_placement = await find_school_place(sorted_population.clone(), school_code)

    if population_placement != -1:
        em1.add_field(
            name=f'Population Data:',
            value=f'Date: {date}\n'
                  f'Approx. Total: {tuple_of_information[1]["APPROX_TOTAL"]}\n'
                  f'Placement: {population_placement} out of {len(list(sorted_population))}',
            inline=True,
        )
    await ctx.respond(embed=em1)

client.run(getenv('BOT_TOKEN'))
