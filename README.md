# Elitiscraper
## Overview
Singapore's eLitigation provides all written judgments issued by the Supreme Court of Singapore since 2000. This scraper pulls information from all cases found within 

This code can be modified to search for specific areas of law based on the catchword or specific keywords as found in the full judgment. See <a href="https://github.com/kevanwee/crimewatch">this repo</a> for an implementation of this code that strictly searches for criminal cases.

## Methodology
This project utilizes a **web scraper** built with `BeautifulSoup` to extract all reported judgments from **eLitigation**. The scraped data is then processed and analyzed using statistical methods to identify trends, patterns, and other insights related to case law in Singapore. 

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/kevanwee/elitiscraper.git
   ```
2. Navigate to the project directory:
   ```sh
   cd elitiscraper
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
Run the main script to scrape data and generate statistical reports:
```sh
python elitiscrape.py
```
