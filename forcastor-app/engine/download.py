import requests
from bs4 import BeautifulSoup as bs
import sys
import pandas as pd

filePath = sys.argv[1]


def download_file(file):
    filepath = file+"/customer_predictions.xlsx"

    tables = pd.read_html('gui/datatable1.html')
    df = tables[0]
    df.to_excel(filepath, index=False)
    output = "Download Completed!"

    return output

print(download_file(filePath))
sys.stdout.flush()
