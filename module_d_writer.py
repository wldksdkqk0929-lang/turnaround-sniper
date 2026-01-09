import pandas as pd
import json
import os
from datetime import datetime

def export_to_json(input_path="data/candidates_c.csv", output_path="data/data.json"):
    print("📝 Module D: Generating Korean Operation Report...")
    
    # 통계용 변수 초기화
    logs = []
    stats = {"universe": 0, "s1_filtered": 0, "s2_checked": 0, "final_ready": 0}

    # 1. Universe 카운트
    if os.path.exists("data/universe.csv"):
        try:
            stats['universe'] = len(pd.read_csv("data/universe.csv"))
        except: pass

    # 2. Scanner 카운트
    if os.path.exists("data/candidates_b.csv"):
        try:
            stats['s1_filtered'] = len(pd.read_csv("data/candidates_b.csv"))
        except: pass

    candidates = []
    
    # 3. 데이터 가공 및 한글 리포트 작성
    if os.path.exists(input_path):
        try:
            df = pd.read_csv(input_path)
            stats['s2_checked'] = len(df)
            
            for _, row in df.iterrows():
                # 수치 데이터 정리
                drop_rate = row.get('drop_rate', 0)
                rec_rate = row.get('recovery_rate', 0) / 100.0
                price = row.get('price', 0)
                ticker = row['ticker']
                
                # 태그 결정
                tag = "READY" if rec_rate >= 0.10 else "WATCH"
                if tag == "READY": stats['final_ready'] += 1

                # [수정] 뉴스 데이터 문자열 강제 변환 (오류 해결 핵심)
                raw_news = row.get('news_top', '')
                if pd.isna(raw_news) or str(raw_news).strip() == "" or str(raw_news).lower() == 'nan':
                    news_text = "특이 뉴스 없음 (기술적 반등 구간)"
                else:
                    news_text = str(raw_news)

                # [신규] AI 분석 리포트 생성 (한글)
                # 실제 AI 모델 없이 로직 기반으로 문장 생성
                if tag == "READY":
                    analysis = (
                        f"📉 **하락 요인:** 고점 대비 -{abs(drop_rate):.1f}% 급락하며 과매도 구간 진입. "
                        f"최근 뉴스를 통해 악재 소멸 여부 확인 필요.\n"
                        f"🚀 **반등 시그널:** 저점 대비 +{rec_rate*100:.1f}% 반등하며 강력한 매수세 유입 확인. "
                        f"기관 수급이 의심되는 '기술적 턴어라운드' 초기 단계입니다."
                    )
                else:
                    analysis = (
                        f"📉 **하락 요인:** -{abs(drop_rate):.1f}% 하락했으나 아직 바닥 확인 중. "
                        f"시장 소외주이거나 악재가 진행 중일 가능성 있음.\n"
                        f"⚠️ **관망 필요:** 반등폭이 +{rec_rate*100:.1f}%로 미미함. "
                        f"확실한 거래량 실린 양봉 출현 전까지는 진입 유보 권장."
                    )

                candidate = {
                    "ticker": str(ticker),
                    "price": float(price),
                    "metrics": {
                        "drop_rate": drop_rate,
                        "rec_rate": rec_rate
                    },
                    "evidence": {
                        "s4_tag": tag,
                        "analysis_kr": analysis  # 한글 분석 내용
                    },
                    "context": news_text  # 깨끗한 뉴스 문자열
                }
                candidates.append(candidate)
                
        except Exception as e:
            print(f"❌ Error in Module D: {e}")
            logs.append(f"Error: {e}")

    # 최종 JSON 저장
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
    
    print("✅ Module D: Korean Report Generated.")
    return True
