
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_collector import ReviewCollector
from preprocessor import TextPreprocessor
from sentiment_analyzer import SentimentAnalyzer
import requests
import sys
from visualizer import SentimentVisualizer
import re

class Config:
    SENTIMENT_COLORS = {
        'positive': 'green',
        'negative': 'red',
        'neutral': 'blue'
    }
    MAX_PAGES_LIMIT = 10
    DEFAULT_PAGES = 5

def set_page_config():
    st.set_page_config(
        page_title="Sentiment Analysis Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def sidebar_config():
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/100/sentiment-analysis.png", width=100)
        st.title("Settings")
        
        model_type = st.selectbox(
            "Select Model",
            ["VADER (Fast)", "BERT (Accurate)"],
            help="VADER is faster but BERT might be more accurate"
        )
        
        st.divider()
        
        st.markdown("### About")
        st.info("""
        This tool analyzes sentiment in product reviews using AI.
        - 📊 Analyze single reviews
        - 🔍 Bulk analyze Amazon products
        - 📈 View detailed visualizations
        """)
        
        return "vader" if "VADER" in model_type else "bert"

def display_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 E-commerce Sentiment Analysis")
        st.markdown("Analyze product reviews and understand customer sentiment")
    with col2:
        if not check_internet_connection():
            st.error("⚠️ No Internet Connection")
        else:
            st.success("✅ Connected")

def single_review_analysis(preprocessor, analyzer):
    with st.expander("Review Analysis Options", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            review = st.text_area(
                "Enter your review",
                placeholder="Type or paste your review here...",
                height=150
            )
        with col2:
            st.markdown("### Options")
            show_details = st.checkbox("Show detailed scores", value=True)
            show_preprocessing = st.checkbox("Show preprocessing steps")
            
        analyze_button = st.button("🔍 Analyze Review", use_container_width=True)
        
        if analyze_button:
            if not review:
                st.warning("⚠️ Please enter a review text")
            else:
                with st.spinner("🔄 Analyzing..."):
                    # Show preprocessing if selected
                    if show_preprocessing:
                        with st.expander("Preprocessing Steps", expanded=True):
                            st.code(review, language="text")
                            processed_text = preprocessor.preprocess(review)
                            st.code(processed_text, language="text")
                    else:
                        processed_text = preprocessor.preprocess(review)
                    
                    result = analyzer.analyze_text(processed_text)
                    
                    # Display results
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown("### Sentiment Result")
                        sentiment = result['sentiment'].upper()
                        color = Config.SENTIMENT_COLORS[result['sentiment']]
                        st.markdown(f"<h2 style='color: {color};'>{sentiment}</h2>", 
                                  unsafe_allow_html=True)
                    
                    if show_details:
                        with col2:
                            st.markdown("### Detailed Scores")
                            for score_type, value in result['scores'].items():
                                st.metric(score_type.title(), f"{value:.2f}")

def amazon_product_analysis(collector, preprocessor, analyzer, visualizer):
    with st.expander("Amazon Product Analysis", expanded=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            product_id = st.text_input(
                "Amazon Product ID",
                placeholder="Enter 10-character product ID...",
                help="Find this in the Amazon product URL"
            )
        with col2:
            max_pages = st.slider(
                "Pages to analyze",
                1, Config.MAX_PAGES_LIMIT,
                Config.DEFAULT_PAGES,
                help="More pages = more reviews but slower analysis"
            )
        
        analyze_button = st.button("📊 Analyze Product Reviews", use_container_width=True)
        
        if analyze_button:
            if not validate_product_id(product_id):
                st.warning("⚠️ Please enter a valid 10-character Amazon product ID")
            else:
                with st.spinner("🔄 Fetching and analyzing reviews..."):
                    try:
                        reviews_df = collector.get_amazon_reviews(product_id, max_pages)
                        
                        if reviews_df.empty:
                            st.error("No reviews found for this product ID")
                            return
                        
                        # Progress bar for analysis
                        progress_bar = st.progress(0)
                        reviews_df = analyze_reviews(reviews_df, preprocessor, analyzer)
                        progress_bar.progress(100)
                        
                        # Display results in tabs
                        tab1, tab2, tab3, tab4 = st.tabs([
                            "📊 Overview",
                            "📈 Trends",
                            "☁️ Word Clouds",
                            "🔍 Details"
                        ])
                        
                        with tab1:
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.plotly_chart(
                                    visualizer.sentiment_distribution(reviews_df),
                                    use_container_width=True
                                )
                            with col2:
                                st.markdown("### Summary Statistics")
                                counts = reviews_df['sentiment'].value_counts()
                                total = len(reviews_df)
                                for sent, count in counts.items():
                                    st.metric(
                                        sent.title(),
                                        f"{count} reviews",
                                        f"{count/total*100:.1f}%"
                                    )
                        
                        with tab2:
                            st.plotly_chart(
                                visualizer.plot_sentiment_trends(reviews_df),
                                use_container_width=True
                            )
                        
                        with tab3:
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                sentiment_option = st.selectbox(
                                    "Select Sentiment",
                                    ["All", "Positive", "Negative", "Neutral"]
                                )
                            with col2:
                                filtered_texts = reviews_df['review_text']
                                if sentiment_option != "All":
                                    filtered_texts = reviews_df[
                                        reviews_df['sentiment'] == sentiment_option.lower()
                                    ]['review_text']
                                
                                if not filtered_texts.empty:
                                    st.pyplot(visualizer.create_wordcloud(filtered_texts))
                                else:
                                    st.warning(f"No {sentiment_option.lower()} reviews found")
                        
                        with tab4:
                            st.dataframe(
                                reviews_df[['review_text', 'sentiment', 'date']],
                                use_container_width=True
                            )
                    
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")

def check_internet_connection():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False

def analyze_reviews(reviews_df, preprocessor, analyzer):
    """Helper function to analyze reviews"""
    processed_texts = reviews_df['review_text'].apply(preprocessor.preprocess)
    sentiments = []
    
    for text in processed_texts:
        result = analyzer.analyze_text(text)
        sentiments.append(result['sentiment'])
    
    reviews_df['sentiment'] = sentiments
    return reviews_df

def validate_product_id(product_id):
    """Validate Amazon product ID format"""
    if not product_id:
        return False
    # Basic format check for Amazon product IDs
    return bool(re.match(r'^[A-Z0-9]{10}$', product_id))

def main():
    set_page_config()
    model_type = sidebar_config()
    display_header()
    
    try:
        # Initialize components
        collector = ReviewCollector()
        preprocessor = TextPreprocessor()
        analyzer = SentimentAnalyzer(model_type=model_type)
        visualizer = SentimentVisualizer()
        
        # Main content area
        tab1, tab2 = st.tabs(["📝 Single Review", "🔍 Amazon Product"])
        
        with tab1:
            single_review_analysis(preprocessor, analyzer)
            
        with tab2:
            amazon_product_analysis(collector, preprocessor, analyzer, visualizer)
            
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.warning("Please try restarting the application")

if __name__ == "__main__":
    main()
