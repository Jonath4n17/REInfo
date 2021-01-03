from __future__ import print_function
import os
from cv2 import cv2
import re
from google.cloud import vision
import pandas as pd
import io

def is_blacklisted(line):
  # Terms that confirm a line is not an item name
  blacklist = ["kg", "lb", "oz", "size"]
  for word in blacklist:
    if word in line:
      return True
  return  False

# Finds the last end index of currency
def find_currency(line):
  last_index = -1
  currencies = ["$", "CAD", "USD"]
  for currency in currencies:
    if line.rfind(currency) > last_index:
      last_index = line.rfind(currency)
      last_index += len(currency)
  return last_index

def ocr(img_path):
  os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "static/googleKey.json"

  # Reads file
  path = img_path

  client = vision.ImageAnnotatorClient()
  with io.open(path, 'rb') as image_file:
    content = image_file.read()

  image = vision.Image(content=content)

  client = vision.ImageAnnotatorClient()
  image = vision.Image(content=content)

  response = client.text_detection(image=image)
  df = pd.DataFrame(columns=['locale', 'description'])

  texts = response.text_annotations
  for text in texts:
      df = df.append(
          dict(
              locale=text.locale,
              description=text.description
          ),
          ignore_index=True
      )

  parse = df['description'][0]

  arr = parse.splitlines()
  names = []
  prices = []
  first_line = -1

  # Looks for prices and adds them to an array
  c = 0
  while c < len(arr):
    if is_blacklisted(arr[c]):
      continue
    index = -1

    # Checks if a price appears in the line
    regex = re.search("\d+\.\d{2}", arr[c])
    index_currency = find_currency(arr[c])
    if regex is not None:
      index = arr[c].index(regex.group(0))
    elif index_currency > -1:
      index = index_currency + 1

    if index > -1:
      temp = arr[c][index:]
      if " " in temp:
        temp = temp[0: temp.find(" ")]
      prices.append(float(temp))
      arr.pop(c)
      c -= 1
      if first_line == -1:
        first_line = arr.index(arr[c])
    c += 1


  # Finds first possible name preceding the first price
  counter = 0
  while is_blacklisted(arr[first_line - counter]) or not any(char.isalpha() for char in arr[first_line - counter]):
    counter += 1

  # Looks for possible names and adds them to an array
  for line in arr[first_line - counter:]:
      if is_blacklisted(line) or not any(c.isalpha() for c in line):
        continue
      
      names.append(line)
      # Breaks when enough names are collected
      if len(names) == len(prices):
        break

  # Adds names and prices to a dictionary
  items = {names[i]: prices[i] for i in range(len(names))}
  return(items)