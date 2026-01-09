import pandas as pd
import json
import os
from datetime import datetime

def export_to_json(input_path="data/candidates_c.csv", output_path="data/data.json"):
    print("💾 Module D: Converting data to JSON for Dashboard...")
    
    # 1. 데이터 로드 (파일이 없거나 비어있으면 빈 JSON 생성)
    if not os.path.exists(input_path):
        candidates = []
    else:
        try:
            df = pd.read_csv(input_path)
            candidates = []
            
            for _, row in df.iterrows():
                # HTML 대시보드가 요구하는 데이터 구조로 매핑
                rec_rate = row.get('recovery_rate', 0) / 100.0 # 퍼센트를 소수로 변환
                
                # 태그 결정 로직 (반등폭 10% 이상이면 READY)
                tag = "READY" if rec_rate >= 0.10 else "WATCH"
                
                candidate = {
                    "ticker": str(row['ticker']),
                    "price": float(row['price']),
                    "metrics": {
                        "rec_rate": rec_rate
                    },
                    "evidence": {
                        "s4_tag": tag
                    },
                    "context": str(row.get('news_top', 'No News Data'))
                }
                candidates.append(candidate)
        except Exception as e:
            print(f"⚠️ Error reading CSV: {e}")
            candidates = []

    # 2. 메타데이터 생성 (통계치)
    # 실제 카운트를 위해 universe 파일 등을 읽어야 하지만, 약식으로 처리
    try:
        uni_count = len(pd.read_csv("data/universe.csv")) if os.path.exists("data/universe.csv") else 6000
    except: uni_count = 6000

    data = {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S KST"),
            "pipeline_stats": {
                "universe": uni_count,
                "s1_drawdown": 300, # 스캔 대상 수 (Scanner 코드의 제한 값)
                "s3_news_risk": len(candidates)
            }
        },
        "candidates": candidates
    }

    # 3. JSON 파일 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Module D: JSON generated at {output_path}")
    return True
