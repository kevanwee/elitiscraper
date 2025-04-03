import time
import requests
from bs4 import BeautifulSoup
from ftfy import fix_text
import pandas as pd
from tqdm import tqdm

class SingaporeLawScraper:
    def __init__(self):
        self.base_list_url = "https://www.elitigation.sg/gd/Home/Index"
        self.base_case_url = "https://www.elitigation.sg/gd/s/"

    def scrape_elitigation_cases(self, start_year, end_year):
        all_cases = []
        output_file_name = f"elitigation_cases_{start_year}_to_{end_year}.csv"

        with tqdm(desc="Scraping cases", unit="case") as pbar:
            for year in range(start_year, end_year + 1):
                page_num = 1
                while True:
                    list_url = f"{self.base_list_url}?Filter=SUPCT&YearOfDecision={year}&SortBy=Score&CurrentPage={page_num}"
                    response = requests.get(list_url)
                    
                    if response.status_code != 200:
                        break

                    soup = BeautifulSoup(response.text, 'html.parser')
                    cards = soup.find_all('div', class_='card col-12')
                    
                    if not cards:
                        break

                    for card in cards:
                        case_identifier_span = card.find('span', class_='gd-addinfo-text')
                        if case_identifier_span:
                            case_identifier = fix_text(case_identifier_span.text.strip().replace(" |", ""))
                            catchwords_links = card.find_all('a', class_='gd-cw')
                            catchwords_texts = [
                                fix_text(link.text.strip().replace("â€”", "-").replace("[", "").replace("]", ""))
                                for link in catchwords_links
                            ]
                            
                            formatted_case_identifier = (
                                case_identifier.replace(" ", "_")
                                               .replace("[", "")
                                               .replace("]", "")
                                               .replace("(", "")
                                               .replace(")", "")
                            )
                            case_url = f"{self.base_case_url}{formatted_case_identifier}"
                            
                            case_details = self.scrape_case_details(case_url)
                            
                            if case_details:
                                all_cases.append({
                                    'CaseIdentifier': case_identifier,
                                    'Catchwords': ", ".join(catchwords_texts) if catchwords_texts else None,
                                    'Year': year,
                                    'URL': case_url,
                                    **case_details
                                })
                                pbar.update(1)
                                pbar.set_postfix_str(f"Year: {year}, Page: {page_num}", refresh=False)

                    page_num += 1
                    time.sleep(0.5)

        pd.DataFrame(all_cases).to_csv(output_file_name, index=False)
        print(f"\nSaved all cases to {output_file_name}")
        return output_file_name

    def scrape_case_details(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # paragraph count handling
        judgment_divs = soup.find_all('div', class_='Judg-1')
        paragraph_count = 0
        if judgment_divs:
            last_paragraph = fix_text(judgment_divs[-1].text.strip())
            if last_paragraph:
                first_word = last_paragraph.split()[0] if last_paragraph.split() else ''
                paragraph_count = int(first_word) if first_word.isdigit() else 0

        # word count calculation
        full_text = " ".join(fix_text(div.text) for div in judgment_divs)
        word_count = len(full_text.split())

        # judge name cleaning
        judge_div = soup.find('div', class_='Judg-Author') or soup.find('div', class_='Judg-Sign')
        judge_raw = fix_text(judge_div.text.strip()) if judge_div else "Unknown"
        judge_cleaned = (
            judge_raw.replace("Â", "")
                     .replace(":", "")
                     .split("(delivering")[0]
                     .strip()
        )

        # counsels
        lawyers_divs = soup.find_all('div', class_='Judg-Lawyers')
        legal_parties_text = []
        
        if lawyers_divs:
            for div in lawyers_divs:
                legal_parties_text.append(fix_text(div.text.strip()))
            
            last_lawyer_div = lawyers_divs[-1]
            current_element = last_lawyer_div.next_sibling
            
            while current_element:
                if hasattr(current_element, 'name') and current_element.name == 'div':
                    if 'class' in current_element.attrs:
                        if 'Judg-EOF' in current_element.get('class', []):
                            break
                        elif 'txt-body' in current_element.get('class', []):
                            legal_parties_text.append(fix_text(current_element.text.strip()))
                
                current_element = current_element.next_sibling
        
        legal_parties_cleaned = " ".join(legal_parties_text).replace(";", "").strip()

        return {
            'WordCount': word_count,
            'ParagraphCount': paragraph_count,
            'Author': judge_cleaned,
            'LegalParties': legal_parties_cleaned if legal_parties_cleaned else "Not found"
        }

if __name__ == "__main__":
    scraper = SingaporeLawScraper()
    scraper.scrape_elitigation_cases(start_year=2020, end_year=2025)
