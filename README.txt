The goal of this project is to analyze and visualize data from
the Municipal Equality Index (MEI). The MEI is a 2013 report 
from the Human Rights Campaign (HRC) that scores 292 US municipalities 
on their policies regarding LGBT equality.

The data appears to contain some inconsistencies.
Each municipality profile contains some information that pertains
to the state as a whole. For example, the legality of same-sex marriage
is decided at the state level, not the municipal level. This information
should be the same for all municipalities within a state, but there are
some discrepancies. The script attempts to correct these errors.

Contents:
	Scripts/scrape_hrc.py
		Python script to extract the data from the HRC website
	HTML/profileXXX.html
		Profiles for 292 cities, numbered from 002 to 293, in HTML format.
		These are the raw HTML files that are downloaded from www.hrc.org
	Data/MEI.csv
		MEI data in CSV format (comma-separated values)
	Data/MEI_Codebook.csv
		Describes the columns in Data/MEI.csv
	Data/MEI-states.csv
		MEI data aggregated by state
	Data/MEI_States_Codebook.csv
		Describes the columns in Data/MEI-states.csv
	Data/MEI-errors.csv
		List of apparent inconsistencies in MEI data
	Data/MEI-revised.csv
		Corrected version of Data/MEI.csv with inconsistencies removed


