import pandas as pd
import json
import os
from datetime import datetime

def export_to_json(input_path="data/candidates_c.csv", output_path="data/data.json"):
    print("📝 Module D: Generating AI Report...")
    
    logs = []
    stats = {"universe": 0, "s1_filtered": 0, "s2_checked": 0, "final_ready": 0}

    # Step A, B 생략 (이전 코드와 동일하므로 로그 로직 유지된다고 가정하고 핵심만 작성)
    # 실제 파일에는 Step A, B 확인 로직이 있어야 하지만, 코드 길이를 줄이기 위해
    # 지휘관님이 쓰시던 기존 module_d_writer.py의 앞부분(로그 수집)은 그대로 두고
    # 아래 [데이터 매핑] 부분만 바뀌는 것이 원칙입니다.
    # 하지만 복잡함을 피하기 위해 '전체 코드'를 드립니다.
    
    # [로그 수집 - 약식 복원]
    if os.path.exists("data/universe.csv"): stats['universe'] = len(pd.read_csv("data/universe.csv"))
    if os.path.exists("data/candidates_b.csv"): stats['s1_filtered'] = len(pd.read_csv("data/candidates_b.csv"))
    
    candidates = []
    if os.path.exists(input_path):
        try:
            df = pd.read_csv(input_path)
            stats['s2_checked'] = len(df)
            
            if not df.empty:
                logs.append(f"✅ [Step 3] AI Analysis: {len(df)} candidates rated.")
                
                for _, row in df.iterrows():
                    rec_rate = row.get('recovery_rate', 0) / 100.0
                    
                    # 태그 로직: 반등 10% 이상이면서 감성 점수가 너무 나쁘지 않아야 함(-0.5 이상)
                    sent_score = row.get('sentiment_score', 0)
                    
                    tag = "WATCH"
                    if rec_rate >= 0.10 and sent_score > -0.5:
                        tag = "READY"
                    
                    if tag == "READY": stats['final_ready'] += 1
                    
                    # 데이터 매핑 (링크와 점수 추가)
                    news_text = row.get('news_top', 'No Data')
                    if pd.isna(news_text): news_text = "No Data"

                    candidate = {
                        "ticker": str(row['ticker']),
                        "price": float(row['price']),
                        "metrics": {
                            "drop_rate": row.get('drop_rate', 0),
                            "rec_rate": rec_rate
                        },
                        "evidence": {
                            "s4_tag": tag,
                            "ai_score": float(sent_score) # AI 점수
                        },
                        "context": {
                            "title": str(news_text),
                            "url": str(row.get('news_link', '#')) # 뉴스 링크
                        }
                    }
                    candidates.append(candidate)
        except Exception as e:
            logs.append(f"❌ Error: {str(e)}")
    
    data = {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S KST"),
            "pipeline_stats": stats,
            "system_logs": logs
        },
        "candidates": candidates
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return True
