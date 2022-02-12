from pymongo import MongoClient
from math import floor
import discord
from pymongo import UpdateOne

# .env setup
from dotenv import load_dotenv
from os import getenv
load_dotenv()

client = MongoClient(getenv('MONGO_LINK'))
collections = client.data.schools
discordCache = client.data.discord
discordPopulationCache = client.data.discord_population


# generates school data for all schools in nested_data
def generate_data(nested_data):
    date = nested_data[0][2]
    for data in nested_data:
        school_code = data[0]
        school_name = data[1]
        percentage = data[3]
        if percentage == 'NS':
            percentage = 0.0
        percentage = float(percentage)
        if doc := collections.find_one({'CODE': school_code}):
            if 'POPULATION' in doc:
                collections.update_one({'CODE': school_code}, {'$set': {date: {
                    "PERCENTAGE": percentage,
                    "APPROX_TOTAL": floor(percentage/100 * doc['POPULATION'])
                }}})
            else:
                collections.update_one({'CODE': school_code}, {'$set': {date: {
                    "PERCENTAGE": percentage,
                }}})
        else:
            insertion = {
                "NAME": school_name,
                "CODE": school_code,
                date: {
                    "APPROX_TOTAL": percentage,
                },
            }
            print("added " + school_name + " code: " + school_code)
            collections.insert_one(insertion)


# adds every data from today into a cache to use for discord
def generate_discord_data(date):
    if not discordCache.find_one({date: {'$exists': 1}}):
        em1 = discord.Embed(
            title="Attendance Percentage",
            description="Best 5 Schools for Attendance on " + date,
        )
        counter = 1
        for doc in collections.find({date: {'$exists': 1}}, {'_id': 0, 'NAME': 1, 'CODE': 1, date: 1})\
                .sort(f'{date}.PERCENTAGE', -1)\
                .limit(5):
            em1.add_field(
                name=f'{counter}) {doc["NAME"]} ({doc["CODE"]})',
                value=f'{doc[date]["PERCENTAGE"]}%',
                inline=False,
            )
            counter += 1
        discordCache.update_one(discordCache.find()[0], {'$set': {date: em1.to_dict()}})
    else:
        print("already generated discord data for percentage for today")


def generate_discord_population_data(date):
    if not discordPopulationCache.find_one({date: {'$exists': 1}}):
        em1 = discord.Embed(
            title="Attendance",
            description="Best 5 Schools for Attendance on " + date,
        )
        counter = 1
        for doc in collections.find({f'{date}.APPROX_TOTAL': {'$exists': 1}},
                                    {'_id': 0, 'NAME': 1, 'CODE': 1, date : 1})\
                .sort(f'{date}.APPROX_TOTAL', -1)\
                .limit(5):
            em1.add_field(
                name=f'{counter}) {doc["NAME"]} ({doc["CODE"]}%)',
                value=f'{doc[date]["APPROX_TOTAL"]} ({doc[date]["PERCENTAGE"]}%)',
                inline=False,
            )
            counter += 1
        discordPopulationCache.update_one(discordPopulationCache.find()[0], {'$set': {date: em1.to_dict()}})
    else:
        print("already generated discord data for population for today")


# helper functions
def delete_all_data(dates):
    for date in dates:
        collections.update_many({}, {'$unset': {date: 1}})


def fix_population():
    for doc in collections.find():
        if 'POPULATION' in doc:
            if not doc['POPULATION']:
                collections.update_one({'NAME': doc['NAME']}, {'$unset': {'POPULATION': ""}})
            if type(doc['POPULATION']) == str:
                collections.update_one({'NAME': doc['NAME']}, {'$set': {'POPULATION': int(doc['POPULATION'])}})
