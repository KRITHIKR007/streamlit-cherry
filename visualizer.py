import matplotlib.pyplot as plt
# Remove seaborn style
# plt.style.use('seaborn')  # Remove this line
from wordcloud import WordCloud
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

class SentimentVisualizer:
    def __init__(self):
        # Use a built-in matplotlib style instead
        plt.style.use('default')  # or try 'classic', 'bmh', 'ggplot'

    def create_wordcloud(self, texts, sentiment_filter=None):
        """Generate word cloud from texts"""
        plt.clf()  # Clear current figure
        combined_text = ' '.join(texts)
        wordcloud = WordCloud(width=800, height=400,
                            background_color='white').generate(combined_text)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        fig = plt.gcf()
        plt.close()  # Close the figure to free memory
        return fig

    def plot_sentiment_trends(self, df):
        """Plot sentiment trends over time"""
        df['date'] = pd.to_datetime(df['date'])
        daily_sentiments = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
        
        fig = go.Figure()
        for sentiment in daily_sentiments.columns:
            fig.add_trace(go.Scatter(
                x=daily_sentiments.index,
                y=daily_sentiments[sentiment],
                name=sentiment,
                mode='lines+markers'
            ))
        
        fig.update_layout(
            title='Sentiment Trends Over Time',
            xaxis_title='Date',
            yaxis_title='Number of Reviews',
            hovermode='x unified'
        )
        return fig

    def create_category_analysis(self, df):
        """Create category-wise sentiment analysis"""
        if 'category' in df.columns:
            cat_sentiment = pd.crosstab(df['category'], df['sentiment'])
            fig = px.bar(cat_sentiment,
                        title='Category-wise Sentiment Distribution',
                        barmode='group')
            return fig
        return None

    def sentiment_distribution(self, df):
        """Create sentiment distribution pie chart"""
        sentiment_counts = df['sentiment'].value_counts()
        colors = {'positive': 'green', 'negative': 'red', 'neutral': 'blue'}
        
        fig = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            marker_colors=[colors[s] for s in sentiment_counts.index]
        )])
        
        fig.update_layout(title='Overall Sentiment Distribution')
        return fig
