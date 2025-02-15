import re

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# genusName = "musca"
# specificName = "domestica"

baseURL = "http://www.diptera.org"
searchParams = "/Nomenclator?kind=Species&sortorder=ascending&Sortfield=unsorted&Name="

# TODO: finish the regex (and maybe create more
regexGenusSpeciesAuthorYearPage = r""

# TODO: create function for importing excel/csv sheet
def importData():
    print()


# Looks up species information for a list of species (if available)
# Takes a data frame containing scientific species names
# Pre-condition: species names consist of two words (genus name and specific name), no subsp./var.
# returns data frame with extra columns with relevant information
def processSpecies(speciesDataFrame):
    newInformation = []
    for index, row in speciesDataFrame.iterrows():
        newRow = []
        if len(row['name'].split(" ")) != 2:
            print(f"{row['name']}: name invalid, skipping")
        else:
            print(f"{row['name']}: starting look-up")
            genusName, specificName = row['name'].split(" ")
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
    print(f"Species name: {speciesName}, recordURL: {recordURL}")

    if len(recordURL) > 4:
        specInfoList = getSpeciesInfo(baseURL + recordURL)
        print(f"Species name: {speciesName}, specInfoList: {recordURL}")
        return specInfoList

    # Return empty list if lookUpSpeciesURL() has failed
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
        href = soup.find_all("a", class_="milouska")[0].get('href')
        return href


# Parses the species record page
# Takes a string with the URL to the web page containing the record
# Returns a list with the relevant information or a status code in case the request failed (also as string)
def getSpeciesInfo(specURL):
    r = requests.get(specURL)
    print(specURL)
    if r.status_code != 200:
        return str(r.status_code)
    else:
        soup = BeautifulSoup(r.text, "html.parser")
        for i in soup.find_all("td", class_="Verdana-11-sort"):
            print(i.text)
        for i in soup.find_all("td", class_="Verdana-11-graa"):
            print(40*"-")
            print(i.text)
        print(40 * "-")
        # TODO: parse information using regex's
        #  species name, author, year, citation, type, family and range
        #  Return empty list if failed
        # return specInfo





# EXAMPLE OF SCRAPED PAGE                                                                                               USEFUL INFORMATION
# ----------------------------------------
# Musca domestica Linnaeus, 1758: 596                                                                                   0  genus, specific name, author, year, page number
# ----------------------------------------
# TL: Europe & North America (ST A lost)                                                                                1  type
# ----------------------------------------
# (Available, Valid) Current Valid Name                                                                                 2  status
# ----------------------------------------
#
# ----------------------------------------
# Musca domestica ssp. domestica Linnaeus, 1758
# ----------------------------------------
# Muscidae                                                                                                              5  Family
# ----------------------------------------
# Species
# ----------------------------------------
# (PA NE: PA AF AU OR NE NT) cosmopolitan                                                                               7  Range
# ----------------------------------------
#
# ----------------------------------------
# Linnaeus, C. 1758. Systema naturae... Ed. 10, Vol. 1. 824 pp. L. Salvii, Holmiae [= Stockholm]. [1758.01.01]          9  Citation
# ----------------------------------------
# 99
# ----------------------------------------
# Poole, R.W. & Gentili, P. (eds.) 1996                                                                                 10 Authority
# ----------------------------------------
# 07/24/2024
# ----------------------------------------
# Species
# ----------------------------------------
# 69872
# ----------------------------------------


# TODO: list of information:
#  genus name
#  specific name
#  author
#  year
#  page number
#  type
#  status
#  family
#  range
#  citation
#  authority



df = pd.DataFrame({"name": ["Musca domestica"]})
processSpecies(df)
