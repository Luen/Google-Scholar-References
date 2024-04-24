# Google Scholar References
A python script for personal-use that generates references in a format for a resume/curriculum vitae for professors / academics / scholars including the journal's impact factor (IF).

See also Zotera, an open source citation manager

# Install
- Download this git repository
- Install [Python](https://www.python.org/downloads/)
- Install [scholarly](https://github.com/scholarly-python-package/scholarly) and [wikipedia](https://github.com/goldsmith/Wikipedia) `pip install -r requirements.txt`
- Run the script by passing your Google Scholar name in as a command line argument `python references.py --name "John Smith"`
- Examine the output and edit the script if necessary

# Example output

Example output for [Jodie L. Rummer](http://scholar.google.com.au/citations?user=ynWS968AAAAJ&hl=en)

`python references.py --name "Jodie Rummer"`

Outputs file references-jodie-rummer.html in the following format. Here's a snippet:

Citations: 2695
h-index: 29
i10-index: 55

Heinrich, D. , Dhellemmes, F. , Guttridge, T. L. , Smukall, M. , Brown, C. , Rummer, J. , Gruber, S. , Huveneers, C. (2021) Short-term impacts of daily feeding on the residency, distribution and energy expenditure of sharks *Animal Behaviour* 172, 55-71. https://www.sciencedirect.com/science/article/pii/S0003347220303535 C: 1 IF: 2.689

Johansen, J. L. , Nadler, L. E. , Habary, A. , Bowden, A. J. , Rummer, J. (2021) Thermal acclimation of tropical coral reef fishes to global heat waves *Elife* 10, e59162. https://elifesciences.org/articles/59162 C: 0 IF: 7.080

Wheeler, C. R. , Rummer, J. L. , Bailey, B. , Lockwood, J. , Vance, S. , Mandelman, J. W. (2021) Future thermal regimes for epaulette sharks (Hemiscyllium ocellatum): growth and metabolic performance cease to be optimal *Scientific Reports* 11, 1-12. https://www.nature.com/articles/s41598-020-79953-0 C: 0 IF: 3.998

Cinner, J. E. , Pratchett, M. S. , Graham, N. A. J. , Messmer, V. , Fuentes, M. M. P. B. , Ainsworth, T. , Ban, N. , Bay, L. K. , Blythe, J. , Dissard, D. , Dunn, S. , Evans, L. , Fabinyi, M. , Fidelman, P. , Figueiredo, J. , Frisch, A. J. , Fulton, C. J. , Hicks, C. C. , Lukoschek, V. , Mallela, J. , Moya, A. , Penin, L. , Rummer, J. L. , Walker, S. , Williamson, D. H. (2016) A framework for understanding climate change impacts on coral reef social–ecological systems *Regional Environmental Change* 16, 1133-1146. https://link.springer.com/article/10.1007%252Fs10113-015-0832-z C: 47 IF: 3.481

Heinrich, D. D. , Watson, S. , Rummer, J. L. , Brandl, S. J. , Simpfendorfer, C. A. , Heupel, M. R. , Munday, P. L. (2016) Foraging behaviour of the epaulette shark Hemiscyllium ocellatum is not affected by elevated CO2 Ices *Journal Of Marine Science* 73, 633-640. https://academic.oup.com/icesjms/article-abstract/73/3/633/2458696 C: 41 IF: 3.188

Rummer, J. L. , Binning, S. A. , Roche, D. G. , Johansen, J. L. (2016) Methods matter: considering locomotory mode and respirometry technique when estimating metabolic rates of fishes *Conservation Physiology* 4, . https://academic.oup.com/conphys/article-abstract/4/1/cow008/2951329 C: 48 IF: 2.570


# Notes
- Journal impact factors from https://journal-if.com/
- Journal impact factors are found on (search "[journal impact factor by JCR](https://jcr.clarivate.com/)" or "[journal impact factor Clarivate Analytics](https://clarivate.com/webofsciencegroup/essays/impact-factor/)") and would need ot save the data every year or scrape on run. Requires log in credentials.


# Set up
```
virtualenv venv
.\venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
```