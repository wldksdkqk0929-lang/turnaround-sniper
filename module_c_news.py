import pandas as pd
import requests
import xml.etree.ElementTree as ET
import time
import os
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def get_google_news_data(ticker):
    # 구글 뉴스 RSS (7일간)
    url = f"https://news.google.com/rss/search?q={ticker}+stock+when:7d&hl=en-US&gl=US&ceid=US:en"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall('./channel/item')
            
            if not items:
                return "No recent news", "", 0
            
            # 최신 뉴스 1건만 집중 분석
            item = items[0]
            title = item.find('title').text
            link = item.find('link').text
            
            # 언론사 이름 제거 (깔끔하게)
            if "-" in title:
                title = title.split("-")[0].strip()
                
            return title, link, len(items)
            
    except Exception as e:
        return f"Error: {str(e)}", "", 0
    
    return "No Data", "", 0

def analyze_news(input_path="data/candidates_b.csv", output_path="data/candidates_c.csv"):
    if not os.path.exists(input_path):
        print("❌ Module C: Input file not found.")
        return False
        
    df = pd.read_csv(input_path)
    if df.empty:
        df.to_csv(output_path, index=False)
        return True

    # NLTK 감성분석기 준비 (최초 실행 시 데이터 다운로드)
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon', quiet=True)
    
    sia = SentimentIntensityAnalyzer()
    
    results = []
    risk_words = ['bankruptcy', 'chapter 11', 'delisting', 'fraud', 'investigation']

    print(f"🧠 Module C: AI Sentiment Analysis for {len(df)} stocks...")

    for i, row in df.iterrows():
        ticker = row['ticker']
        
        # 1. 뉴스 데이터 수집
        title, link, count = get_google_news_data(ticker)
        
        # 2. 리스크 키워드 1차 필터
        risk_found = False
        for risk in risk_words:
            if risk in title.lower():
                risk_found = True
                print(f"   🔻 Filtered {ticker}: Risk '{risk}' detected.")
                break
        
        if not risk_found:
            # 3. AI 감성 점수 계산 (-1.0 ~ +1.0)
            # 뉴스가 없으면 점수 0 (중립)
            if title == "No recent news" or title == "No Data":
                score = 0
            else:
                score = sia.polarity_scores(title)['compound']
            
            row['news_top'] = title
            row['news_link'] = link
            row['sentiment_score'] = score
            
            results.append(row)
            
            # 로그: 점수에 따라 이모지 다르게 표시
            emoji = "😐"
            if score > 0.3: emoji = "😊"
            elif score < -0.3: emoji = "😨"
            
            print(f"   [{ticker}] {emoji} Score: {score:.2f} | {title[:30]}...")
        
        time.sleep(0.3)

    pd.DataFrame(results).to_csv(output_path, index=False)
    print(f"✅ Module C: Analysis complete. {len(results)} stocks rated.")
    return True
