import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

#################### Pre-condition:
# The input consists of one Excel file with a column containing the species names. These names consist of two words
# (genus name and specific name) separated by a space, no ssp./var. or anything else.

# For some species, only a subspecies is available in the database. These will not be handled correctly unfortunately


#################### CHANGE THESE VARIABLE NAMES (CaSe-SeNSiTiVe):
# Name of the Excel file with the species names that need to be looked up:
nameInputFile = "InputExample"
# Name of the Excel file that needs to be created (if the same as above, the original will be overwritten):
nameOutputFile = "OutputExample"
# Sheet name of the Excel file that contains the names:
sheetName = "Sheet1"
# Column name that contains the names (note: the first cell is considered a header and not the species name):
columnName = "Name"





#################### No need to change anything below this line

# General variables
# Website URL
baseURL = "http://www.diptera.org"
# Parameters for initial search
searchParams = "/Nomenclator?kind=Species&sortorder=ascending&Sortfield=unsorted&Name="
# File extension for Excel
extension = ".xlsx"
# Regular expression for separating the first columns
regexGenusSpeciesAuthorYearPage = re.compile(r"(\S+) (\S+) ([^,]+), (\d{4}): (\d{1,6})")
# The column names of final table
colNames = ["Original name (used in search)",
            "Genus name (found name)",
            "Specific name (found name)",
            "Author",
            "Year",
            "Page number",
            "Type",
            "Status",
            "Notes",
            "Valid name",
            "Family",
            "Category",
            "Range",
            "URL",
            "Citation",
            "Verification code",
            "Authority",
            "Revision date",
            "Kind of name",
            "Record #"]


# Imports data, processes the data and writes the result to a new file
# Takes a string with the name of the input file
# Returns None
# Creates a new Excel file
def importProcessAndOutputData(fileName):
    dfSpecNames = pd.read_excel(fileName, sheet_name=sheetName)
    dfSpecNames = dfSpecNames[[columnName]]
    print(dfSpecNames.head(20))
    print('\n')
    # Create second data frame with new information
    dfFinal = processSpecies(dfSpecNames)
    # Set the column names
    dfFinal.columns = colNames
    # Write output to Excel
    dfFinal.to_excel(nameOutputFile + extension, index=False)


# Looks up species information for a list of species (if available)
# Takes a data frame containing scientific species names
# Pre-condition: species names consist of a string of two words (genus name and specific name), no subsp./var.
# Returns data frame with extra columns with relevant information
def processSpecies(speciesDataFrame):
    newInformation = []
    for index, row in speciesDataFrame.iterrows():
        newRow = []
        if not isinstance(row[columnName], str):
            print(f"{row[columnName]}: name invalid, skipping")
        elif len(row[columnName].split(" ")) != 2:
            print(f"{row[columnName]}: name invalid, skipping")
        else:
            print(f"{row[columnName]}: starting look-up")
            genusName, specificName = row[columnName].split(" ")
            speciesName = "+".join([genusName, specificName])
            newRow = lookUpSpeciesInfo(speciesName)

        newInformation.append(newRow)
    newInfoDF = pd.DataFrame(newInformation)
    speciesDataFrameExtended = pd.concat([speciesDataFrame, newInfoDF], axis=1)
    return speciesDataFrameExtended


# Takes a species name and returns a data frame contain the species information
# Takes a string with the scientific species name (genus and specific name) separated by a plus sign
# Returns list containing strings for the species name, author, year, citation, type, family and range
def lookUpSpeciesInfo(speciesName):
    recordURL = lookUpSpeciesURL(baseURL + searchParams + speciesName)
    if len(recordURL) > 4:
        specInfoList = getSpeciesInfo(baseURL + recordURL)
        if len(specInfoList) < 2:
            # Return empty list if getSpeciesInfo() has failed
            print(f"request failed. specInfoList (status code): {specInfoList}")
            return []
        # print(f"Species name: {speciesName}, recordURL: {baseURL + recordURL}, specInfoList: {specInfoList}")
        return specInfoList
    # Return empty list if lookUpSpeciesURL() has failed
    print(f"request failed. recordURL (status code): {recordURL}")
    return []


# Retrieves the species URL for a species search string
# Takes a string with the search URL
# Returns a string containing the ID or a status code in case the request failed (also as string)
def lookUpSpeciesURL(searchURL):
    r = requests.get(searchURL)
    if r.status_code != 200:
        return str(r.status_code)
    else:
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all("a", class_="milouska")
        if links:
            href = links[0].get('href')
            return href
        else:
            return "NA"


# Parses the species record page
# Takes a string with the URL to the web page containing the record
# Returns a list with the relevant information or a status code in case the request failed (also as list)
def getSpeciesInfo(specURL):
    r = requests.get(specURL)
    inf = []
    applyRegex = True
    if r.status_code != 200:
        return [str(r.status_code)]
    else:
        soup = BeautifulSoup(r.text, "html.parser")
        for i in soup.find_all("td", class_="Verdana-11-graa"):
            if applyRegex:
                applyRegex = False
                reg = regexGenusSpeciesAuthorYearPage.search(i.text)
                inf.append(reg[1])  # Genus name
                inf.append(reg[2])  # Species name
                inf.append(reg[3])  # Author
                inf.append(reg[4])  # Year
                inf.append(reg[5])  # Page number
            else:
                inf.append(i.text)  # Append rest without splitting
        return inf


#################### Start of the program
importProcessAndOutputData(nameInputFile + extension)
