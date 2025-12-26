import datetime
import google.generativeai as genai
import time
import os
from pathlib import Path
from PyPDF2 import PdfReader
import re
import csv
import io
from PIL import Image
import pytesseract
#-----------------------------------------------------------#
#Issues takes a while
#API key
genai.configure(api_key='')
model = genai.GenerativeModel("gemini-3-flash-preview") #model
fulltxt = ""
suffixes = ["png","img","pdf","jpg"]
prompt = ( "extract the requested information: Amount,Date Bought, and Item/purpose of bill. Each each bill's info should be on its own line. the line that has 'END OF BILL' is the end of that bill, the next line is the start of a new bill. Output format example: 49.8-2007/12/01_Brusco Brothers -DO NOT OUTPUT METADATA -IF BILL REPEATS, STILL INCLUDE IT"
)

billinfo = []
def writeinfile(item,amount,date): #make it a csv
    dateofscan = datetime.datetime.now()
    file = Path(f"{dateofscan.strftime('%b_%Y')} bills.csv")
    if file.exists() == False: #checks if there is already a file that is named like this
        with open(f"{dateofscan.strftime('%b_%Y')} bills.csv",mode="a") as csvfile:
            print("exsists")
            fielnames = ['item',"amount","date"]
            writer= csv.DictWriter(csvfile,fieldnames=fielnames)
            writer.writeheader()
            writer.writerow({"item":f"{item}","amount":f"{amount}","date":f"{date}"})
    else:
        with open(f"{dateofscan.strftime('%b_%Y')} bills.csv",mode="a") as csvfile:
            fielnames = ['item',"amount","date"]
            writer= csv.DictWriter(csvfile,fieldnames=fielnames)
            writer.writerow({"item":f"{item}","amount":f"{amount}€","date":f"{date}"})

def iterfiles():
    global fulltxt
    folder = Path("billholder")
    fulltxt = ""
    for filename in folder.iterdir():
        strfilename = str(filename)
        suf =  strfilename[len(strfilename) - 3:len(strfilename)] #suffix
        if suf in suffixes:
            if suf == "pdf": #before  strfilename[len(strfilename) - 3:len(strfilename)] != "pdf"
                reader = PdfReader(filename)
                lenofdoc = len(reader.pages)
                for i in range(0,lenofdoc):
                    page = reader.pages[i]
                    text = page.extract_text()
                    fulltxt = fulltxt + f"\n{text}"
                    fulltxt = fulltxt + "\n END"
            if suf == "png" or suf == "img" or suf == "jpg":
                text = pytesseract.image_to_string(Image.open(filename))
                fulltxt = fulltxt + f"\n{text}"
                fulltxt = fulltxt + "\n END OF BILL"
    extraction()

def extraction():
    global billinfo
    clean_text = re.sub(r'\s+', ' ', fulltxt)
    response = model.generate_content(f"from {clean_text}, {prompt}") #make date format globally the same
    print(response.text)
    print(model.count_tokens(f"from the set of bills {clean_text}, {prompt}"))
    amount_date_symbol = response.text.find("-")
    item_symbol = response.text.find("_")
    responselst = str(response.text).split("\n")
    print(responselst)
    for i in responselst:
        amount = i[0:amount_date_symbol]
        date = i[amount_date_symbol + 1:item_symbol:]
        item = i[item_symbol+1::]
        billinfo.append([item,amount,date])
        writeinfile(item,amount, date)
    print(f"bill info = {billinfo}")




start_time = time.perf_counter()
print(f"run time = {start_time}")

iterfiles()


import tkinter
#-------------------------------------#
#              UI :((((







