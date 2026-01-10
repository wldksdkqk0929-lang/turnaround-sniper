import yfinance as yf
import pandas as pd
import numpy as np
import time
import os

# [핵심] 차트 데이터 수집 함수
def fetch_price_history(candidates_df):
    print(f"📈 Fetching charts for {len(candidates_df)} candidates...")
    histories = {}
    tickers = candidates_df['ticker'].tolist()
    if not tickers: return {}
    
    try:
        data = yf.download(tickers, period="3mo", interval="1d", group_by='ticker', auto_adjust=True, progress=False)
        for ticker in tickers:
            try:
                if len(tickers) == 1: hist_data = data['Close']
                else: hist_data = data[ticker]['Close']
                
                # NaN 제거 및 리스트 변환 (최근 60일)
                clean_hist = hist_data.dropna().tail(60).tolist()
                
                # [데이터 검증] 차트 데이터가 너무 짧으면(10일 미만) 제외
                if len(clean_hist) < 10:
                    histories[ticker] = []
                else:
                    histories[ticker] = [round(x, 2) for x in clean_hist]
            except: histories[ticker] = []
    except: pass
    return histories

def get_technical_indicators(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        # 6개월치 데이터 가져오기
        hist = ticker.history(period="6mo")
        
        if len(hist) < 50: return None
            
        current_price = hist['Close'].iloc[-1]
        
        # [필터 1] "동전주(Penny Stock)" 제거 
        # 이유: 2달러 미만은 주식 병합 장난질이 너무 심함
        if current_price < 2.0: 
            return None

        high_52w = hist['Close'].max()
        low_52w = hist['Close'].min()
        
        # 낙폭 계산
        drop_rate = (current_price - high_52w) / high_52w
        # 반등폭 계산
        recovery_rate = (current_price - low_52w) / low_52w
        
        # [필터 2] "가짜 급등(Split Error)" 제거
        # 이유: 바닥 대비 200%(3배) 이상 오른 건 스나이퍼 타겟이 아니라 이미 과열/오류임
        if recovery_rate > 2.0:
            return None

        # RSI 계산
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return {
            "ticker": ticker_symbol,
            "price": current_price,
            "high_52w": high_52w,
            "low_52w": low_52w,
            "drop_rate": drop_rate,
            "recovery_rate": recovery_rate,
            "rsi": rsi.iloc[-1]
        }

    except Exception:
        return None

def run_scan(input_path="data/universe.csv", output_path="data/candidates_b.csv"):
    if not os.path.exists(input_path): return False
        
    df = pd.read_csv(input_path)
    tickers = df['ticker'].tolist()
    # tickers = tickers[:200] # 테스트할 때만 주석 해제

    print(f"🕵️ Precision Scanning {len(tickers)} tickers (Filtering Fake Pumps)...")

    candidates = []
    for i, ticker in enumerate(tickers):
        result = get_technical_indicators(ticker)
        
        if result:
            # [조건] 
            # 1. 고점 대비 -20% 이상 빠진 놈 (낙폭 과대)
            # 2. 바닥 대비 +5% 이상 반등한 놈 (추세 전환 시작)
            if result['drop_rate'] < -0.20 and result['recovery_rate'] > 0.05:
                 candidates.append(result)
        
        if (i+1) % 100 == 0:
            time.sleep(0.1)

    if candidates:
        candidates_df = pd.DataFrame(candidates)
        
        # 차트 데이터 수집
        chart_data = fetch_price_history(candidates_df)
        
        # 차트 데이터가 없는 놈은 탈락시킴
        candidates_df['history'] = candidates_df['ticker'].map(chart_data)
        candidates_df = candidates_df[candidates_df['history'].map(lambda d: len(d) > 0 if d else False)]
        
        # 문자열로 변환하여 저장
        candidates_df['history'] = candidates_df['history'].apply(str)

        candidates_df.to_csv(output_path, index=False)
        print(f"✅ Scan Complete. {len(candidates_df)} Valid Targets Found.")
        return True
    else:
        print("⚠️ No candidates found.")
        return False

if __name__ == "__main__":
    run_scan()
