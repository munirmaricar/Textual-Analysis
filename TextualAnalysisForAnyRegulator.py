"""
GENERALISED CODE

Steps for Executing Code For All Regulators:
1. Upload the CSV file containing the relevant data from different regulators and rename it to Data.csv. The CSV file should only contain the case sensitive headers Record ID, Institution Name and Link to File.
2. Create a new empty folder called Pages. This will store all the converted pages of the downloaded PDF file in an image format.
3. Execute the main part of the code and provide filters for the starting date, the ending date, as well as for a specific keyword if necessary.
"""

# Importing the previously installed libraries.
import sys, os, re, requests, pytesseract, urllib.request, pandas as pd
from PyPDF2 import PdfFileMerger, PdfFileReader
from pdf2image import convert_from_path
from urllib.parse import urljoin
from datetime import datetime
from bs4 import BeautifulSoup
from PIL import Image


# This function is used to download all the PDFs from a given CSV file and 
# returns a list of the names of all the PDFs that have been downloaded.
def downloadPDFs():

    # We read the data and load it using pandas into a dataframe.
    dataframe = pd.read_csv("Data.csv")

    # We iterate through all the rows in the dataframe.
    for index, row in dataframe.iterrows():

        # This variable stores the link to the PDF file.
        link = row["Link to File"]

        # This variable stores the unique ID of the row.
        uniqueID = str(row["Record ID"])

        # We modify the link if it is incomplete (links from the FED tend to be 
        # incomplete).
        if link[:5] != "https":
            link = "https://www.federalreserve.gov/" + link

        # If the link provided in the argument of the function is a webpage 
        # instead of a link that directly leads to a PDF download, we handle it 
        # differently using a Python library called Beautiful Soup. This helps 
        # us pull data out of HTML files.
        if link[-3:] == "htm":

            # This is used to open the link provided as an argument to the 
            # function.
            response = requests.get(link)

            # This variable obtains the HTML code for the webpage.
            soup = BeautifulSoup(response.text, "html.parser")    

            # Some webpages may contain multiple PDFs and this variable is used 
            # as a counter to rename the different files uniquely.
            counter = 1

            # We iterate through all the PDFs available in the webpage.  
            for url in soup.select("a[href$='.pdf']"):

                # We name the PDF files using the last portion of each link 
                # which are unique.
                fileName = uniqueID + "-" + str(counter) + ".pdf"

                # If the file has successfully been downloaded, we make a note 
                # of it.
                with open(fileName, 'wb') as f:
                    f.write(requests.get(urljoin(link, url['href'])).content)

                # We increment the counter variable for every PDF that is 
                # downloaded from a specific web page.
                counter += 1

            # This object is used to merge several different PDFs obtained from
            # one link into one PDF that can be processed.
            mergedObject = PdfFileMerger()

            # Every file is saved with its unique ID as well as a number to 
            # identify how many files are associated with that unique ID.
            for fileNumber in range(1, counter):
                mergedObject.append(PdfFileReader(uniqueID + "-" + 
                                                str(fileNumber) + '.pdf', 'rb'))
 
            # We store the merged file with its unique ID as its file name.
            mergedObject.write(uniqueID + ".pdf")

        else:

            # This is used to open the link provided as an argument to the 
            # function.
            response = urllib.request.urlopen(link)

            # This opens the file in a binary-write mode.    
            file = open(uniqueID + ".pdf", 'wb')

            # If the file has successfully been downloaded, we make a note of 
            # it.
            file.write(response.read())

            # We close the file.
            file.close()


# This function is used to convert the different pages of the PDF with the name 
# provided as an argument into images which can be processed to look for dates. 
# It also takes a keyword filter as an argument to look for the keyword in the
# PDF. 
def processPDF(pdfFile, listOfKeywords):

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

    # This list of sentences stores the sentence that contains a date or a 
    # keyword mentioned in the PDF. It is a list of lists with the first element  
    # being a boolean value to indicate if the key information is a date or not 
    # (True if it is a date), the second element being the sentence and the 
    # third element being the date only if the first element is True.
    listOfSentencesWithKeyInformation = []

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
                # listOfSentencesWithKeyInformation variable.
                listOfSentencesWithKeyInformation.append([True, 
                                                sentence.replace('\n', ' '), 
                                                date[0][0].replace('\n', ' ')])
                
            # We are checking if the current sentence does contain the keyword.    
            if (listOfKeywords != ['']):

                # We iterate through all the keywords in the list of keywords to
                # check each of them.
                for keyword in listOfKeywords:

                    # We are checking if the current keyword is present in the
                    # current sentence.
                    if (keyword.lower() in sentence.lower()):

                        # We add the sentence along with the keyword that it 
                        # contains in the form of a list to the 
                        # listOfSentencesWithKeyInformation variable.
                        listOfSentencesWithKeyInformation.append([False, 
                                        sentence.replace('\n', ' '), keyword])

    # We are returning the listOfSentencesWithKeyInformation so it can be 
    # presented in a CSV file.
    return listOfSentencesWithKeyInformation


# This function is used to read all PDFs obtained from a CSV file and output the 
# relevant information after considering the appropriate filters given as input. 
# The output should be in the form of a CSV file. 
def getDataFromDataframe(startDate, endDate, listOfKeywords):
   
    # We read the data and load it using pandas into a dataframe.
    dataframe = pd.read_csv("Data.csv")

    # We create an appropriate output dataframe with four different columns as 
    # requested.
    outputDataframe = pd.DataFrame(columns=['Record ID', 'Name of Institution',
                                            'Key Information', 'Sentence Cont' + 
                                            'aining Key Information'])
    
    # We iterate through all the rows in the dataframe.
    for index, row in dataframe.iterrows():

        # This variable stores the unique ID of the row.
        uniqueID = str(row["Record ID"])

        # This variable stores the name of the bank involved.
        institutionName = row["Institution Name"]

        # We find the list of sentences with the key information they contain 
        # mentioned in the PDF using the previous function we created.
        listOfSentencesWithKeyInformation = processPDF(uniqueID, listOfKeywords)

        # We iterate through every sentence and key information combination in 
        # the listOfSentencesWithKeyInformation variable. 
        for i in range(len(listOfSentencesWithKeyInformation)):
            
            # We check if the key information contained in the sentence is a 
            # date or not.
            if listOfSentencesWithKeyInformation[i][0] == True:

                # We convert the date to a datetime object.
                date = datetime.strptime(listOfSentencesWithKeyInformation[i][2], 
                                            '%B %d, %Y')
                
                # We check if the date is in between our starting and ending
                # date filters. 
                if ((date >= startDate) and (date <= endDate)):
                    
                    # We output the relevant information in the output 
                    # dataframe we created earlier.
                    outputDataframe = outputDataframe.append({'Record ID': 
                                        uniqueID, 
                                        'Name of Institution': 
                                        institutionName, 
                                        'Key Information': 
                                        listOfSentencesWithKeyInformation[i][2],
                                        'Sentence Containing Key Information': 
                                        listOfSentencesWithKeyInformation[i][1]}, 
                                        ignore_index = True)
                    
            # We check if the key information contained in the sentence is a 
            # keyword or not.
            else:

                # We output the relevant information in the output 
                # dataframe we created earlier.
                outputDataframe = outputDataframe.append({'Record ID': 
                                        uniqueID, 
                                        'Name of Institution': 
                                        institutionName, 
                                        'Key Information': 
                                        listOfSentencesWithKeyInformation[i][2],
                                        'Sentence Containing Key Information': 
                                        listOfSentencesWithKeyInformation[i][1]}, 
                                        ignore_index = True)

    # The outputDataframe is converted into an Output.csv file which can be 
    # viewed by the user.
    outputDataframe.to_csv('Output.csv')
    print()
    print("Please open the Output.csv file to see the relevant date informati" +
          "on.")


# This is the main part of the program.
if __name__ == "__main__":

    # This variable stores the information regarding whether or not the user 
    # would like to process PDFs that he/she has locally or if they would like 
    # to download them.
    areFilesLocal = input("Are the PDF files you would like processed availab" +
                          "le locally? Reply with a 'True' \nor 'False'. ")  
    
    # We are checking the result of the user's response.
    if areFilesLocal == "False":

        # We use the function we defined previously to download all the PDFs 
        # available from the Data.csv file.
        print("The program will use the uploaded Data.csv file to download th" +
              "e necessary PDFs.")
        downloadPDFs()

    # An instruction message is displayed in case the user wants to use the PDF 
    # files available locally.
    else:
        print("Since you are using files available locally, please ensure tha" +
              "t each PDF file is labelled according to its unique Record ID.")            
    print()

    # This variable stores the starting date that we need as a filter in a data 
    # type that can be manipulated.
    startDate = datetime.strptime(input("Enter the starting date filter in DD" + 
                                        "/MM/YYYY format: "), '%d/%m/%Y')
    
    # This variable stores the ending date that we need as a filter in a data 
    # type that can be manipulated.
    endDate = datetime.strptime(input("Enter the ending date filter in DD/M" + 
                                        "M/YYYY format: "), '%d/%m/%Y')
    
    # This variable stores the keyword that we need as a filter if the user 
    # decides to provide one. 
    # Try "Wyomissing;Reginald" to test function.
    listOfKeywords = input("Enter keywords you would like to search for in th" +
                          "e document and separate each \nkeyword from anothe" +
                          "r using only a semicolon (;). If you do not want t" +
                           "o search for \nany keywords, leave it blank:" +
                           " ").split(";")
    
    # We use the function we defined previously to get data from the different 
    # PDFs and output it in a CSV file.
    getDataFromDataframe(startDate, endDate, listOfKeywords)