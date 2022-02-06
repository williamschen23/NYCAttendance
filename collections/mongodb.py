from pymongo import MongoClient
from math import floor

# .env setup
from dotenv import load_dotenv
from os import getenv
load_dotenv()

client = MongoClient(getenv('mongo_link'))
collections = client.data.schools


# generates data for both new and old indexes in mongoDB collections
def generate_data(nested_data):
    date = nested_data[0][2]
    for data in nested_data:
        school_code = data[0]
        school_name = data[1]
        percentage = data[3]
        if percentage == 'NS':
            percentage = 0.0
        percentage = float(percentage)
        doc = collections.find_one({'CODE': school_code})
        if doc:
            if 'POPULATION' in doc and doc['POPULATION']:
                collections.update_one({'NAME': school_name}, {'$set': {date: {
                    "PERCENTAGE": percentage,
                    "APPROX_TOTAL": floor(percentage/100 * doc['POPULATION'])
                }}})
            else:
                collections.update_one({'NAME': school_name}, {'$set': {date: {
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


