"""
SPECIFIC CODE FOR EACH REGULATOR

Steps for Executing Code Specific For Regulator:
1. Import the data by uploading the CSV and XLSX files from the different regulators. Rename them as FDIC.csv, OCC.xlsx and FED.csv respectively.
2. Create a new empty folder called Pages. This will store all the converted pages of the downloaded PDF file in an image format.
3. Execute the main part of the code and provide information specific for the type of regulator requested.
"""

# Importing the previously installed libraries.
import sys
import os
import re
import requests
import pytesseract
import urllib.request
import pandas as pd
from pdf2image import convert_from_path
from urllib.parse import urljoin
from datetime import datetime
from bs4 import BeautifulSoup
from PIL import Image


# This function is used to download a PDF given a link and it saves the PDF
# using the given name.
def downloadPDF(link, fileName):

    # This variable stores a list of the PDF files that have been downloaded
    # from the appropriate link.
    listOfFiles = []

    # If the link provided in the argument of the function is a webpage instead
    # of a link that directly leads to a PDF download, we handle it differently
    # using a Python library called Beautiful Soup. This helps us pull data out
    # HTML files.
    if link[-3:] == "htm":

        # This is used to open the link provided as an argument to the function.
        response = requests.get(link)

        # This variable obtains the HTML code for the webpage.
        soup = BeautifulSoup(response.text, "html.parser")

        # We iterate through all the PDFs available in the webpage.
        for url in soup.select("a[href$='.pdf']"):

            # We name the PDF files using the last portion of each link which
            # are unique.
            filename = url['href'].split('/')[-1]

            # We append the listOfFiles variable.
            listOfFiles.append(filename)

            # If the file has successfully been downloaded, we make a note of
            # it.
            with open(filename, 'wb') as f:
                f.write(requests.get(urljoin(link, url['href'])).content)

    else:
        # This is used to open the link provided as an argument to the function.
        response = urllib.request.urlopen(link)

        # This opens the file in a binary-write mode.
        file = open(fileName + ".pdf", 'wb')

        # If the file has successfully been downloaded, we make a note of it.
        file.write(response.read())

        # We close the file.
        file.close()

        # We append the listOfFiles variable.
        listOfFiles.append(fileName + ".pdf")

    # We return the listOfFiles variable so other functions can see how many
    # files were downloaded.
    return listOfFiles


# This function is used to convert the different pages of the PDF with the name
# provided as an argument into images which can be processed to look for dates.
def processPDF(pdfFile):

    # Name of the PDF file.
    pdf = pdfFile + ".pdf"

    # This variable stores all the pages of the PDF.
    pages = convert_from_path(pdf, 500)

    # This variable is a counter to store each page of the PDF to an image.
    imageCounter = 1

    # We iterate through all the pages stored above.
    for page in pages:

        # We are specifying the file name for each page of the PDF to be stored
        # as its corresponding image file. For instance, page 1 of the PDF will
        # be stored as an image with the name Page 1.jpg in the Pages folder.
        fileName = "Pages/Page " + str(imageCounter) + ".jpg"

        # This will save the image of the page in our system.
        page.save(fileName, 'JPEG')

        # This will increment the image counter to show how many images we have.
        imageCounter = imageCounter + 1

    # This variable stores the total number of pages we have in our file.
    fileLimit = imageCounter - 1

    # This list of sentences stores the sentence that contains a date that was
    # mentioned in the PDF. It is a list of lists with the first element being
    # the sentence and the second element being the date.
    listOfSentencesWithDate = []

    # We iterate again from 1 to the total number of pages in the PDF.
    for i in range(1, fileLimit + 1):

        # We set the file name to recognize text from the respective image of
        # each page. Again, these files will be Page 1.jpg, Page 2.jpg, etc.
        fileName = "Pages/Page " + str(i) + ".jpg"

        # This recognizes the text as a string from the image using pytesseract.
        text = str(((pytesseract.image_to_string(Image.open(fileName)))))

        # This variable stores the recognized text. In many PDFs, at the ending
        # of a line, if a word cannot be written fully, a 'hyphen' is added and
        # the rest of the word is written in the next line. We are removing
        # that.
        text = text.replace('-\n', '')

        # We split the text up into a list of different sentences.
        sentences = text.split(". ")

        # We iterate through all the sentences.
        for sentence in sentences:

            # The date variable stores the date that occurs in the current
            # sentence we are looking at and stores it as a list using regular
            # expression.
            date = re.findall(r'((January|February|March|April|May|June|July|' +
                              'August|September|October|November|December' +
                              ')\s+\d{1,2},\s+\d{4})', sentence)

            # We are checking if the current sentence does contain a date.
            if date != []:

                # We add the sentence and the date in the form of a list to the
                # listOfSentencesWithDate variable.
                listOfSentencesWithDate.append([sentence.replace('\n', ' '),
                                                date[0][0].replace('\n', ' ')])

    # We are returning the listOfSentencesWithDate so it can be presented in a
    # CSV file.
    return listOfSentencesWithDate


# This function is used to differentiate the operations for different
# regulators. The regulator name is provided as argument to the function.
def getDataFromDataframe(regulatorName):

    # We are checking if the regulator is FDIC.
    if regulatorName == "FDIC":

        # We read the FDIC data and load it using pandas into a dataframe.
        dataframe = pd.read_csv("FDIC.csv")

        # This variable stores the docket number that is provided as a user
        # input.
        docketNumber = input("Enter the FDIC docket number for the document " +
                             "you would like to see the date information for: ")

        # This inserts a unique ID in the dataframe that is displayed in the
        # output.
        dataframe.insert(0, 'Unique ID', range(1, len(dataframe) + 1))

        # This flag is used to indicate if we found the docket number requested
        # by the user in the dataframe.
        found = False

        # We iterate through all the rows in the dataframe.
        for index, row in dataframe.iterrows():

            # We are updating the current docket number that we are going to
            # compare. Some rows may have multiple docket numbers and in such
            # scenarious, we are splitting them into a list of docket numbers.
            currentDocketNumber = str(row[" Docket Number"])
            currentDocketNumber = currentDocketNumber.split(",")

            # If the docket number matches to the one requested by the user, we
            # download the PDF using the link for the documents for the
            # corresponding docket number in the same row.
            if docketNumber in currentDocketNumber:

                # We update the found flag to True.
                found = True

                # This variable stores the link to the PDF file.
                linkToFile = row[" File URL"]

                # This variable stores the name of the bank involved.
                institutionName = row[" Bank Name"]

                # This variable stores the unique ID of the row.
                uniqueID = row["Unique ID"]

                # We download the PDF using the previous function we created.
                listOfFiles = downloadPDF(linkToFile, docketNumber)

                # We find the list of sentences with date mentioned in the PDF
                # using the previous function we created.
                listOfSentencesWithDate = processPDF(docketNumber)

                # We create an appropriate output dataframe with four different
                # columns as requested.
                outputDataframe = pd.DataFrame(columns=['Unique ID', 'Name o' +
                                                        'f Institution', 'Date',
                                                        'Sentence Containing' +
                                                        ' Date'])

                # We iterate through every sentence and date combination in the
                # list of sentences with date.
                for i in range(len(listOfSentencesWithDate)):

                    # We convert the date to a datetime object.
                    date = datetime.strptime(listOfSentencesWithDate[i][1],
                                             '%B %d, %Y')

                    # We check the year of the date since we only include
                    # dates that occur after 1990.
                    if date.year >= 1990:

                        # We output the relevant information in the output
                        # dataframe we created earlier.
                        outputDataframe = outputDataframe.append({'Unique ID':
                                                                  uniqueID,
                                                                  'Name of Institution':
                                                                  institutionName,
                                                                  'Date':
                                                                  listOfSentencesWithDate[i][1],
                                                                  'Sentence Containing Date':
                                                                  listOfSentencesWithDate[i][0]},
                                                                 ignore_index=True)

                # We display an error message if there are no dates after 1990
                # that appear in the document.
                if outputDataframe.empty:
                    print("There are no relevant dates after the year 1990 in" +
                          " the document referred to with the FDIC docket num" +
                          "ber of " + docketNumber + ".")
                else:
                    # The outputDataframe is converted into an Output.csv file
                    # which can be viewed by the user.
                    outputDataframe.to_csv('Output.csv')
                    print()
                    print("Please open the Output.csv file to see the relevan" +
                          "t date information.")

        # We display an error message if the FDIC docket number is not found in
        # the dataframe.
        if found == False:
            print("The FDIC docket number of " + docketNumber + " is incorrec" +
                  "t. Please run the program again.")

    # We are checking if the regulator is OCC.
    elif regulatorName == "OCC":

        # We read the OCC data and load it using pandas into a dataframe.
        dataframe = pd.read_excel("OCC.xlsx")

        # This variable stores the docket number that is provided as a user
        # input.
        orderNumber = input("Enter the OCC order number for the document you " +
                            "would like to see the date information for: ")

        # This flag is used to indicate if we found the docket number requested
        # by the user in the dataframe.
        found = False

        # We iterate through all the rows in the dataframe.
        for index, row in dataframe.iterrows():

            # We are updating the current order number that we are going to
            # compare.
            currentOrderNumber = str(row["Order Number"])

            # If the order number matches to the one requested by the user, we
            # download the PDF using the link for the documents for the
            # corresponding order number in the same row.
            if orderNumber == currentOrderNumber:

                # We update the found flag to True.
                found = True

                # This variable stores the link to the PDF file.
                linkToFile = row["Link to Enforcement Action"]

                # This variable stores the name of the bank involved.
                institutionName = row["Institution Name"]

                # This variable stores the unique ID of the row.
                uniqueID = row["Record ID"]

                # We download the PDF using the previous function we created.
                downloadPDF(linkToFile, orderNumber)

                # We find the list of sentences with date mentioned in the PDF
                # using the previous function we created.
                listOfSentencesWithDate = processPDF(orderNumber)

                # We create an appropriate output dataframe with four different
                # columns as requested.
                outputDataframe = pd.DataFrame(columns=['Unique ID', 'Name o' +
                                                        'f Institution', 'Date',
                                                        'Sentence Containing' +
                                                        ' Date'])

                # We iterate through every sentence and date combination in the
                # list of sentences with date.
                for i in range(len(listOfSentencesWithDate)):

                    # We convert the date to a datetime object.
                    date = datetime.strptime(listOfSentencesWithDate[i][1],
                                             '%B %d, %Y')

                    # We check the year of the date since we only include
                    # dates that occur after 1990.
                    if date.year >= 1990:

                        # We output the relevant information in the output
                        # dataframe we created earlier.
                        outputDataframe = outputDataframe.append({'Unique ID':
                                                                  uniqueID,
                                                                  'Name of Institution':
                                                                  institutionName,
                                                                  'Date':
                                                                  listOfSentencesWithDate[i][1],
                                                                  'Sentence Containing Date':
                                                                  listOfSentencesWithDate[i][0]},
                                                                 ignore_index=True)

                # We display an error message if there are no dates after 1990
                # that appear in the document.
                if outputDataframe.empty:
                    print("There are no relevant dates after the year 1990 in" +
                          " the document referred to with the OCC order numbe" +
                          "r of " + orderNumber + ".")
                else:
                    # The outputDataframe is converted into an Output.csv file
                    # which can be viewed by the user.
                    outputDataframe.to_csv('Output.csv')
                    print()
                    print("Please open the Output.csv file to see the relevan" +
                          "t date information.")

        # We display an error message if the OCC order number is not found in
        # the dataframe.
        if found == False:
            print("The OCC order number of " + orderNumber + " is incorrect. " +
                  "Please run the program again.")

    # We are checking if the regulator is FED.
    elif regulatorName == "FED":

        # We read the FED data and load it using pandas into a dataframe.
        dataframe = pd.read_csv("FED.csv")

        # This list of sentences stores the sentence that contains a date that
        # was mentioned in the PDF.
        listOfSentencesWithDate = []

        # This variable stores the URL for the document that the user provides
        # as input.
        url = input("Enter the FED URL for the document you would like to see" +
                    " the date information for: ")

        # This inserts a unique ID in the dataframe that is displayed in the
        # output.
        dataframe.insert(0, 'Unique ID', range(1, len(dataframe) + 1))

        # This flag is used to indicate if we found the docket number requested
        # by the user in the dataframe.
        found = False

        # We iterate through all the rows in the dataframe.
        for index, row in dataframe.iterrows():

            # We are updating the current URL that we are going to compare.
            currentURL = str(row["URL"])

            # If the URL matches to the one requested by the user, we download
            # the PDF using the link for the documents.
            if url == currentURL:

                # We update the found flag to True.
                found = True

                # This variable stores the link to the PDF file.
                linkToFile = "https://www.federalreserve.gov/" + currentURL

                # This variable stores the name of the bank involved.
                institutionName = row["Banking Organization"]

                # This variable stores the unique ID of the row.
                uniqueID = str(row["Unique ID"])

                # We download the PDF using the previous function we created.
                listOfFiles = downloadPDF(linkToFile, uniqueID)

                # Since the FED can result in multiple PDFs needing to be
                # analysed, we analyse each of them by iterating through all the
                # files in the listOfFiles variables that is returned as a
                # result of executing the downloadPDF function.
                for tempFile in listOfFiles:

                    # We find the list of sentences with date mentioned in the
                    # PDF using the previous function we created. We do this for
                    # all the files in the list of files.
                    listOfSentencesWithDate += processPDF(tempFile[:-4])

                # We create an appropriate output dataframe with four different
                # columns as requested.
                outputDataframe = pd.DataFrame(columns=['Unique ID', 'Name o' +
                                                        'f Institution', 'Date',
                                                        'Sentence Containing' +
                                                        ' Date'])

                # We iterate through every sentence and date combination in the
                # list of sentences with date.
                for i in range(len(listOfSentencesWithDate)):

                    # We convert the date to a datetime object.
                    date = datetime.strptime(listOfSentencesWithDate[i][1],
                                             '%B %d, %Y')

                    # We check the year of the date since we only include
                    # dates that occur after 1990.
                    if date.year >= 1990:

                        # We output the relevant information in the output
                        # dataframe we created earlier.
                        outputDataframe = outputDataframe.append({'Unique ID':
                                                                  uniqueID,
                                                                  'Name of Institution':
                                                                  institutionName,
                                                                  'Date':
                                                                  listOfSentencesWithDate[i][1],
                                                                  'Sentence Containing Date':
                                                                  listOfSentencesWithDate[i][0]},
                                                                 ignore_index=True)

                # We display an error message if there are no dates after 1990
                # that appear in the document.
                if outputDataframe.empty:
                    print("There are no relevant dates after the year 1990 in" +
                          " the document referred to with the url of " + url)
                else:
                    # The outputDataframe is converted into an Output.csv file
                    # which can be viewed by the user.
                    outputDataframe.to_csv('Output.csv')
                    print()
                    print("Please open the Output.csv file to see the relevan" +
                          "t date information.")

        # We display an error message if the URL is not found in the dataframe.
        if found == False:
            print("The URL of " + url + " is incorrect. Please run the progra" +
                  "m again.")


# This is the main part of the program.
if __name__ == "__main__":

    # This variable stores the regulator name that the user will provide as
    # input.
    regulatorName = input("Enter the regulator you would like to obtain docum" +
                          "ents for (FDIC, OCC or FED): ")

    # The user will be asked to try again if the regulator is not one of the
    # three regulators allowed.
    while ((regulatorName != "FDIC") and (regulatorName != "OCC") and
           (regulatorName != "FED")):
        regulatorName = input("Please try a valid regulator (FDIC, OCC or FED" +
                              "): ")

    # We use the function we defined previously to deal with the regulator
    # provided in an appropriate way.
    getDataFromDataframe(regulatorName)
