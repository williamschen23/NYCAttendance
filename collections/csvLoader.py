import csv
import requests
import pymongo

def getDictFromCSV():
    """
    Loads the csv file and returns a dictionary with the data.
    """
    results = {}

    with open('school_data.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            results[row['Local School Code']] = {
                "bedsCode": row['BEDS Code'],
                "schoolName": row['School Name'],
            }
    return results

def get_population(schoolCode, bedsCode):
    try:
        url = f"https://schoolcovidreportcard.health.ny.gov/data/public/school.300000.{bedsCode}.json"
        response = requests.get(url)
        data = response.json()


        currentCounts = data["currentCounts"]
        if "studentEnrolled" in data["currentCounts"]:
            # actual school
            population = currentCounts["studentEnrolled"]

        else:
            # remote bitches
            print("remote school " + schoolCode + " || " + bedsCode)
            population = currentCounts["onSiteStudentPopulation"] + currentCounts["offSiteStudentPopulation"]

        return population

    except Exception as e:
        print("either your internet sucks or the school doesnt exist")

def fillWilliamsUp():
    #
    connectionString = ""
    client = pymongo.MongoClient(connectionString)

    schoolsCollection = client.data.schools

    csvData = getDictFromCSV()
    i = 0
    # manuallly insert the data and run the main.py two more times for today and yesterday
    for doc in schoolsCollection.find({}):
        # if computer dies and doesnt upload everything wrap this in a
        # if "population"  not in doc:
        try:
            if i == 0:
                i = 1
                continue
            date1 = doc["2/02/2022"]
            date2 = doc["2/03/2022"]
            schoolsCollection.update_one({"CODE": doc["CODE"]}, {"$unset": {"2/02/2022": 1}})
            schoolsCollection.update_one({"CODE": doc["CODE"]}, {"$unset": {"2/03/2022": 1}})

            schoolsCollection.update_one({"CODE": doc["CODE"]}, {"$set": {"POPULATION": get_population(doc["CODE"], csvData[doc["CODE"]]["bedsCode"])}})

            schoolsCollection.update_one({"CODE": doc["CODE"]}, {"$set": {"2/02/2022": date1}})
            schoolsCollection.update_one({"CODE": doc["CODE"]}, {"$set": {"2/03/2022": date2}})
        except:
            print("error at " + doc["CODE"])


fillWilliamsUp()
