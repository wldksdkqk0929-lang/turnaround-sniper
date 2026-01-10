import pandas as pd
import json
import os
import datetime
import numpy as np
import math

# [보조 함수] 리스트 안에 숨은 NaN을 청소하는 함수
def clean_history_list(history_str):
    try:
        # 문자열을 리스트로 변환
        if not isinstance(history_str, str): return []
        data = json.loads(history_str.replace("'", '"'))
        
        # 리스트 내부에 NaN이 있는지 검사하고 청소
        cleaned_data = []
        for x in data:
            # 숫자가 아니거나(NaN), 무한대(inf)면 None으로 변경
            if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
                cleaned_data.append(None)
            else:
                cleaned_data.append(x)
        return cleaned_data
    except:
        return []

def export_to_json(input_path="data/candidates_final.csv", output_path="data/data.json"):
    if not os.path.exists(input_path):
        print(f"❌ Error: {input_path} not found.")
        return

    try:
        df = pd.read_csv(input_path)
        
        # 1차 청소: 데이터프레임 전체의 NaN 제거
        df = df.where(pd.notnull(df), None)

        candidates = []
        for _, row in df.iterrows():
            # 2차 청소: 차트 데이터(history) 정밀 세척
            history_clean = clean_history_list(row.get('history', '[]'))
            
            # 3차 청소: 기본 수치 데이터 안전 처리
            def get_safe_val(val):
                if val is None: return 0
                try:
                    f = float(val)
                    if math.isnan(f) or math.isinf(f): return 0
                    return f
                except: return 0

            candidate = {
                "ticker": row['ticker'],
                "price": get_safe_val(row['price']),
                "drop_rate": get_safe_val(row['drop_rate']),
                "recovery_rate": get_safe_val(row['recovery_rate']),
                "rsi": get_safe_val(row.get('rsi', 0)),
                "high_52w": get_safe_val(row.get('high_52w', 0)),
                "low_52w": get_safe_val(row.get('low_52w', 0)),
                # 청소된 깨끗한 리스트를 문자열로 저장
                "history": json.dumps(history_clean), 
                "context": str(row.get('context', 'No news available')),
                "evidence": {
                    "s4_tag": str(row.get('s4_tag', 'WATCH')),
                    "analysis_kr": str(row.get('analysis_kr', '분석 대기 중...'))
                }
            }
            candidates.append(candidate)

        final_data = {
            "metadata": {
                "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S KST"),
                "total_count": len(candidates)
            },
            "candidates": candidates
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
            
        print(f"✅ JSON Export Successful! ({len(candidates)} items cleaned & saved)")

    except Exception as e:
        print(f"❌ JSON Export Failed: {e}")

if __name__ == "__main__":
    export_to_json()
