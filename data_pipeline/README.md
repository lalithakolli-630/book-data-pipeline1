# Data Pipeline

## Overview

This module implements a complete data pipeline using data scraped from books.toscrape.com.

The pipeline follows:

Scrape → Clean → Convert → Store → Query → Analyze

## Data Source

Data was scraped from books.toscrape.com using Python requests and BeautifulSoup.

The final dataset contains 69 books across 3 categories.

## Data Cleaning

The scraped price was converted into a float column named price_gbp.

Star ratings were converted from text values such as One, Two, Three, Four and Five into integers from 1 to 5.

Availability was converted into the Boolean column in_stock.

The scraped data was checked for parsing failures and missing values.

## Currency Conversion

The project uses the required fixed conversion rate:

1 GBP = 105.50 INR

This is a project-defined fixed baseline and does not use an external currency API.

The converted value is stored in price_inr.

## Database

A normalized SQLite database was created with two related tables:

### categories

- category_id - Primary Key
- category_name - Unique

### books

- book_id - Primary Key
- title
- price_gbp
- price_inr
- rating
- in_stock
- category_id - Foreign Key referencing categories

## SQL Analysis

Five SQL queries were executed.

The queries demonstrate:

- SELECT
- WHERE
- ORDER BY
- LIMIT
- DISTINCT
- IN
- BETWEEN
- JOIN

The SQL query outputs are shown in the executed Colab notebook.

## Pandas Analysis

SQL query results were read into pandas using pd.read_sql().

The JOIN query was independently reproduced using pandas.merge().

The SQL JOIN and pandas merge results were compared and verified to be equivalent.

## How to Run

Install the required packages:

pip install requests beautifulsoup4 pandas

Open the notebook in Google Colab or Jupyter Notebook and run the cells from top to bottom.
## Validation

The final pipeline produced 69 book records across 3 book categories.

The database contains the normalized categories and books tables with a primary-key/foreign-key relationship.
