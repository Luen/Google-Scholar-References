import argparse
from scholarly import scholarly  # https://github.com/scholarly-python-package/scholarly
import json
import re
import urllib.request
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib import request
import numpy as np
import time
import math

pagesCrawled = 0

# Retrieve the author's id
def get_author_id(name):
    search_query = scholarly.search_author(name)
    author = scholarly.fill(next(search_query))
    # example output ynWS968AAAAJ:Mojj43d5GZwC
    return author["scholar_id"]


# https://stackoverflow.com/questions/41005700/function-that-returns-capitalized-initials-of-name
def initialize(fullname):
    xs = fullname
    name_list = xs.split()
    surname = name_list[-1]
    initials = ""
    for name in name_list:  # go through each name
        if name != surname:
            initials += name[0].upper() + "."
            if name != name_list[-2]:
                initials += " "  # append a space except for the end one
        else:
            initials = surname.title() + ", " + initials  # prepend the surname
    return initials


# Get authors in a usable format
def standandise_authors(authors):  # prettify_authors
    author_list = authors.lower().split(" and ")
    authors = ""
    for a in author_list:
        if a != author_list[0]:
            authors += ", "
        authors += initialize(a)
        # et al.
    return authors


def getImpactFactor(title):
    if not title:
        return False
    for impactFactorArr in impactFactorArray:
        if impactFactorArr["title"].lower() == title.lower():
            return impactFactorArr["impactFactor"]
    # no exact match found, so search:
    return searchImpactFactor(title, 12)


def searchImpactFactor(searchTitle, threshold):
    lowestTitle = ""
    lowestImpactFactor = ""
    lowestLevenshtein = 100
    for impactFactorArr in impactFactorArray:
        currentTitle = impactFactorArr["title"]
        currentLevenshtein = levenshtein(searchTitle.lower(), currentTitle.lower())
        if currentLevenshtein < lowestLevenshtein:
            lowestLevenshtein = currentLevenshtein
            lowestTitle = currentTitle
            lowestImpactFactor = impactFactorArr["impactFactor"]
    if lowestLevenshtein <= threshold:
        print(
            "Could not find exact match:",
            searchTitle,
            "-->",
            lowestTitle,
            lowestImpactFactor,
        )
        return lowestImpactFactor
    return False


# https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros((size_x, size_y))
    for x in range(size_x):
        matrix[x, 0] = x
    for y in range(size_y):
        matrix[0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x - 1] == seq2[y - 1]:
                matrix[x, y] = min(
                    matrix[x - 1, y] + 1, matrix[x - 1, y - 1], matrix[x, y - 1] + 1
                )
            else:
                matrix[x, y] = min(
                    matrix[x - 1, y] + 1, matrix[x - 1, y - 1] + 1, matrix[x, y - 1] + 1
                )
    return matrix[size_x - 1, size_y - 1]


def getDOIs(url):
    req = request.Request(
        url, data=None, headers={"User-Agent": "Mozilla/5.0"}, method="GET"
    )  # https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
    try:
        cookieProcessor = request.HTTPCookieProcessor()
        opener = request.build_opener(cookieProcessor)
        req = opener.open(req, timeout=100)
        cookie = req.info().get_all("Set-Cookie")
        content_type = req.info()["Content-Type"]
        charset = req.info().get_content_charset()
        html = req.read()  # .decode('utf-8')
        return parseDOIs(html)
    except HTTPError as err:
        print("err status: {0}".format(err), url)
        return False


def parseDOIs(html):
    # https://www.crossref.org/blog/dois-and-matching-regular-expressions/
    # regex /^10.\d{4,9}/[-._;()/:A-Z0-9]+$/i
    # pattern = r"(?:https:\/\/doi.org[^\/])?(10.\d{4,9}\/[-._;()\/:A-Z0-9]+)" # this one seems to catch alot with ';' substring
    pattern = r"(?:https:\/\/doi.org[^\/])?(10.\d{4,9}\/[-._()\/:A-Z0-9]+)"
    matches = re.findall(pattern, str(html), re.IGNORECASE)
    return matches


def similariseUrl(url):
    url = url.replace(
        "/abs/", "/"
    )  # https://royalsocietypublishing.org & https://onlinelibrary.wiley.com/
    url = url.replace("/article/", "/")  # https://link.springer.com/
    url = url.replace("/articles/", "/")  # https://www.nature.com
    url = url.replace("http://", "https://")
    url = url.replace("//www.", "//")
    url = url.split("?")[0]
    return url


def checkDOI(doi, expectUrl):
    shortUrl = "https://doi.org/api/handles/" + doi
    opener = urllib.request.build_opener()
    r = opener.open(shortUrl)
    data = r.read()
    try:
        j = json.loads(data)
        for value in j["values"]:
            if value["type"] == "URL":
                followUrl = value["data"]["value"]
                if followUrl == expectUrl:
                    return True  # exact match
                if similariseUrl(followUrl) == similariseUrl(expectUrl):
                    return True  # match without parameters
    except:
        print("Could not load JSON data")
    return False


def fallbackCheckDOI(doi, expectUrl):
    shortUrl = "https://doi.org/" + doi
    req = request.Request(
        shortUrl,
        data=None,
        headers={"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"},
        method="GET",
    )
    try:
        cookieProcessor = request.HTTPCookieProcessor()
        opener = request.build_opener(cookieProcessor)
        req = opener.open(req, timeout=100)
        cookie = req.info().get_all("Set-Cookie")
        content_type = req.info()["Content-Type"]
        charset = req.info().get_content_charset()
        html = req.read()  # .decode('utf-8')
        followUrl = req.geturl()
        if followUrl == expectUrl:
            return True  # shortDOI links to the URL
        if similariseUrl(followUrl) == similariseUrl(expectUrl):
            return True  # links to the URL
        followDois = parseDOIs(html)
        if followDois:
            followDoi = shortDOI(followDois[0])
            if followDoi and doi == followDoi:
                return True  # The DOI is the first DOI on the page
            if doi in followDois:
                return True  # DOI is on page
            # if ";" in somestring #check if ; in string and split string and then check if in followDois
            #    doi = doi.split(';')[0]
            #    if doi in followDois:
            #        print("split doi by ; which is in DOIs on page",doi,followDois)
            #        return True
        if hasCaptcha(html):
            print("Captcha on website", doi, expectUrl)
            time.sleep(30)
        print("Couldn't confirm doi", doi, expectUrl)
        return False
    except HTTPError as err:
        print("err status: {0}".format(err), doi, expectUrl)
        return False


def shortDOI(doi):
    # also see this service - http://shortdoi.org/
    # e.g., http://shortdoi.org/10.1007/s10113-015-0832-z?format=json
    BASE_URL = "https://doi.org/"
    # shortUrl= doi if doi.startswith(BASE_URL) else BASE_URL+doi
    shortDOI = doi.replace(BASE_URL, "")
    return shortDOI


def hasCaptcha(html):
    captchas = [
        "gs_captcha_ccl",  # the normal captcha div
        "recaptcha",  # the form used on full-page captchas
        "captcha-form",  # another form used on full-page captchas
        "rc-doscaptcha-body",  # DOS
    ]
    for id in captchas:
        if id in str(html):
            return True
    return False


"""
#just a test:
import urllib.request
opener = urllib.request.build_opener()
opener.addheaders = [('Accept', 'application/vnd.crossref.unixsd+xml')]
r = opener.open('http://dx.doi.org/10.1007/s10113-015-0832-z')
print(r.info()['Link'])
#print(r.read())
exit()
"""


with open("./journal-if-2020.json") as json_file:
    impactFactorArray = json.load(json_file)

# get argument passed in python commandline
parser = argparse.ArgumentParser(description="Input full name.")
parser.add_argument(
    "--name",
    nargs=1,
    metavar=('"Full Name"'),
    help='You\'re full name e.g., python references.py --name "Jodie Rummer"',
)
args = parser.parse_args()
if not args.name:
    print(
        'Please re-run with --name argument. E.g., python references.py --name "Jodie Rummer"'
    )
    print("See python references.py -h for more details")
    exit()
author_name = args.name[0]
if (" " not in author_name) == True:
    print(
        'Please use full name with quotes. E.g., python references.py --name "Jodie Rummer"'
    )
    print("See python references.py -h for more details")
    exit()


print("Getting Google Scholar ID for", author_name)
author_id = get_author_id(author_name)
pagesCrawled += 1
print("Author's ID:", author_id)

print("Getting Google Scholar publication list sorted by year")
# author = scholarly.search_author_id(id = 'ynWS968AAAAJ', filled = True, sortby = "year", publication_limit = 5)
author = scholarly.search_author_id(id=author_id, filled=True, sortby="year")
pagesCrawled += math.ceil(len(author["publications"]) / 100)

print("Opening file to write to")
with open(
    "references-" + author_name.lower().replace(" ", "-") + ".html",
    "w",
    encoding="utf8",
) as f:

    citations = str(author["citedby"])
    hindex = str(author["hindex"])
    i10index = str(author["i10index"])

    print("Citations:", citations)
    f.write("Citations: " + citations + "<br>")

    print("h-index:", hindex)
    f.write("h-index: " + hindex + "<br>")

    print("i10-index:", i10index)
    f.write("i10-index: " + i10index + "<br>")

    print(
        "Getting data from", len(author["publications"]), "publications. Please wait..."
    )
    for pub in author["publications"]:
        publication = scholarly.fill(pub)
        pagesCrawled += 1

        authors = str(
            publication["bib"]["author"]
        )  # .encode("windows-1252").decode("utf-8")
        authors = standandise_authors(authors)

        title = str(publication["bib"]["title"])
        pub_year = ""
        if "pub_year" in pub["bib"]:
            pub_year = str(publication["bib"]["pub_year"])
        else:
            print("Could not year for", title, ". Skipping...")
            continue

        journal = ""
        impactfactor = ""
        if "journal" in pub["bib"]:
            journal = str(publication["bib"]["journal"]).title()
            journal == journal if journal.strip().lower() != "null" else ""

            impactfactor = getImpactFactor(journal)
            if not impactfactor:
                print("Could not get impact factor for journal:", journal)

            impactfactor = "IF: " + impactfactor if impactfactor else ""

        volume = ""
        if "volume" in pub["bib"]:
            volume = str(publication["bib"]["volume"])
        pages = ""
        if "pages" in pub["bib"]:
            pages = str(publication["bib"]["pages"])
        pub_url = str(publication["pub_url"])
        # DOIs needs a proxy or tor
        # dois = getDOIs(pub_url)
        dois = False
        pagesCrawled += 1
        time.sleep(10)  # sleep after scraping DOIs from journal. Becuase the next journal may be the same journal and don't want to reqest too many at once. TODO: Proxy or Tor
        doi = ""
        if dois:
            doi = str(dois[0])
            pagesCrawled += 1  # checkDOI()
            if not checkDOI(doi, pub_url):
                pagesCrawled += 1  # fallbackCheckDOI()
                time.sleep(60)  # sleep after scraping DOIs from journal. Too many requests and you get a HTTP Error 403: Forbidden
                if not fallbackCheckDOI(doi, pub_url):
                    doi = ""

        num_citations = str(publication["num_citations"])
        num_citations = "C: " + num_citations if num_citations else ""

        reference = ""
        reference += authors
        reference += " (" + pub_year + ") "
        reference += title
        if journal:
            reference += " <em>" + journal + "</em> "
        reference += volume
        if pages:
            reference += ", " + pages + ". "
        if doi:
            reference += doi
        else:
            reference += pub_url
        if num_citations:
            reference += " " + num_citations
        if impactfactor:
            reference += " " + impactfactor
        # print(reference)
        f.write("<p>" + reference + "</p>")

print(pagesCrawled, "pages crawled")
