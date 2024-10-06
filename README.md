# INF1002 HORSAUI Project

## Installation and setup

### Local 

1. Clone this repository.
2. Setup a python virtual environment in the root folder.
3. Install all required dependencies with `pip install -r requirements.txt`.
4. Run `python -m flask --app main run -h 0.0.0.0 -p 3000` to start server.

### Docker

1. Ensure Docker is installed in your system.
2. Run `docker build --tag inf1002 .` in the root folder. This creates the docker image.
3. Run `docker run -p 3000:3000 inf1002` to run the project in a docker container. 

## Independent functions

### data/static_sentiment.py 
Adds sentiment rating to each review </br>
Adds Ammenity Count </br>
Will take around 2 hours </br>
Outputs static_data.csv

### data/clean_data.py
Adds positive and negative word count  </br>
Outputs to cleaned.csv

### scraper/trip.py
Scrapes the trip.com website for reviews on a given hotel page.

## To run the data cleaning OR to fix any errors

1. From project root folder type "cd data"
2. Delete cleaned.csv
3. Type "python clean_data.py"
