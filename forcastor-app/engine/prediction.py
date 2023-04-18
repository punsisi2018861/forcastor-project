import requests
from bs4 import BeautifulSoup as bs
import sys
import pandas as pd

filePath = sys.argv[1]


def get_weather(place):
    weather = place
    df = pd.read_excel(weather)
    df1= df.head(2)
    # output = df1.to_json()
    htmlFile = df.to_html()

    text_file = open("gui/datatable.html", "w")
    text_file.write(htmlFile)
    text_file.close()
    output = "Prediction Completed!"

    return output

print(get_weather(filePath))
sys.stdout.flush()
