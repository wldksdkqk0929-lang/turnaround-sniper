import yfinance as yf
import pandas as pd
import time
import os

def run_scan(input_path="data/universe.csv", output_path="data/candidates_b.csv"):
    if not os.path.exists(input_path):
        print("❌ Module B: Input file not found.")
        return False

    df_unv = pd.read_csv(input_path)
    tickers = df_unv['ticker'].tolist()
    results = []
    
    print(f"🔬 Module B: Scanning {len(tickers)} tickers... (This may take time)")

    # [테스트 모드] 전체 6000개는 너무 오래 걸리므로, 우선 300개만 샘플링하여 로직 검증 권장
    # 실전 배치 시에는 tickers[:300] 을 tickers 로 변경하십시오.
    for i, ticker in enumerate(tickers[:300]): 
        try:
            # 진행 상황 표시 (50개마다)
            if i % 50 == 0: print(f"...Scanning {i}/{len(tickers)}...")

            stock = yf.Ticker(ticker)
            # 1년치 데이터, 에러 발생 시 무시(auto_adjust=True로 수정주가 반영)
            hist = stock.history(period="1y", auto_adjust=True)
            
            if len(hist) < 200: continue # 상장된 지 1년 미만 제외

            high_1y = hist['High'].max()
            curr = hist['Close'].iloc[-1]
            low_20d = hist['Low'].iloc[-20:].min()
            
            if high_1y == 0: continue # 데이터 오류 방지

            dd = (curr / high_1y) - 1       # 고점 대비 낙폭
            rec = (curr / low_20d) - 1      # 저점 대비 반등폭

            # 필터 조건: 낙폭 -30% 이상, 바닥 반등 5%~20%
            if dd <= -0.30 and 0.05 <= rec <= 0.20:
                results.append({
                    "ticker": ticker, 
                    "price": round(curr, 2), 
                    "drop_rate": round(dd * 100, 2), 
                    "recovery_rate": round(rec * 100, 2)
                })
            
            # API 차단 방지용 딜레이 (0.1초)
            time.sleep(0.1)

        except Exception:
            continue # 개별 종목 에러는 무시하고 다음으로 진행

    # 결과 저장
    if results:
        pd.DataFrame(results).to_csv(output_path, index=False)
        print(f"✅ Module B: Found {len(results)} candidates.")
    else:
        print("⚠️ Module B: No candidates found.")
        # 빈 파일이라도 생성해야 파이프라인이 안 깨짐
        pd.DataFrame(columns=["ticker", "price", "drop_rate", "recovery_rate"]).to_csv(output_path, index=False)
    
    return True
