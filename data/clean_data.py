import csv
import numpy as np
import pandas as pd
from words import *
# read the data file with sentiment rating added
df = pd.read_csv("staticdata.csv")

# list of valid characters and to remove any inputs with weird characters
df.hotel.replace({r"[^\x00-\x7F]+": ""}, regex=True, inplace=True)

# initialise a list
list_of_hotels = []

# get the total ratings for original review data
df.loc[df["originalRating"] > 5, "originalRating"] = df["originalRating"] / 2
product = df.groupby("hotel")["originalRating"].sum().to_dict()

# get the total ratings for sentimentRating review data
sentiment_rating_total = df.groupby("hotel")["sentimentRating"].sum().to_dict()

# create a list of our conditions for review stars
conditions = [
    (df["originalRating"] < 1),
    (df["originalRating"] >= 1) & (df["originalRating"] < 2),
    (df["originalRating"] >= 2) & (df["originalRating"] < 3),
    (df["originalRating"] >= 3) & (df["originalRating"] < 4),
    (df["originalRating"] >= 4),
]
# create a list of the values we want to assign for each condition for review stars
values = ["Terrible", "Poor", "Average", "Very good", "Excellent"]

# assigns a rating to the review based on the review stars
df["overall_english"] = np.select(conditions, values)

# finds out each unique hotel has how many of each rating for review stars

total_overall_english = (
    df.assign(
        no_of_terrible=np.where(df["overall_english"] == "Terrible", +1, +0),
        no_of_poor=np.where(df["overall_english"] == "Poor", +1, +0),
        no_of_average=np.where(df["overall_english"] == "Average", +1, +0),
        no_of_very_good=np.where(df["overall_english"] == "Very good", +1, +0),
        no_of_excellent=np.where(df["overall_english"] == "Excellent", +1, +0),
    )
    .groupby("hotel")
    .agg(
        {
            "no_of_terrible": sum,
            "no_of_poor": sum,
            "no_of_average": sum,
            "no_of_very_good": sum,
            "no_of_excellent": sum,
        }
    )
    .to_dict()
)

# create a list of our conditions for sentiment rating
conditions_sentimentRating = [
    (df["sentimentRating"] < 1),
    (df["sentimentRating"] >= 1) & (df["sentimentRating"] < 2),
    (df["sentimentRating"] >= 2) & (df["sentimentRating"] < 3),
    (df["sentimentRating"] >= 3) & (df["sentimentRating"] < 4),
    (df["sentimentRating"] >= 4),
]
# create a list of the values we want to assign for each condition for review stars
values_sentimentRating = ["Terrible", "Poor", "Average", "Very good", "Excellent"]

# assigns a rating to the review based on the review stars
df["overall_english_sentimentRating"] = np.select(
    conditions_sentimentRating, values_sentimentRating
)

# finds out each unique hotel has how many of each rating for review stars

total_overall_english_sentimentRating = (
    df.assign(
        no_of_terrible_sentiment=np.where(
            df["overall_english_sentimentRating"] == "Terrible", +1, +0
        ),
        no_of_poor_sentiment=np.where(
            df["overall_english_sentimentRating"] == "Poor", +1, +0
        ),
        no_of_average_sentiment=np.where(
            df["overall_english_sentimentRating"] == "Average", +1, +0
        ),
        no_of_very_good_sentiment=np.where(
            df["overall_english_sentimentRating"] == "Very good", +1, +0
        ),
        no_of_excellent_sentiment=np.where(
            df["overall_english_sentimentRating"] == "Excellent", +1, +0
        ),
    )
    .groupby("hotel")
    .agg(
        {
            "no_of_terrible_sentiment": sum,
            "no_of_poor_sentiment": sum,
            "no_of_average_sentiment": sum,
            "no_of_very_good_sentiment": sum,
            "no_of_excellent_sentiment": sum,
        }
    )
    .to_dict()
)

# get the total number of reviews and unique hotel names
no_of_reviews = df["hotel"].value_counts().to_dict()

# get the address, lat and long for each hotel
address = df[
    [
        "hotel",
        "address",
        "latitude",
        "longitude",
    ]
].drop_duplicates(subset=["hotel"])
# makes the name the key for a dictionary and the rest of values into list
formmated_dict = address.set_index("hotel").T.to_dict("list")

i = 0
for stay in no_of_reviews:
    list_of_hotels.append(
        {
            "hotel_id": i,
            "name": stay,
            "average_rating": "%0.2f" % (product[stay] / no_of_reviews[stay]),
            "no_of_reviews": no_of_reviews[stay],
            "address": formmated_dict[stay][0],
            "latitude": formmated_dict[stay][1],
            "longitude": formmated_dict[stay][2],
            "no_of_terrible": total_overall_english["no_of_terrible"][stay],
            "no_of_poor": total_overall_english["no_of_poor"][stay],
            "no_of_average": total_overall_english["no_of_average"][stay],
            "no_of_very_good": total_overall_english["no_of_very_good"][stay],
            "no_of_excellent": total_overall_english["no_of_excellent"][stay],
            "no_of_terrible_sentiment": total_overall_english_sentimentRating[
                "no_of_terrible_sentiment"
            ][stay],
            "no_of_poor_sentiment": total_overall_english_sentimentRating[
                "no_of_poor_sentiment"
            ][stay],
            "no_of_average_sentiment": total_overall_english_sentimentRating[
                "no_of_average_sentiment"
            ][stay],
            "no_of_very_good_sentiment": total_overall_english_sentimentRating[
                "no_of_very_good_sentiment"
            ][stay],
            "no_of_excellent_sentiment": total_overall_english_sentimentRating[
                "no_of_excellent_sentiment"
            ][stay],
            "sentiment_rating": "%0.2f"
            % (sentiment_rating_total[stay] / no_of_reviews[stay]),
        }
    )
    i = i + 1


# get the columns
keys = list_of_hotels[0].keys()
# write to csv
with open("cleaned.csv", "w", newline="", encoding="utf-8") as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(list_of_hotels)

hotelList = []
# group hotels by hotel name
hotelName = df.groupby("hotel")

# get a specific hotel i
for name in hotelName.groups:
    wordDict = {}
    wordList = []
    newdict = {}
    # get the word , hotel name and sentiment rating
    for word, hotel, rating in zip(
        hotelName.get_group(name)["Word"],
        hotelName.get_group(name)["hotel"],
        hotelName.get_group(name)["sentimentRating"],
    ):
        # check if string is not nan
        if str(word) != "nan":
            # checks if there is space in word
            if " " in word.strip():
                # splits the word by space
                mutlipleword = word.split()
                # append word into a list
                for word in mutlipleword:
                    wordList.append(word)
                    # adds key pair values to a dict
                    if word not in wordDict.keys():
                        wordDict[word] = int(rating)
                    else:
                        wordDict[word] += int(rating)
            else:
                # append word into a list
                wordList.append(word)
                # adds key pair values to a dict
                if word.strip() not in wordDict.keys():
                    wordDict[word.strip()] = int(rating)
                else:
                    wordDict[word.strip()] += int(rating)
    # iterate through wordDict
    for item in wordDict:
        # initialize a new variable key with contents of item
        key = item
        # create a nested dictionary
        newdict[key] = {}
        count = 0
        # adds count if word in wordList is the same as item in wordDict
        for word in wordList:
            if word.strip() == item.strip():
                count += 1
        number = wordDict[item]
        # gets the average sentiment rating divide it by count
        newdict[key][count] = int(number) / count
    # add to the hotelList the nested dictionary
    hotelList.append(newdict)

# read the data file with sentiment rating added
df = pd.read_csv("staticdata.csv")

# group dataframe by hotel name
hotelName = df.groupby("hotel")
wordList = []
negativeList = []
# list of words to filter out

# get a specific hotel name
for name in hotelName.groups:
    wordDict = {}
    negDict = {}
    # get the review, hotel name and sentiment rating
    for review, hotel, rating in zip(
        hotelName.get_group(name)["review"],
        hotelName.get_group(name)["hotel"],
        hotelName.get_group(name)["sentimentRating"],
    ):
        # check if rating is positive and very positive
        if int(rating) >= 4:
            # adds word into dict if word contains only letters
            for word in review.split():
                if word not in wordDict.keys() and word.isalpha():
                    wordDict[word.lower()] = 1
                # adds count if word exists as a dictionary key
                elif word.isalpha():
                    wordDict[word.lower()] += 1
        # check if rating is negative and very negative
        elif int(rating) <= 2:
            # adds word into dict if word contains only letters
            for word in review.split():
                if word not in negDict.keys() and word.isalpha():
                    negDict[word.lower()] = 1
                # adds count if word exists as a dictionary key
                elif word.isalpha():
                    negDict[word.lower()] += 1
        else:
            continue
        # sort dictionary based on count, highest to smallest
        wordDict = dict(
            sorted(wordDict.items(), key=lambda item: item[1], reverse=True)
        )
        negDict = dict(sorted(negDict.items(), key=lambda item: item[1], reverse=True))
    # removes the word in dictionary if it contains a word that is commonly used
    for word in stopwords:
        if word in wordDict:
            # removes word from WordDict if word in stopwords
            wordDict.pop(word)
    for word in stopwords:
        if word in negDict:
            # removes word from negDict if word in stopwords
            negDict.pop(word)
    # converts wordDict to lists
    positiveDictList = list(wordDict)
    positiveCopy = list(wordDict)
    negativeDictList = list(negDict)
    negativeCopy = list(negDict)
   
    for word in positiveCopy:
         # checks the first word in the list with the rest
        for other in positiveDictList[1:]:
            if positiveDictList[0] in other:
                # if the word is in another word in list, pop it from wordDict
                wordDict[positiveDictList[0]] += wordDict[other]
                wordDict.pop(other)
                positiveDictList.remove(other)
        # insert the last item in list as the first item and pops the last item from the list
        positiveDictList.insert(0, positiveDictList.pop())

    for word in negativeCopy:
        # checks the first word in the list with the rest
        for other in negativeDictList[1:]:
            if negativeDictList[0] in other:
                # if the word is in another word in list, pop it from negDict
                negDict[negativeDictList[0]] += negDict[other]
                negDict.pop(other)
                negativeDictList.remove(other)
        # insert the last item in list as the first item and pops the last item from the list
        negativeDictList.insert(0, negativeDictList.pop())
    # get the first 10 positive and negative pairs by count and add to respective lists
    topTenPositive = {k: wordDict[k] for k in list(wordDict)[:10]}
    topTenNegative = {k: negDict[k] for k in list(negDict)[:10]}
    wordList.append(topTenPositive)
    negativeList.append(topTenNegative)

# sort csv by hotel names
clean = pd.read_csv("cleaned.csv")
clean = clean.sort_values(by=["name"])
clean.to_csv("cleaned.csv", encoding="utf-8")

# read the csv file that was cleaned earlier
clean = pd.read_csv("cleaned.csv")
# create dataframe columns "word", "positiveWord", "negativeWord"
clean = clean.assign(word="")
clean = clean.assign(positiveWord="")
clean = clean.assign(negativeWord="")

clean = clean.assign(dataset="static")

# add hte list of words to the "word" column based on index
for index, item in enumerate(hotelList):
    clean.loc[:, "word"][index] = item

# add the list of positiveWords to the "positiveWord" column based on index
for index, item in enumerate(wordList):
    clean.loc[:, "positiveWord"][index] = item

# add the list of negativeWords to the "negativeWord" column based on index
for index, item in enumerate(negativeList):
    clean.loc[:, "negativeWord"][index] = item

# sort dataframe by id
clean = clean.sort_values("hotel_id")
# convert dataframe and overwrite it to staticdata.csv
clean.to_csv("cleaned.csv", encoding="utf-8")

# to show that the function has finished running
print("The static data has been cleaned and written to cleaned.csv!")
