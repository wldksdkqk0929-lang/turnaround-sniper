import os
import module_a_universe as mod_a
import module_b_scanner as mod_b
import module_c_news as mod_c
import module_d_writer as mod_d

def main():
    print("🚀 System Start: Turnaround Sniper (Precision Filter Mode)")
    
    # [중요] 기존 쓰레기 데이터 삭제 (강제 재실행)
    if os.path.exists("data/candidates_b.csv"):
        os.remove("data/candidates_b.csv")
        print("🗑️ Cleared old data for fresh scan.")

    # 1. 유니버스 구성
    mod_a.build_universe()
    
    # 2. 정밀 스캔 (Module B 수정본 실행)
    # 이제 $2 미만 잡주와 +200% 가짜 급등주는 걸러집니다.
    success = mod_b.run_scan() 
    
    if success:
        # 3. 뉴스 분석
        mod_c.analyze_news(input_path="data/candidates_b.csv", output_path="data/candidates_final.csv")
        
        # 4. JSON 변환 (HTML 시각화용)
        mod_d.export_to_json(input_path="data/candidates_final.csv")
        print("✅ All systems go. Dashboard ready.")
    else:
        print("❌ Scan failed or no targets found.")

    print("🏁 Pipeline Completed.")

if __name__ == "__main__":
    main()
