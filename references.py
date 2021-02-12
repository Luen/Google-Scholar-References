import argparse
from scholarly import scholarly
import asyncio
from pyppeteer import launch

# Retrieve the author's id
def get_author_id(name):
    search_query = scholarly.search_author(name)
    author = scholarly.fill(next(search_query))
    #example output ynWS968AAAAJ:Mojj43d5GZwC
    return author["scholar_id"]
#https://stackoverflow.com/questions/41005700/function-that-returns-capitalized-initials-of-name
def initialize(fullname):
    xs = (fullname)
    name_list = xs.split()
    surname = name_list[-1]
    initials = ""
    for name in name_list:  # go through each name
        if name != surname:
            initials += name[0].upper() + "."
            if name != name_list[-2]:
                initials += " " # append a space except for the end one
        else:
            initials = surname.title() + ", " + initials # prepend the surname
    return initials
#Get authors in a usable format
def standandise_authors(authors): #prettify_authors
    author_list = authors.lower().split(' and ')
    authors = ""
    for a in author_list:
        if a != author_list[0]:
            authors += ", "
        authors += initialize(a)
        # et al.
    return authors


async def main():
    # get argument passed in python commandline
    parser = argparse.ArgumentParser(description='Input full name.')
    parser.add_argument('--name', nargs=1, metavar=('\"Full Name\"'), help='You\'re full name e.g., python references.py --name "Jodie Rummer"')
    args = parser.parse_args()
    if not args.name:
        print('Please re-run with --name argument. E.g., python references.py --name "Jodie Rummer"')
        print('See python references.py -h for more details')
        exit()
    author_name = args.name[0]
    if (' ' not in author_name) == True:
        print('Please use full name with quotes. E.g., python references.py --name "Jodie Rummer"')
        print('See python references.py -h for more details')
        exit()

    print("Getting Google Scholar ID for", author_name)
    author_id = get_author_id(author_name)
    print("Author's ID:", author_id)

    #https://github.com/scholarly-python-package/scholarly
    print("Getting Google Scholar publication list sorted by year")
    #author = scholarly.search_author_id(id = 'ynWS968AAAAJ', filled = True, sortby = "year", publication_limit = 5)
    author = scholarly.search_author_id(id = author_id, filled = True, sortby = "year")
    #scholarly.pprint(author)
    #print(author)
    #exit()
    #print(scholarly.fill(author['publications'][0]))
    #exit()
    # Print the titles of the author's publications
    #print([pub['bib']['title'] for pub in author['publications']])
    #exit()


    #could also have used requests-html https://github.com/psf/requests-html
    #journal-if.com doesn't work in Chromium use Chrome instead
    print("Launching pyppeteer in headless mode")
    #browser = await launch(headless=False, executablePath='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
    browser = await launch(headless=True, executablePath='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
    page = await browser.newPage()
    await page.setViewport({'width': 1536, 'height': 698})
    await page.goto('https://journal-if.com/')
    print("pyppeteer launched")
    selector = ".MuiInputBase-input"
    await page.waitForSelector(selector)

    print("Opening file to write to")
    with open("references-" + author_name.lower().replace(" ", "-") + ".html", "w", encoding='utf8') as f:
    #with open("resume.html", "w", encoding='ISO-8859-1') as f:
    #with open("resume.html", "w", encoding='cp1252') as f:

        citations = str(author['citedby'])
        hindex = str(author['hindex'])
        i10index = str(author['i10index'])

        print('Citations:', citations)
        f.write('Citations: ' + citations + "<br>")

        print('h-index:', hindex)
        f.write('h-index: ' + hindex + "<br>")

        print("i10-index:", i10index)
        f.write('i10-index: ' + i10index + "<br>")

        #print(author['publications'])
        #print('pub_year', 'authors', 'title', 'journal', 'publisher', 'volume', 'pages', 'pub_url', 'num_citations')
        #f.write('pub_year authors title journal publisher volume pages pub_url num_citations')
        impactfactorarr = {}
        print("Getting data from", len(author['publications']), "publications. Please wait...")
        for pub in author['publications']:
            publication = scholarly.fill(pub)

            authors = str(publication['bib']['author']) #.encode("windows-1252").decode("utf-8")
            authors = standandise_authors(authors)

            title = str(publication['bib']['title'])
            pub_year = ""
            if 'pub_year' in pub['bib']:
                pub_year = str(publication['bib']['pub_year'])
            else:
                print("Could not year for", title, ". Skipping...")
                continue

            journal = ""
            impactfactor = ""
            if 'journal' in pub['bib']:
                journal = str(publication['bib']['journal']).title()
                journal == journal if journal.strip().lower() != "null" else ""
                #journal == journal if journal != "Null" else ""

                a = "Comparative Biochemistry and Physiology A-Molecular & Integrative Physiology"
                c = "Comparative Biochemistry and Physiology C-Toxicology & Pharmacology"
                gscholarfixes = {
                    'Comparative Biochemistry And Physiology Part C: Toxicology & Pharmacology': c,
                    'Comparative Biochemistry And Physiology. Toxicology & Pharmacology: Cbp': c,
                    'Comparative Biochemistry And Physiology, Part C': c,
                    'Comparative Biochemistry And Physiology Part A: Molecular & Integrative Physiology': a,
                    'Comparative Biochemistry And Physiology-Part A: Molecular And Integrative Physiology': a,
                    'Comparative Biochemistry And Physiology, Part A': a,
                    'Proceedings Of The Royal Society B: Biological Sciences': "Proceedings Of The Royal Society B: Biological Sciences",
                    'Mar Biodivers': "Marine Biodiversity",
                    'Cell Stress And Chaperones': "Cell Stress & Chaperones"
                }
                if journal in gscholarfixes:
                    #print("Manual fixes: converting", journal, "to", gscholarfixes[journal])
                    journal = gscholarfixes[journal]

                #get journal impact factor
                key = journal.lower()
                if key in impactfactorarr:
                    impactfactor = impactfactorarr[key]
                    #print(journal, impactfactor, "stored")
                #elif journal != "Null":
                else:
                    await page.type(selector, journal)
                    #await asyncio.sleep(.5)
                    impactfactor = await page.evaluate('''() => Array.from(document.querySelectorAll('table.MuiTable-root tbody tr:first-child td:nth-child(2) p'), element => element.textContent)''')
                    if not impactfactor:
                        print("Could not get impact factor for journal:", journal)
                    else:
                        impactfactor = impactfactor[0]
                        #print(journal, impactfactor)
                    impactfactorarr[key] = impactfactor #store var in array (even if null to avoid searching a second time)
                    #https://stackoverflow.com/questions/52631057/how-to-delete-existing-text-from-input-using-puppeteer
                    for element in range(0, len(journal)):
                        await page.keyboard.press('Backspace')
                    #await asyncio.sleep(.5)
                impactfactor = "IF: "+impactfactor if impactfactor else ""

            #publisher = ""
            #if 'publisher' in pub['bib']:
            #    publisher = str(publication['bib']['publisher'].decode('utf-8'))
            volume = ""
            if 'volume' in pub['bib']:
                volume = str(publication['bib']['volume'])
            pages = ""
            if 'pages' in pub['bib']:
                pages = str(publication['bib']['pages'])
            pub_url = str(publication['pub_url'])
            num_citations = str(publication['num_citations'])
            num_citations = "C: "+num_citations if num_citations else ""


            reference = ""
            reference += authors
            reference += " (" + pub_year + ") "
            reference += title
            if journal:
                reference += " <em>" + journal + "</em> "
            reference += volume
            if pages:
                reference += ", " + pages + ". "
            reference += pub_url
            if num_citations:
                reference += " " + num_citations
            if impactfactor:
                reference += " " + impactfactor
            #print(reference)
            f.write("<p>" + reference + "</p>")

    await browser.close()

asyncio.get_event_loop().run_until_complete(main())
