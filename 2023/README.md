# Muncipal Equality Index (2023)

This directory contains the data behind the Municipal Equality Index for 2023.
It does not include point totals -- you will have to compute them yourself.
The Python code to scrape the data from the HRC website will be added soon.

The CSV file `mei-data-2023.csv` contains the following columns:
- `Row Id`: A unique identifier for each row.
- `City Id`: A unique identifier for each city.
- `City`: The name of the city.
- `State`: The state in which the city is located (two-letter abbreviation).
- `URL`: The URL of the city's MEI report.
- `Category`: The category of the city's MEI report. Possible values are `Non-Discrimination Laws`, `Municipality as Employer`, `Municipal Services`, `Law Enforcement`, and `Leadership on LGBTQ+ Equality`.
- `Criterion`: The criterion within the category.
- `Level of government`: The level of government responsible for the criterion. Possible values are `City`, `County`, and `State`.
- `Orientation/Identity`: Possible values are `Sexual Orientation`, `Gender Identity`, and `NA`.
- `Score`: The city's score for the criterion.

