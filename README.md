# E-commerce Sentiment Analysis

A Python-based sentiment analysis tool for analyzing e-commerce product reviews using VADER and BERT models.

## Features

- **Dual Model Support**:
  - VADER (default) - Fast and accurate for social media text
  - BERT - Deep learning based for more nuanced analysis

- **Multiple Input Methods**:
  - Single review analysis
  - Bulk analysis using Amazon product IDs
  - CSV file support for batch processing

- **Text Preprocessing**:
  - Lowercase conversion
  - Special character removal
  - Stop word elimination
  - Lemmatization
  - Tokenization

- **Visualization**:
  - Sentiment distribution pie charts
  - Score breakdown for individual reviews

## How to Use

1. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Running the Application**:
   ```bash
   streamlit run app.py
   ```

3. **Usage Options**:
   - **Single Review Analysis**:
     1. Select "Single Review" option
     2. Enter your review text
     3. Click "Analyze"

   - **Amazon Product Reviews**:
     1. Select "Amazon Product ID" option
     2. Enter the product ID from Amazon URL
     3. Click "Fetch and Analyze"

## Components

1. **Sentiment Analyzer (`sentiment_analyzer.py`)**:
   - Implements both VADER and BERT models
   - Provides sentiment scores and classifications
   - Supports batch processing

2. **Text Preprocessor (`preprocessor.py`)**:
   - Cleans and normalizes text data
   - Removes noise and irrelevant information
   - Prepares text for analysis

3. **Data Collector (`data_collector.py`)**:
   - Scrapes reviews from Amazon
   - Handles pagination and error recovery
   - Saves data in structured format

4. **Web Interface (`app.py`)**:
   - Streamlit-based user interface
   - Interactive analysis options
   - Visual result presentation

## Technical Details

- **VADER Sentiment Analysis**:
  - Rule-based analysis
  - Optimized for social media text
  - Returns compound, positive, negative, and neutral scores

- **BERT Model**:
  - Transformer-based deep learning
  - Context-aware analysis
  - Higher accuracy for complex sentences

## Requirements

- Python 3.7+
- See `requirements.txt` for complete package list

## Limitations

- Amazon review scraping may be affected by website changes
- BERT model requires more computational resources
- Internet connection needed for Amazon review collection

## Error Handling

- Graceful failure for network issues
- Input validation for all user entries
- Clear error messages and recovery options
