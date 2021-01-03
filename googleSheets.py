import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def createSheet(content):

  spreadsheet_id = '1KW1tCrEx8atX0UhmFcyr2EvMX2gCpPjQzFcCR-6hUfQ'

  # define the scope
  scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

  # add credentials to the account
  creds = ServiceAccountCredentials.from_json_keyfile_name('static/googleKey.json', scope)

  # authorize the clientsheet 
  client = gspread.authorize(creds)

  receipt = content

  for key in receipt:
    temp = []
    temp.append(receipt[key])
    receipt[key] = temp

  # get the instance of the Spreadsheet
  sheet = client.open('ReInfo')

  # get the first sheet of the Spreadsheet
  sheet_instance = sheet.get_worksheet(0)

  # add sheet
  num = int(sheet_instance.acell('A1').value) + 1
  sheet_instance.update_cell(1, 1, num)
  sheet.add_worksheet(rows=len(receipt) + 1,cols=2,title='Receipt' + str(num))
  sheet_instance = sheet.get_worksheet(num)

  # write data
  sheet_instance.update_cell(1, 1, 'Name')
  sheet_instance.update_cell(1, 2, 'Price')
  row = 2
  for key in receipt:
      sheet_instance.update_cell(row, 1, key)
      sheet_instance.update_cell(row, 2, receipt[key][0])
      row += 1
