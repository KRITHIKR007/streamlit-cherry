from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import pandas as pd

class SentimentAnalyzer:
    def __init__(self, model_type="vader"):
        self.model_type = model_type
        if model_type == "vader":
            self.analyzer = SentimentIntensityAnalyzer()
        elif model_type == "bert":
            self.analyzer = pipeline("sentiment-analysis")

    def analyze_text(self, text):
        if self.model_type == "vader":
            scores = self.analyzer.polarity_scores(text)
            sentiment = "positive" if scores['compound'] > 0 \
                       else "negative" if scores['compound'] < 0 \
                       else "neutral"
            return {
                'sentiment': sentiment,
                'scores': scores
            }
        else:
            result = self.analyzer(text)[0]
            return {
                'sentiment': result['label'],
                'scores': {'score': result['score']}
            }

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
