import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
import time

class ReviewCollector:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_amazon_reviews(self, product_id, max_pages=5, max_retries=3):
        reviews = []
        base_url = f"https://www.amazon.com/product-reviews/{product_id}"
        
        for page in range(1, max_pages + 1):
            retries = 0
            while retries < max_retries:
                try:
                    time.sleep(2)
                    response = requests.get(f"{base_url}?pageNumber={page}", 
                                         headers=self.headers, 
                                         timeout=10)  # Add timeout
                    response.raise_for_status()  # Raise exception for bad status codes
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    review_elements = soup.find_all("div", {"data-hook": "review"})
                    
                    for review in review_elements:
                        review_text = review.find("span", {"data-hook": "review-body"})
                        review_date = review.find("span", {"data-hook": "review-date"})
                        
                        if review_text and review_date:
                            reviews.append({
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
                
        return pd.DataFrame(reviews)

    def get_product_category(self, soup):
        """Extract product category from page"""
        try:
            category = soup.find("a", {"class": "a-link-normal a-color-tertiary"})
            return category.text.strip() if category else "Unknown"
        except:
            return "Unknown"

    def save_reviews(self, reviews_df, output_path):
        reviews_df.to_csv(output_path, index=False)
