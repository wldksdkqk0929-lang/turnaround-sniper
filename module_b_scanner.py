import yfinance as yf
import pandas as pd
import numpy as np
import time
import os

def get_technical_indicators(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        # 최근 6개월 데이터 가져오기 (이동평균선 계산용)
        hist = ticker.history(period="6mo")
        
        if len(hist) < 50: # 데이터가 너무 적으면 패스
            return None
            
        current_price = hist['Close'].iloc[-1]
        
        # 52주 최고/최저 (yfinance info가 느려서 history에서 계산)
        high_52w = hist['Close'].max()
        low_52w = hist['Close'].min()
        
        # 낙폭 계산 (고점 대비 현재가)
        drop_rate = (current_price - high_52w) / high_52w

        # 반등폭 계산 (저점 대비 현재가)
        recovery_rate = (current_price - low_52w) / low_52w

        # 기술적 지표: RSI (14일)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]

        # 기술적 지표: 이동평균선 (20일, 50일)
        ma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        ma50 = hist['Close'].rolling(window=50).mean().iloc[-1]

        return {
            "ticker": ticker_symbol,
            "price": current_price,
            "high_52w": high_52w, # 정확한 고점
            "low_52w": low_52w,   # 정확한 저점
            "drop_rate": drop_rate,
            "recovery_rate": recovery_rate,
            "rsi": current_rsi,
            "ma20": ma20,
            "ma50": ma50
            # 'history'는 여기서 안 구함 (속도 저하 방지)
        }

    except Exception as e:
        # print(f"Error checking {ticker_symbol}: {e}") # 에러 로그 너무 많으면 주석 처리
        return None

# [신규 기능] 최종 후보들의 차트용 과거 데이터 수집 함수
def fetch_price_history(candidates_df):
    print(f"📈 Fetching 3-month history charts for {len(candidates_df)} candidates...")
    histories = {}
    
    # yfinance 배치 다운로드로 속도 향상
    tickers = candidates_df['ticker'].tolist()
    if not tickers: return {}
    
    try:
        # 최근 3개월 데이터 한 번에 요청
        data = yf.download(tickers, period="3mo", interval="1d", group_by='ticker', auto_adjust=True, progress=False)
        
        for ticker in tickers:
            try:
                # 단일 종목일 경우와 다중 종목일 경우 데이터 구조가 다름
                if len(tickers) == 1:
                    hist_data = data['Close']
                else:
                    hist_data = data[ticker]['Close']
                
                # NaN 값 제거 및 리스트로 변환 (최근 60개 정도만 사용)
                clean_hist = hist_data.dropna().tail(60).tolist()
                # 소수점 2자리로 통일
                histories[ticker] = [round(x, 2) for x in clean_hist]
                
            except Exception as e: 
                print(f"   ⚠️ Chart data error for {ticker}: {e}")
                histories[ticker] = []
                
    except Exception as e:
         print(f"❌ Batch download failed: {e}")

    return histories

def run_scan(input_path="data/universe.csv", output_path="data/candidates_b.csv"):
    if not os.path.exists(input_path):
        print("❌ Module B: Universe file not found.")
        return False
        
    df = pd.read_csv(input_path)
    tickers = df['ticker'].tolist()
    # 테스트용으로 줄일 때는 아래 주석 해제
    # tickers = tickers[:200] 
    
    print(f"🕵️ Module B: Scanning {len(tickers)} tickers for Turnaround Signals...")

    candidates = []
    # 1차 필터링 (기술적 지표)
    for i, ticker in enumerate(tickers):
        result = get_technical_indicators(ticker)
        if result:
            # 필터링 조건: 고점 대비 -20% 이상 하락했고, 바닥에서 조금이라도 반등한 놈
            if result['drop_rate'] < -0.20 and result['recovery_rate'] > 0.01:
                 candidates.append(result)
        
        if (i+1) % 100 == 0:
            print(f"   Progress: {i+1}/{len(tickers)} checked...")
            time.sleep(0.5)

    # 결과 저장 및 2차 데이터(히스토리) 수집
    if candidates:
        candidates_df = pd.DataFrame(candidates)
        
        # [핵심 추가] 최종 후보들의 차트 데이터 수집
        chart_data = fetch_price_history(candidates_df)
        # 데이터프레임에 'history' 컬럼 추가 (문자열 형태로 저장)
        candidates_df['history'] = candidates_df['ticker'].map(chart_data).apply(lambda x: str(x) if x else "[]")

        candidates_df.to_csv(output_path, index=False)
        print(f"✅ Module B: Scan complete. {len(candidates_df)} candidates found with charts.")
        return True
    else:
        print("⚠️ Module B: No candidates found.")
        pd.DataFrame(columns=['ticker','price','drop_rate','recovery_rate','rsi','ma20','ma50','history']).to_csv(output_path, index=False)
        return False

# 테스트 실행용
if __name__ == "__main__":
    run_scan()
