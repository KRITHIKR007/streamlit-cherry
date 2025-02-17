import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
import time
import random

class ReviewCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = "https://www.amazon.com/product-reviews/{product_id}/ref=cm_cr_arp_d_paging_btm_next_{page}?pageNumber={page}"
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_amazon_reviews(self, product_id, max_pages=5, max_retries=3):
        reviews_data = []
        
        for page in range(1, max_pages + 1):
            url = self.base_url.format(product_id=product_id, page=page)
            retries = 0
            while retries < max_retries:
                try:
                    time.sleep(2)
                    response = requests.get(url, headers=self.headers, timeout=10)  # Add timeout
                    response.raise_for_status()  # Raise exception for bad status codes
                    soup = BeautifulSoup(response.content, 'html.parser')
                    reviews = soup.find_all('div', {'data-hook': 'review'})
                    
                    for review in reviews:
                        review_text = review.find('span', {'data-hook': 'review-body'})
                        review_date = review.find('span', {'data-hook': 'review-date'})
                        
                        if review_text and review_date:
                            reviews_data.append({
                                'review_text': review_text.text.strip(),
                                'date': datetime.strptime(
                                    review_date.text.split('on ')[-1], 
                                    '%B %d, %Y'
                                ),
                                'category': self.get_product_category(soup)
                            })
                    break  # Success, exit retry loop
                except requests.RequestException as e:
                    retries += 1
                    if retries == max_retries:
                        self.logger.error(f"Failed to fetch page {page} after {max_retries} attempts: {e}")
                    else:
                        time.sleep(retries * 2)  # Exponential backoff
                        continue
                
                # Add delay to avoid rate limiting
                time.sleep(random.uniform(1, 2))
        
        return pd.DataFrame(reviews_data)

    def get_product_category(self, soup):
        """Extract product category from page"""
        try:
            category = soup.find("a", {"class": "a-link-normal a-color-tertiary"})
            return category.text.strip() if category else "Unknown"
        except:
            return "Unknown"

    def save_reviews(self, reviews_df, output_path):
        reviews_df.to_csv(output_path, index=False)
