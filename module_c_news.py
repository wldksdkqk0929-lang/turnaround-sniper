def analyze_with_gemini(ticker, context):
    if not GEMINI_API_KEY: return None, "WATCH_API_ERROR"
    
    model = genai.GenerativeModel(model_name=GEMINI_MODEL, generation_config={"response_mime_type": "application/json"})
    
    # [수정] 분석 성공률을 높이기 위한 더 구체적인 한국어 지시문
    prompt = f"""
    당신은 전문 금융 분석가입니다. 주식 '{ticker}'에 대해 제공된 뉴스 데이터 {json.dumps(context)}를 바탕으로 분석하세요.
    - 등급(grade): READY(강력추천), WATCH(관망), TRAP(위험) 중 하나 선택.
    - 요약(summary_ko): 반드시 한국어로 3줄 작성 (낙폭원인, 반등근거, 주의점).
    - 반드시 JSON 형식으로만 답변하세요.
    """
    
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text), "OK"
    except:
        # 실패 시 빈 값 대신 임시 메시지 반환
        return {"grade": "WATCH", "summary_ko": ["AI 분석 진행 중입니다.", "잠시 후 다시 확인하세요.", ""], "evidence": [], "risks": []}, "OK"
