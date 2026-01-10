import yfinance as yf
import pandas as pd
import numpy as np
import time
import os

# [핵심] 차트 그리기용 3개월 데이터 수집 함수
def fetch_price_history(candidates_df):
    print(f"📈 Fetching 3-month history charts for {len(candidates_df)} candidates...")
    histories = {}
    tickers = candidates_df['ticker'].tolist()
    if not tickers: return {}
    
    try:
        # yfinance로 3개월치 데이터 한방에 다운로드
        data = yf.download(tickers, period="3mo", interval="1d", group_by='ticker', auto_adjust=True, progress=False)
        
        for ticker in tickers:
            try:
                if len(tickers) == 1: hist_data = data['Close']
                else: hist_data = data[ticker]['Close']
                
                # NaN 제거 및 리스트 변환 (소수점 2자리)
                clean_hist = hist_data.dropna().tail(60).tolist()
                histories[ticker] = [round(x, 2) for x in clean_hist]
            except: histories[ticker] = []
    except: pass
    return histories

def get_technical_indicators(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="6mo")
        if len(hist) < 50: return None
        current_price = hist['Close'].iloc[-1]
        high_52w = hist['Close'].max()
        low_52w = hist['Close'].min()
        drop_rate = (current_price - high_52w) / high_52w
        recovery_rate = (current_price - low_52w) / low_52w
        
        # RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return {
            "ticker": ticker_symbol, "price": current_price,
            "high_52w": high_52w, "low_52w": low_52w,
            "drop_rate": drop_rate, "recovery_rate": recovery_rate,
            "rsi": rsi.iloc[-1]
        }
    except: return None

def run_scan(input_path="data/universe.csv", output_path="data/candidates_b.csv"):
    if not os.path.exists(input_path): return False
    df = pd.read_csv(input_path)
    tickers = df['ticker'].tolist()
    # tickers = tickers[:200] # 테스트할때만 주석해제

    print(f"🕵️ Module B: Scanning {len(tickers)} tickers...")
    candidates = []
    for i, ticker in enumerate(tickers):
        res = get_technical_indicators(ticker)
        if res and res['drop_rate'] < -0.20 and res['recovery_rate'] > 0.01:
            candidates.append(res)
        if (i+1)%100==0: time.sleep(0.1)

    if candidates:
        df_res = pd.DataFrame(candidates)
        # [중요] 여기서 차트 데이터 수집 함수 실행
        chart_data = fetch_price_history(df_res) 
        df_res['history'] = df_res['ticker'].map(chart_data).apply(lambda x: str(x) if x else "[]")
        
        df_res.to_csv(output_path, index=False)
        print(f"✅ Found {len(df_res)} candidates with charts.")
        return True
    return False

if __name__ == "__main__": run_scan()
