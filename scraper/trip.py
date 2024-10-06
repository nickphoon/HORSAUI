import ast
import json
import requests
import time
from bs4 import BeautifulSoup


def scrapeTripDotCom(hotel_id):
    hotel_url = "https://sg.trip.com/hotels/detail/?hotelId=" + hotel_id

    # Url of the API used by trip.com to retrieve reviews for speicfied hotel.
    review_url = "https://sg.trip.com/restapi/soa2/24077/clientHotelCommentList"

    page = requests.get(hotel_url)

    soup = BeautifulSoup(page.content, "html.parser")
    data = [
        json.loads(x.string)
        for x in soup.find_all("script", type="application/ld+json")
    ]

    hotel_name = data[0]["name"]
    print(f"The current hotel name is {hotel_name}")

    hotel_dict = ast.literal_eval(data[0]["address"])
    hotel_address = hotel_dict["streetAddress"]
    hotel_city = hotel_dict["addressRegion"]
    hotel_country = hotel_dict["addressCountry"]
    no_of_reviews = int(data[0]["aggregateRating"]["reviewCount"])
    print(f"The current number of reviews for this hotel is {no_of_reviews}")
    reviewList = []
    number_of_times_to_loop_40 = no_of_reviews // 40
    print(f"The number of times to loop 0 is {number_of_times_to_loop_40}")
    last_loop_num_review = no_of_reviews % 40
    print(f"The last loop number is {last_loop_num_review}")
    # first situation when reviews is 0
    if last_loop_num_review == 0 and number_of_times_to_loop_40 == 0:
        print("In the first if statement")
        return reviewList
    # second situation when reviews is multiples of 40
    elif last_loop_num_review == 0 and number_of_times_to_loop_40 > 0:
        print("In the second if statement")
        for i in range(number_of_times_to_loop_40):
            body = {
                "hotelId": hotel_id,
                "pageIndex": i + 1,
                "pageSize": "40",
                "orderBy": "0",
                "UnusefulReviewPageIndex": "1",
                "repeatComment": "1",
                "pageID": "10320668147",
                "head": {
                    "userRegion": "SG",
                    "Locale": "en-SG",
                    "LocaleController": "en-SG",
                    "TimeZone": "8",
                    "HotelExtension": {
                        "group": "TRIP",
                        "hasAidInUrl": "false",
                        "Qid": "259776002879",
                        "WebpSupport": "true",
                        "PID": "aea7cbb8-9507-4f25-8f3d-fbcfb08c56a2",
                    },
                },
                "PageNo": i + 1,
            }
            response = requests.post(review_url, json=body)
            try:
                reviews = response.json()["groupList"][0]["commentList"]
                print(f"The current number of reviews fetched is {len(reviews)}")
                # Loops through object to retrieve important information we will be using in machine learning process.
                for review in reviews:
                    obj = {
                        "review": review["content"],
                        "createdAt": review["createDate"],
                        "city": hotel_city,
                        "country": hotel_country,
                        "name": hotel_name,
                        "rating": review["rating"],
                        "address": hotel_address,
                        "lat": "0",
                        "lon": "0",
                    }
                    reviewList.append(obj)
            except IndexError:
                break

            time.sleep(3)

    # third condition when reviews more than 40 but has less than 40
    else:
        print("in 3rd")
        for i in range(number_of_times_to_loop_40 + 1):
            print(f"The number of times of the loop is {i}")
            if i != number_of_times_to_loop_40:
                body = {
                    "hotelId": hotel_id,
                    "pageIndex": i + 1,
                    "pageSize": "40",
                    "orderBy": "0",
                    "UnusefulReviewPageIndex": "1",
                    "repeatComment": "1",
                    "pageID": "10320668147",
                    "head": {
                        "userRegion": "SG",
                        "Locale": "en-SG",
                        "LocaleController": "en-SG",
                        "TimeZone": "8",
                        "HotelExtension": {
                            "group": "TRIP",
                            "hasAidInUrl": "false",
                            "Qid": "259776002879",
                            "WebpSupport": "true",
                            "PID": "aea7cbb8-9507-4f25-8f3d-fbcfb08c56a2",
                        },
                    },
                    "PageNo": i + 1,
                }
                response = requests.post(review_url, json=body)
                try:
                    reviews = response.json()["groupList"][0]["commentList"]
                    print(f"The current number of reviews fetched is {len(reviews)}")
                    for review in reviews:
                        obj = {
                            "review": review["content"],
                            "createdAt": review["createDate"],
                            "city": hotel_city,
                            "country": hotel_country,
                            "name": hotel_name,
                            "rating": review["rating"],
                            "address": hotel_address,
                            "lat": "0",
                            "lon": "0",
                        }
                        reviewList.append(obj)
                    print(f"The current number of total reviews is {len(reviewList)}")
                    if len(reviews) != 40:
                        print("The API does not fetch enough reviews.")
                        return reviewList
                except IndexError:
                    print("Error")
                    break
                # Loops through object to retrieve important information we will be using in machine learning process.

                time.sleep(3)
            else:
                print("This is the last loop")
                body = {
                    "hotelId": hotel_id,
                    "pageIndex": i + 1,
                    "pageSize": last_loop_num_review,
                    "orderBy": "0",
                    "UnusefulReviewPageIndex": "1",
                    "repeatComment": "1",
                    "pageID": "10320668147",
                    "head": {
                        "userRegion": "SG",
                        "Locale": "en-SG",
                        "LocaleController": "en-SG",
                        "TimeZone": "8",
                        "HotelExtension": {
                            "group": "TRIP",
                            "hasAidInUrl": "false",
                            "Qid": "259776002879",
                            "WebpSupport": "true",
                            "PID": "aea7cbb8-9507-4f25-8f3d-fbcfb08c56a2",
                        },
                    },
                    "PageNo": i + 1,
                }
                response = requests.post(review_url, json=body)
                try:
                    reviews = response.json()["groupList"][0]["commentList"]
                    print(f"The current number of reviews fetched is {len(reviews)}")
                    for review in reviews:
                        obj = {
                            "review": review["content"],
                            "createdAt": review["createDate"],
                            "city": hotel_city,
                            "country": hotel_country,
                            "name": hotel_name,
                            "rating": review["rating"],
                            "address": hotel_address,
                            "lat": "0",
                            "lon": "0",
                        }
                        reviewList.append(obj)
                except IndexError:
                    print("Error")
                # Loops through object to retrieve important information we will be using in machine learning process.
    return reviewList
