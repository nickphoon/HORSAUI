import pandas as pd

# read the original data file
df = pd.read_csv("dataset.csv")

# list of common ammenities
keyword = [
    "bar",
    "lounge",
    " business",
    "comfort",
    "food",
    "location",
    "quiet",
    "service",
    "bathroom",
    "gym",
    "parking",
    "wifi",
    "internet",
    "spa",
    "cafe",
    "room",
    "value",
    "aircon",
    "air-con",
    "conditioner",
    "sleep",
    "clean",
    "pet-friendly",
    "pet",
]

worddict = {}

# drop null reviews and duplicates
df.drop_duplicates()
df.dropna()

# check for reviews reviews.text
for review in df["reviews.text"]:
    if not isinstance(review, float):
        # check for each item in review using split()
        for item in review.split():
            # check if item is all alphabets
            if item.isalpha():
                # check if word contains words in worddict
                for word in keyword:
                    if word in item.lower():
                        if (
                            word == "aircon"
                            or word == "air-con"
                            or word == "conditioner"
                        ):
                            if "air-conditioner" not in worddict.keys():
                                worddict["air-conditioner"] = 1
                            else:
                                worddict["air-conditioner"] += 1
                        elif word == "bar" or word == "lounge":
                            if "lounge" not in worddict.keys():
                                worddict["lounge"] = 1
                            else:
                                worddict["lounge"] += 1
                        elif word == "wifi" or word == "internet":
                            if "wifi" not in worddict.keys():
                                worddict["wifi"] = 1
                            else:
                                worddict["wifi"] += 1
                        elif word == "pet" or word == "pet-friendly":
                            if "pet" not in worddict.keys():
                                worddict["pet"] = 1
                            else:
                                worddict["pet"] += 1

                        elif word == "bathroom" or word == "toilet":
                            if "toilet" not in worddict.keys():
                                worddict["toilet"] = 1
                            else:
                                worddict["toilet"] += 1
                        else:
                            if word not in worddict.keys():
                                worddict[word] = 1
                            else:
                                worddict[word] += 1
# sort dictionary by highest count
worddict = dict(sorted(worddict.items(), key=lambda item: item[1], reverse=True))
result = ""
# combine the key and pair values of worddict into result
for word, count in worddict.items():
    result += word + ": " + str(count) + " "
print("Count of amenities: ")
print(result)
