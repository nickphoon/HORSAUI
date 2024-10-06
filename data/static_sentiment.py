import re
import pandas as pd
from static_utils import staticPolarity
from transformers import pipeline
from words import *

# read the original data file
reviews = pd.read_csv("dataset.csv")

# drop columns of reviews not needed
reviews = reviews.drop(
    [
        "categories",
        "postalCode",
        "province",
        "reviews.dateAdded",
        "reviews.doRecommend",
        "reviews.userProvince",
        "reviews.id",
        "reviews.title",
        "reviews.userCity",
        "reviews.username",
    ],
    axis=1,
)

# drop null reviews and duplicates
reviews = reviews.dropna()
reviews = reviews.drop_duplicates()

# initialize some empty lists
listReview, listCreatedAt, listCity, listCountry = [], [], [], []
listName, listRating, listAddress, listLat = [], [], [], []
listLon, hotelList, indexList = [], [], []
index = 0
# group hotels by name
hotelName = reviews.groupby("name")

for hotel in hotelName.groups:
    # loop through reviews and their relevant data in dataframe
    for review, date, city, country, name, rating, address, lat, long in zip(
        hotelName.get_group(hotel)["reviews.text"],
        hotelName.get_group(hotel)["reviews.date"],
        hotelName.get_group(hotel)["city"],
        hotelName.get_group(hotel)["country"],
        hotelName.get_group(hotel)["name"],
        hotelName.get_group(hotel)["reviews.rating"],
        hotelName.get_group(hotel)["address"],
        hotelName.get_group(hotel)["latitude"],
        hotelName.get_group(hotel)["longitude"],
    ):

        # split review into smaller sentences
        split_review = review.split(".")
        # adds to a list using filter function
        str_list = list(filter(None, split_review))

        # append information into list
        for row in str_list:
            if "xxx" not in row.lower():
                listReview.append(row)
                listCreatedAt.append(date)
                listCity.append(city)
                listCountry.append(country)
                listName.append(name)
                listRating.append(rating)
                listAddress.append(address)
                listLat.append(lat)
                listLon.append(long)
                hotelList.append(hotel)
                indexList.append(index)
        index += 1

# inialize the sentiment analysis model
sentiment_model = pipeline(model="nlptown/bert-base-multilingual-uncased-sentiment")
print("Running Sentiment Model...")

# run the sentiment on the reviews
sentiment = sentiment_model(listReview)

# updates the list of dictionaries, sentiment,  with sentimentPolarity and returns it to result
result = staticPolarity(
    listReview,
    sentiment,
    listCreatedAt,
    listCity,
    listCountry,
    listName,
    listRating,
    listAddress,
    listLat,
    listLon,
)

# convert list of dictionaries to a dataframe object
df = pd.DataFrame(result)
element = 0
# initializing variables
sentimentRating, finalSentimentRating, finalListReview = [], [], []

# adds the integer value of the label column into a list
for i in df["label"]:
    sentimentRating.append(int(re.search(r"\d+", i).group()))

# iterate through the list of reviews
for index, review in enumerate(listReview):
    newReview = ""
    count = 0
    # check if index of review is the same as index in indexList
    for i in indexList:
        if i == index:
            count += 1
            # combine the strings if the index of the strings are the same
            newReview += listReview[index]
    if count > 0:
        # append the combined review into a list
        finalListReview.append(newReview)
newIndexList = []


for index, rating in enumerate(sentimentRating):
    result = 0
    count = 0

    for i in indexList:
        if i == index:
            # sum up the sentimentrating by adding it to result
            result += sentimentRating[element]
            # element is used to check the last index of the item added
            element += 1
            # increment count if index in indexList is equal to index in sentimentRating list
            count += 1
    if count > 0:
        # append the count of the indexes minus 1
        newIndexList.append(element - 1)
        # append average by dividing result by count
        finalSentimentRating.append(result / count)

# create list needed for future tasks
finalListCreatedAt, finalListCity, finalListLat, finalListLon = [], [], [], []
finalListCountry, finalListName, finalListRating, finalListAddress = [], [], [], []

# append specific index of the combined reviews into final lists
for i in newIndexList:
    finalListCreatedAt.append(listCreatedAt[i])
    finalListCity.append(listCity[i])
    finalListCountry.append(listCountry[i])
    finalListName.append(listName[i])
    finalListRating.append(listRating[i])
    finalListAddress.append(listAddress[i])
    finalListLat.append(listLat[i])
    finalListLon.append(listLon[i])

# convert the final lists into a dataframe object
df = pd.DataFrame(
    list(
        zip(
            finalListReview,
            finalListCity,
            finalListCountry,
            finalListName,
            finalListRating,
            finalListAddress,
            finalListLat,
            finalListLon,
            finalListCreatedAt,
        )
    ),
    columns=[
        "review",
        "city",
        "country",
        "hotel",
        "originalRating",
        "address",
        "latitude",
        "longitude",
        "created_at",
    ],
)

# read the data file with sentiment rating added
wordsList = []
indexList = []


# adds word to wordsList if word is a keyword
for index, review in enumerate(df["review"]):
    # loop through words that are common ammenities
    for word in keyword:
        if word in review.lower():
            if word == "aircon" or word == "air-con" or word == "conditioner":
                wordsList.append("air-conditioner")
                indexList.append(index)
            elif word == "bar" or word == "lounge":
                wordsList.append("lounge")
                indexList.append(index)
            elif word == "clean":
                wordsList.append("cleanliness")
                indexList.append(index)
            elif word == "wifi" or word == "internet":
                wordsList.append("internet")
                indexList.append(index)
            elif word == "pet" or word == "pet-friendly":
                wordsList.append("pet-friendly")
                indexList.append(index)
            elif word == "bathroom" or word == "toilet":
                wordsList.append("bathroom")
                indexList.append(index)
            else:
                wordsList.append(word)
                indexList.append(index)
# create a new dataframe column "Word"
df = df.assign(Word="")

# add the words to the "Word" column based on index
for word, index in zip(wordsList, indexList):
    df.loc[:, "Word"][index] += word + " "

# create a new dataframe column "sentimentRating"
df = df.assign(sentimentRating="")

# add the sentiment rating to the "sentimentRating" column based on index
for index, rating in enumerate(finalSentimentRating):
    df.loc[:, "sentimentRating"][index] = rating

# convert dataframe and overwrite it to staticdata.csv
df.to_csv("staticdata.csv", encoding="utf-8")
