import os
import module_a_universe as mod_a
import module_b_scanner as mod_b
import module_c_news as mod_c
import module_d_writer as mod_d  # <--- 이 친구가 반드시 있어야 합니다!

def main():
    print("🚀 System Start: Turnaround Sniper")
    
    # 1. 유니버스 생성
    mod_a.build_universe()
    
    # 2. 기술적 스캔
    mod_b.run_scan()
    
    # 3. 뉴스 필터링
    mod_c.analyze_news()

    # 4. [중요] 대시보드용 데이터 변환 (이 부분이 빠져있었을 겁니다)
    mod_d.export_to_json()

    print("🏁 Pipeline Completed Successfully.")

if __name__ == "__main__":
    main()
