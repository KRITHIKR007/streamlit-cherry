from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import logging

class SentimentAnalyzer:
    def __init__(self, model_type="vader"):
        self.model_type = model_type
        if model_type == "vader":
            self.analyzer = SentimentIntensityAnalyzer()
        elif model_type == "bert":
            try:
                from transformers import pipeline
                self.analyzer = pipeline("sentiment-analysis")
            except Exception as e:
                logging.warning(f"Failed to load BERT model: {e}. Falling back to VADER.")
                self.model_type = "vader"
                self.analyzer = SentimentIntensityAnalyzer()

    def analyze_text(self, text):
        if self.model_type == "vader":
            scores = self.analyzer.polarity_scores(text)
            sentiment = self._get_vader_sentiment(scores['compound'])
            return {
                'sentiment': sentiment,
                'scores': scores
            }
        else:
            try:
                result = self.analyzer(text)[0]
                sentiment = result['label'].lower()
                return {
                    'sentiment': 'positive' if sentiment == 'positive' else 'negative',
                    'scores': {'score': result['score']}
                }
            except Exception as e:
                logging.error(f"BERT analysis failed: {e}. Falling back to VADER.")
                self.model_type = "vader"
                self.analyzer = SentimentIntensityAnalyzer()
                return self.analyze_text(text)

    def _get_vader_sentiment(self, compound_score):
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'

    def analyze_batch(self, texts):
        sentiments = []
        scores = []
        
        for text in texts:
            result = self.analyze_text(text)
            sentiments.append(result['sentiment'])
            scores.append(result['scores'])
            
        return pd.DataFrame({
            'sentiment': sentiments,
            'scores': scores
        })
