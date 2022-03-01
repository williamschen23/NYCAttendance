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


# generates school data from a list of all the data values from the nyc attendance website
def request_data(data_list):
    requests = []
    for school_code, school_name, date, percentage in zip(*[iter(data_list)] * 4):
        if percentage == 'NS':
            percentage = 0
        percentage = float(percentage)
        if doc := collections.find_one({'CODE': school_code}):
            if 'POPULATION' in doc:
                requests.append(UpdateOne({'CODE': school_code}, {'$set': {date: {
                    "PERCENTAGE": percentage,
                    "APPROX_TOTAL": floor(percentage / 100 * doc['POPULATION'])
                }}}))
            else:
                requests.append(UpdateOne({'CODE': school_code}, {'$set': {date: {
                    "PERCENTAGE": percentage,
                }}}))
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
    collections.bulk_write(requests)


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
                name=f'{counter}) {doc["NAME"]} ({doc["CODE"]})',
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
