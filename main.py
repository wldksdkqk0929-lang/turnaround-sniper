import os
import module_a_universe as mod_a
import module_b_scanner as mod_b
import module_c_news as mod_c
import module_d_writer as mod_d

def main():
    print("🚀 System Start: Turnaround Sniper")

    # [설정] True로 바꾸면: 기존 데이터가 있을 경우 스캔(A, B)을 건너뜁니다.
    # UI나 뉴스 모듈만 테스트할 때 아주 유용합니다.
    SKIP_IF_EXISTS = True 

    # 1. 유니버스 & 2. 기술적 스캔
    if SKIP_IF_EXISTS and os.path.exists("data/candidates_b.csv"):
        print("⏩ [Dev Mode] Skipping Scanner (Found existing data).")
    else:
        mod_a.build_universe()
        mod_b.run_scan()
    
    # 3. 뉴스 필터링 (항상 실행하거나, 필요시 여기도 조건 추가 가능)
    mod_c.analyze_news()

    # 4. 대시보드 생성 (항상 실행)
    mod_d.export_to_json()

    print("🏁 Pipeline Completed Successfully.")

if __name__ == "__main__":
    main()
