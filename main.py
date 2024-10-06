import ast
import csv
import re
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from data.words import *
from data.static_utils import staticPolarity
from bing_image_urls import bing_image_urls
from flask import Flask, render_template, send_file
from scraper.trip import scrapeTripDotCom
from transformers import pipeline
from wordcloud import WordCloud, STOPWORDS


matplotlib.use("Agg")


app = Flask(__name__)


@app.route("/")
def index():
    df = pd.read_csv("data/cleaned.csv")
    list_of_hotels = df.T.to_dict().values()

    return render_template(
        "index.html",
        list_of_hotels=list_of_hotels,
    )


@app.route("/download")
def download_file():
    path = "data/cleaned.csv"
    return send_file(path, as_attachment=True)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route("/scraper/create/<hotel_id>")
def scrapeTripHotel(hotel_id):
    # retrieves a list of dictionaries to reviews
    reviews = scrapeTripDotCom(hotel_id)
    # converts reviews to a dataframe object
    df = pd.DataFrame.from_records(reviews)
    # initialize some empty lists
    listReview, listCreatedAt, listCity, listCountry, indexList = [], [], [], [], []
    listName, listRating, listAddress, listLat, listLon = [], [], [], [], []
    index = 0
    # group hotels by name
    hotelName = df.groupby("name")
    for hotel in hotelName.groups:
        # loop through reviews and their relevant data in dataframe
        for review, date, city, country, name, rating, address, lat, long in zip(
            hotelName.get_group(hotel)["review"],
            hotelName.get_group(hotel)["createdAt"],
            hotelName.get_group(hotel)["city"],
            hotelName.get_group(hotel)["country"],
            hotelName.get_group(hotel)["name"],
            hotelName.get_group(hotel)["rating"],
            hotelName.get_group(hotel)["address"],
            hotelName.get_group(hotel)["lat"],
            hotelName.get_group(hotel)["lon"],
        ):
            # split review into smaller sentences
            split_review = review.split(".")
            # if length of split_review is still more than 500 characters
            # split it even further
            for i in split_review:
                if len(i) > 500:
                    split_review.append(i[0 : len(i) // 2])
                    split_review.append(i[len(i) // 2 :])
                    split_review.remove(i)
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
        # check if word is in list of common ammenities
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
    df.to_csv("./data/scrapeddata.csv", encoding="utf-8")

    # TODO: run clean_data.py on scrappeddata.csv, merge to cleaned.csv

    # read the data file with sentiment rating added
    df = pd.read_csv("./data/scrapeddata.csv")

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

    # read the cleaned data file
    cleaned_df = pd.read_csv("./data/cleaned.csv")

    i = 0
    for stay in no_of_reviews:
        list_of_hotels.append(
            {
                "hotel_id": len(cleaned_df.index + 1),
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
    with open(
        "./data/cleanedscraped.csv", "w", newline="", encoding="utf-8"
    ) as output_file:
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
    df = pd.read_csv("./data/scrapeddata.csv")

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
            negDict = dict(
                sorted(negDict.items(), key=lambda item: item[1], reverse=True)
            )
        # removes the word in dictionary if it contains a word that is commonly used
        for word in stopwords:
            if word in wordDict:
                wordDict.pop(word)
        for word in stopwords:
            if word in negDict:
                negDict.pop(word)
        # get the first 10 positive and negative pairs by count and add to respective lists
        topTenPositive = {k: wordDict[k] for k in list(wordDict)[:10]}
        topTenNegative = {k: negDict[k] for k in list(negDict)[:10]}
        wordList.append(topTenPositive)
        negativeList.append(topTenNegative)

    # sort csv by hotel names
    clean = pd.read_csv("./data/cleanedscraped.csv")
    clean = clean.sort_values(by=["name"])
    clean.to_csv("./data/cleanedscraped.csv", encoding="utf-8")

    # read the csv file that was cleaned earlier
    clean = pd.read_csv("./data/cleanedscraped.csv")
    # create dataframe columns "word", "positiveWord", "negativeWord"
    clean = clean.assign(word="")
    clean = clean.assign(positiveWord="")
    clean = clean.assign(negativeWord="")

    clean = clean.assign(dataset="dynamic")

    # add the list of words to the "word" column based on index
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
    df3 = pd.concat([cleaned_df, clean])

    for column in df3.columns:
        if "Unnamed" in column:
            df3.drop(column, axis=1)
    df3.to_csv("./data/cleaned.csv", encoding="utf-8", index=False)

    print("Scrapping done!")
    # read the dataset
    df4 = pd.read_csv("./data/cleaned.csv")
    # display the dataframe head

    return str(df4.shape[0])


@app.route("/overview/<hotel_id>")
def overview(hotel_id):
    df = pd.read_csv("data/cleaned.csv")
    list_of_hotels = df.T.to_dict().values()
    try:
        hotel = list(list_of_hotels)[int(hotel_id)]
    except IndexError:
        return render_template("404.html")

    # for the dynamic image
    url = bing_image_urls(hotel["name"], limit=4)

    # check if able to gen out wordcloud
    noPositiveCloud = False
    noNegativeCloud = False
    # for dynamic word cloud
    positive_words = ast.literal_eval(hotel["positiveWord"])
    stopwords = set(STOPWORDS)
    if positive_words:

        wordcloud_positive = WordCloud(
            width=600,
            height=600,
            background_color="white",
            stopwords=stopwords,
            min_font_size=10,
        ).fit_words(positive_words)

        # change the value in return to set the single color need, in hsl format.
        def grey_color_func(
            word, font_size, position, orientation, random_state=None, **kwargs
        ):
            return "hsl(120,100%%, %d%%)" % np.random.randint(25, 50)

        # to change color
        wordcloud_positive.recolor(color_func=grey_color_func)
        # plot the WordCloud image
        plt.figure(figsize=(6, 6), facecolor=None)
        plt.imshow(wordcloud_positive)
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig("static/images/advantagesWordCloud.png")
        plt.clf()
    else:
        noPositiveCloud = True
    negative_words = ast.literal_eval(hotel["negativeWord"])
    if negative_words:

        wordcloud_negative = WordCloud(
            width=600,
            height=600,
            background_color="white",
            stopwords=stopwords,
            min_font_size=10,
        ).fit_words(negative_words)

        # change the value in return to set the single color need, in hsl format.
        def grey_color_func(
            word, font_size, position, orientation, random_state=None, **kwargs
        ):
            return "hsl(12,100%%, %d%%)" % np.random.randint(45, 75)

        # to change color
        wordcloud_negative.recolor(color_func=grey_color_func)

        # plot the WordCloud image
        plt.figure(figsize=(6, 6), facecolor=None)
        plt.imshow(wordcloud_negative)
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig("static/images/disadvantagesWordCloud.png")
        plt.clf()
    else:
        noNegativeCloud = True

    data = {
        "Average Sentiment Rating": [
            hotel["no_of_terrible_sentiment"],
            hotel["no_of_poor_sentiment"],
            hotel["no_of_average_sentiment"],
            hotel["no_of_very_good_sentiment"],
            hotel["no_of_excellent_sentiment"],
        ],
        "Average Based on reviews": [
            hotel["no_of_terrible"],
            hotel["no_of_poor"],
            hotel["no_of_average"],
            hotel["no_of_very_good"],
            hotel["no_of_excellent"],
        ],
    }
    # horizontal bar chart
    df = pd.DataFrame(
        data,
        columns=["Average Sentiment Rating", "Average Based on reviews"],
        index=["Terrible", "Poor", "Average", "Very good", "Excellent"],
    )

    plt.style.use("ggplot")

    df.plot.barh()

    plt.title("Overall Score")
    plt.ylabel("Product")
    plt.xlabel("Total number of ratings")
    plt.savefig("static/images/horizontalBar.png")
    plt.clf()

    # for the good, average and bad list

    def round_to_nearest_half_int(num):
        return round(num * 2) / 2

    good_list = []
    average_list = []
    bad_list = []
    # convert from string into dictionary
    good_average_bad_word_dict = ast.literal_eval(hotel["word"])
    for key, value in good_average_bad_word_dict.items():
        for i in value:
            if round_to_nearest_half_int(float(value[i])) < 2.5:
                bad_list.append(
                    {key.capitalize(): [round_to_nearest_half_int(value[i]), i]}
                )
            elif 2.5 <= round_to_nearest_half_int(float(value[i])) <= 3.5:
                average_list.append(
                    {key.capitalize(): [round_to_nearest_half_int(value[i]), i]}
                )
            else:
                good_list.append(
                    {key.capitalize(): [round_to_nearest_half_int(value[i]), i]}
                )

    return render_template(
        "overview.html",
        hotel_id=hotel_id,
        hotel=hotel,
        hotel_image=url,
        good_list=good_list,
        average_list=average_list,
        bad_list=bad_list,
        noNegativeCloud=noNegativeCloud,
        noPositiveCloud=noPositiveCloud,
        list_of_hotels=list_of_hotels,
    )


@app.route("/compare/<hotel_ids>/")
def compare(hotel_ids):
    df = pd.read_csv("data/cleaned.csv")
    list_of_hotels = df.T.to_dict().values()
    try:
        list_of_ids = hotel_ids.split("+")
        hotel_id = list_of_ids[0]
        hotel_id2 = list_of_ids[1]
        hotel = list(list_of_hotels)[int(hotel_id)]
        hotel2 = list(list_of_hotels)[int(hotel_id2)]
    except:
        return render_template("404.html")

    # for the dynamic image
    url = bing_image_urls(hotel["name"], limit=3)
    url2 = bing_image_urls(hotel2["name"], limit=3)

    # check if able to gen out wordcloud
    noPositiveCloud = False
    noNegativeCloud = False
    # for dynamic word cloud
    positive_words = ast.literal_eval(hotel["positiveWord"])
    stopwords = set(STOPWORDS)
    if positive_words:

        wordcloud_positive = WordCloud(
            width=600,
            height=600,
            background_color="white",
            stopwords=stopwords,
            min_font_size=10,
        ).fit_words(positive_words)

        # change the value in return to set the single color need, in hsl format.
        def grey_color_func(
            word, font_size, position, orientation, random_state=None, **kwargs
        ):
            return "hsl(120,100%%, %d%%)" % np.random.randint(25, 50)

        # to change color
        wordcloud_positive.recolor(color_func=grey_color_func)
        # plot the WordCloud image
        plt.figure(figsize=(6, 6), facecolor=None)
        plt.imshow(wordcloud_positive)
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig("static/images/advantagesWordCloud.png")
        plt.clf()
    else:
        noPositiveCloud = True
    negative_words = ast.literal_eval(hotel["negativeWord"])
    if negative_words:
        wordcloud_negative = WordCloud(
            width=600,
            height=600,
            background_color="white",
            stopwords=stopwords,
            min_font_size=10,
        ).fit_words(negative_words)

        # change the value in return to set the single color need, in hsl format.
        def grey_color_func(
            word, font_size, position, orientation, random_state=None, **kwargs
        ):
            return "hsl(12,100%%, %d%%)" % np.random.randint(45, 75)

        # to change color
        wordcloud_negative.recolor(color_func=grey_color_func)
        # plot the WordCloud image
        plt.figure(figsize=(6, 6), facecolor=None)
        plt.imshow(wordcloud_negative)
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig("static/images/disadvantagesWordCloud.png")
        plt.clf()
    else:
        noNegativeCloud = True

    # check if able to gen out wordcloud
    noPositiveCloud2 = False
    noNegativeCloud2 = False
    # for dynamic word cloud
    positive_words2 = ast.literal_eval(hotel2["positiveWord"])
    stopwords = set(STOPWORDS)
    if positive_words2:

        wordcloud_positive2 = WordCloud(
            width=600,
            height=600,
            background_color="white",
            stopwords=stopwords,
            min_font_size=10,
        ).fit_words(positive_words2)

        # change the value in return to set the single color need, in hsl format.
        def grey_color_func(
            word, font_size, position, orientation, random_state=None, **kwargs
        ):
            return "hsl(120,100%%, %d%%)" % np.random.randint(25, 50)

        # to change color
        wordcloud_positive2.recolor(color_func=grey_color_func)
        # plot the WordCloud image
        plt.figure(figsize=(6, 6), facecolor=None)
        plt.imshow(wordcloud_positive2)
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig("static/images/compareAdvantagesWordCloud.png")
        plt.clf()
    else:
        noPositiveCloud2 = True
    negative_words2 = ast.literal_eval(hotel2["negativeWord"])
    if negative_words2:
        wordcloud_negative2 = WordCloud(
            width=600,
            height=600,
            background_color="white",
            stopwords=stopwords,
            min_font_size=10,
        ).fit_words(negative_words2)

        # change the value in return to set the single color need, in hsl format.
        def grey_color_func(
            word, font_size, position, orientation, random_state=None, **kwargs
        ):
            return "hsl(12,100%%, %d%%)" % np.random.randint(45, 75)

        # to change color
        wordcloud_negative2.recolor(color_func=grey_color_func)
        # plot the WordCloud image
        plt.figure(figsize=(6, 6), facecolor=None)
        plt.imshow(wordcloud_negative2)
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig("static/images/compareDisadvantagesWordCloud.png")
        plt.clf()
    else:
        noNegativeCloud2 = True

    # for first hotel
    data = {
        "Average Sentiment Rating": [
            hotel["no_of_terrible_sentiment"],
            hotel["no_of_poor_sentiment"],
            hotel["no_of_average_sentiment"],
            hotel["no_of_very_good_sentiment"],
            hotel["no_of_excellent_sentiment"],
        ],
        "Average Based on reviews": [
            hotel["no_of_terrible"],
            hotel["no_of_poor"],
            hotel["no_of_average"],
            hotel["no_of_very_good"],
            hotel["no_of_excellent"],
        ],
    }
    # horizontal bar chart
    df = pd.DataFrame(
        data,
        columns=["Average Sentiment Rating", "Average Based on reviews"],
        index=["Terrible", "Poor", "Average", "Very good", "Excellent"],
    )

    plt.style.use("ggplot")

    df.plot.barh()

    plt.title("Overall Score")
    plt.ylabel("Product")
    plt.xlabel("Total number of ratings")
    plt.savefig("static/images/horizontalBar.png")
    plt.clf()

    data2 = {
        "Average Sentiment Rating": [
            hotel2["no_of_terrible_sentiment"],
            hotel2["no_of_poor_sentiment"],
            hotel2["no_of_average_sentiment"],
            hotel2["no_of_very_good_sentiment"],
            hotel2["no_of_excellent_sentiment"],
        ],
        "Average Based on reviews": [
            hotel2["no_of_terrible"],
            hotel2["no_of_poor"],
            hotel2["no_of_average"],
            hotel2["no_of_very_good"],
            hotel2["no_of_excellent"],
        ],
    }
    # horizontal bar chart
    df = pd.DataFrame(
        data2,
        columns=["Average Sentiment Rating", "Average Based on reviews"],
        index=["Terrible", "Poor", "Average", "Very good", "Excellent"],
    )

    plt.style.use("ggplot")

    df.plot.barh()

    plt.title("Overall Score")
    plt.ylabel("Product")
    plt.xlabel("Total number of ratings")
    plt.savefig("static/images/compareHorizontalBar.png")
    plt.clf()

    # for the good, average and bad list

    def round_to_nearest_half_int(num):
        return round(num * 2) / 2

    # for the first hotel
    good_list = []
    average_list = []
    bad_list = []
    # convert from string into dictionary
    good_average_bad_word_dict = ast.literal_eval(hotel["word"])
    for key, value in good_average_bad_word_dict.items():
        for i in value:
            if float(value[i]) < 2.5:
                bad_list.append(
                    {key.capitalize(): [round_to_nearest_half_int(value[i]), i]}
                )
            elif 2.5 <= float(value[i]) <= 3.5:
                average_list.append(
                    {key.capitalize(): [round_to_nearest_half_int(value[i]), i]}
                )
            else:
                good_list.append(
                    {key.capitalize(): [round_to_nearest_half_int(value[i]), i]}
                )

    # second hotel
    good_list2 = []
    average_list2 = []
    bad_list2 = []
    # convert from string into dictionary
    good_average_bad_word_dict2 = ast.literal_eval(hotel2["word"])
    for key, value in good_average_bad_word_dict2.items():
        for i in value:
            if float(value[i]) < 2.5:
                bad_list2.append(
                    {key.capitalize(): [round_to_nearest_half_int(value[i]), i]}
                )
            elif 2.5 <= float(value[i]) <= 3.5:
                average_list2.append(
                    {key.capitalize(): [round_to_nearest_half_int(value[i]), i]}
                )
            else:
                good_list2.append(
                    {key.capitalize(): [round_to_nearest_half_int(value[i]), i]}
                )

    return render_template(
        "compare.html",
        hotel_id=hotel_id,
        hotel_id2=hotel_id2,
        hotel=hotel,
        hotel2=hotel2,
        hotel_image=url,
        hotel_image2=url2,
        good_list=good_list,
        good_list2=good_list2,
        average_list=average_list,
        average_list2=average_list2,
        bad_list2=bad_list2,
        noNegativeCloud=noNegativeCloud,
        noPositiveCloud=noPositiveCloud,
        noNegativeCloud2=noNegativeCloud2,
        noPositiveCloud2=noPositiveCloud2,
    )
