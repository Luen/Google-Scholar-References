import wikipedia
from bs4 import BeautifulSoup
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_impact_factor(journal_name):
    journal_name = journal_name+" (journal)"
    try:
        # Search for the page by journal name
        page = wikipedia.WikipediaPage(journal_name)
        
        # Access the content of the page
        html_content = page.html()
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the table row ('tr') where the 'th' (table header) contains the text 'Impact factor'
        impact_factor_row = soup.find('th', string='Impact factor')

        # Check if the row is found
        if impact_factor_row:
            # Get the next sibling 'td' which contains the impact factor
            impact_factor_data = impact_factor_row.find_next_sibling('td')
            if impact_factor_data:
                impact_factor_data_array = impact_factor_data.text.split(' ')
                impact_factor = impact_factor_data_array[0].strip()
                #year = impact_factor_data_array[1].strip().replace('(', '').replace(')', '')
                return impact_factor
            else:
                return "Impact factor not found."
        else:
            return "Impact factor row not found."
    except wikipedia.exceptions.PageError:
        return "Wikipedia page not found."
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple entries found, please specify: {e.options}"
    except Exception as e:
        return f"An error occurred: {e}"

# Example usage
journal_name = "Nature" # Replace with actual journal name
impact_factor = get_impact_factor(journal_name)
print(f"Impact Factor for {journal_name}: {impact_factor}")
impact_factor = get_impact_factor(journal_name)
print(f"Impact Factor for {journal_name}: {impact_factor}")