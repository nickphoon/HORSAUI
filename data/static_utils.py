def staticPolarity(
    reviews,
    sentiment,
    created_dates,
    city,
    country,
    name,
    rating,
    address,
    latitude,
    longitude,
):
    """
    updates the list of dictionaries, sentiment,  with sentimentPolarity
    reviews - list of of reviews
    sentiment - list of dictionaries of review data
    created_dates - list of created_dates
    city - list of city
    country - list of countries
    name - list of names
    rating - list of rating
    address - list of address
    latitude - list of latitude
    longitude - list of longitude
    return - returns the updated list of dictionaries
    """
    result = []
    # get the polarity of the sentiments based on label
    for (index, one) in enumerate(sentiment):
        polarity = " "
        if one["label"] == "1 star":
            polarity = "Very Negative"
        elif one["label"] == "2 stars":
            polarity = "Negative"
        elif one["label"] == "3 stars":
            polarity = "Neutral"
        elif one["label"] == "4 stars":
            polarity = "Positive"
        else:
            polarity = "Very Positive"
        # update the dictionary
        one.update(
            {
                "review": reviews[index],
                "city": city[index],
                "country": country[index],
                "hotel": name[index],
                "originalRating": rating[index],
                "address": address[index],
                "latitude": latitude[index],
                "longitude": longitude[index],
                "created_at": created_dates[index],
                "polarity": polarity,
            }
        )
        # add the dictionary to a list
        result.append(one)
    # returns a list of dictionary of review data
    return result
