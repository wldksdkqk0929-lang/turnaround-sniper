import os
import module_a_universe as mod_a
import module_b_scanner as mod_b
import module_c_news as mod_c
import module_d_writer as mod_d

def main():
    print("🚀 System Start: Turnaround Sniper (Force Run Mode)")
    
    # [핵심] 기존 데이터 강제 삭제 (꾀부리기 방지)
    if os.path.exists("data/candidates_b.csv"):
        os.remove("data/candidates_b.csv")
        print("🗑️ Deleted old scan data to force update.")

    # 1. 유니버스 구성
    mod_a.build_universe()
    
    # 2. 스캔 및 차트 데이터 수집 (여기가 오래 걸려야 정상!)
    # 이 함수가 실행될 때 'Fetching 3-month history...' 로그가 찍혀야 함
    mod_b.run_scan() 
    
    # 3. 뉴스 및 최종 데이터 처리
    # (Module B가 새로 만든 파일을 입력으로 받음)
    if os.path.exists("data/candidates_b.csv"):
        mod_c.analyze_news(input_path="data/candidates_b.csv", output_path="data/candidates_final.csv")
        mod_d.export_to_json(input_path="data/candidates_final.csv")
        print("✅ Data generation complete.")
    else:
        print("❌ Error: Module B failed to generate data.")

    print("🏁 Pipeline Completed.")

if __name__ == "__main__":
    main()
