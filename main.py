import os
import module_a_universe as mod_a
import module_b_scanner as mod_b
import module_c_news as mod_c
import module_d_writer as mod_d

def main():
    print("🚀 System Start: Turnaround Sniper (Smart Fix Mode)")
    
    # 이미 20분 걸려서 만든 파일이 있다면? 스캔 생략!
    if os.path.exists("data/candidates_final.csv"):
        print("⏩ Found existing final data. Skipping Scan & News analysis.")
        print("🔄 Regenerating JSON only (Fixing Display Errors)...")
        
        # JSON 변환만 다시 실행 (1초 소요)
        mod_d.export_to_json(input_path="data/candidates_final.csv")
        
    else:
        # 파일이 없으면 처음부터 실행 (이건 비상시용)
        print("⚠️ No data found. Starting full scan (Takes long time)...")
        mod_a.build_universe()
        mod_b.run_scan()
        if os.path.exists("data/candidates_b.csv"):
            mod_c.analyze_news(input_path="data/candidates_b.csv", output_path="data/candidates_final.csv")
            mod_d.export_to_json(input_path="data/candidates_final.csv")

    print("🏁 Pipeline Completed.")

if __name__ == "__main__":
    main()
