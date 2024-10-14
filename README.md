<a id="readme-top"></a>

<br />
<div align="center">
  <!-- <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a> -->

  <h3 align="center">INF1002 HORSAUI Project</h3>

  <p align="center">
    A Hotel Reviews Sentiment Analyser
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about">About</a>
    </li>
    <li><a href="#built-with">Built With</a></li>
    <li>
      <a href="#installation-and-setup">Installation</a>
    </li>
    <li>
      <a href="#usage">Usage</a>
    </li>
  </ol>
</details>

## About

This project aims to equip travellers with the right platform to augment their traditional data sources with accurate and trustable data providing travellers with more confidence when choosing their accommodation at a one-stop shop.

In this project, a simple webpage is built using Python and sentiment analysis named the Hotel Review Sentiment Analysis User interface (HORSAUI). This webpage is able to best represent publicly available online hotel reviews (Trip.com) and allow travellers to identify the best hotels at a glance.

## Built With

[![Flask](https://img.shields.io/badge/Flask-2.2.2-blue)](https://flask.palletsprojects.com/en/2.2.x/)
[![Transformers](https://img.shields.io/badge/Transformers-4.21.3-orange)](https://huggingface.co/docs/transformers/index)
[![Pandas](https://img.shields.io/badge/Pandas-1.4.4-yellow)](https://pandas.pydata.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.6.0-green)](https://matplotlib.org/)
[![Wordcloud](https://img.shields.io/badge/Wordcloud-1.8.2.2-lightgrey)](https://github.com/amueller/word_cloud)
[![NumPy](https://img.shields.io/badge/NumPy-1.23.3-red)](https://numpy.org/)
[![Requests](https://img.shields.io/badge/Requests-2.28.1-purple)](https://docs.python-requests.org/en/latest/)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.11.1-brightgreen)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
[![Bing Image URLs](https://img.shields.io/badge/bing_image_urls-0.1.4-blueviolet)](https://pypi.org/project/bing-image-urls/)
[![Torch](https://img.shields.io/badge/Torch-1.12.1-orange)](https://pytorch.org/)

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

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

### data/static_sentiment.py

Adds sentiment rating to each review </br>
Adds Ammenity Count </br>
Will take around 2 hours </br>
Outputs static_data.csv

### data/clean_data.py

Adds positive and negative word count </br>
Outputs to cleaned.csv

### scraper/trip.py

Scrapes the trip.com website for reviews on a given hotel page.

## To run the data cleaning OR to fix any errors

1. From project root folder type "cd data"
2. Delete cleaned.csv
3. Type "python clean_data.py"

<p align="right">(<a href="#readme-top">back to top</a>)</p>
