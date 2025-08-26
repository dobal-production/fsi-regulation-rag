import streamlit as st
import logging
import os
from utils.bedrock_lib import BedrockRAG

# 로깅 설정
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

PAGE_TITLE = "한국금융규제 관련 Q&A 채팅봇"

# 페이지 설정
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 모델 옵션 정의
MODEL_OPTIONS = {
    "Claude Sonnet 4": "apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "Claude 3.7 Sonnet": "apac.anthropic.claude-3-7-sonnet-20250219-v1:0",
    "Amazon Nova Pro": "apac.amazon.nova-pro-v1:0"
}

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Claude 3.7 Sonnet"

if "bedrock_rag" not in st.session_state:
    st.session_state.bedrock_rag = BedrockRAG(model_id=MODEL_OPTIONS[st.session_state.selected_model])

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 4000

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.0

if "top_p" not in st.session_state:
    st.session_state.top_p = 0.9

if "max_results" not in st.session_state:
    st.session_state.max_results = 5

# 사이드바 - 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 모델 선택
    selected_model = st.selectbox(
        "모델 선택:",
        options=list(MODEL_OPTIONS.keys()),
        index=list(MODEL_OPTIONS.keys()).index(st.session_state.selected_model)
    )
    
    # 모델이 변경되었을 때 업데이트
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        st.session_state.bedrock_rag = BedrockRAG(model_id=MODEL_OPTIONS[selected_model])
        st.rerun()
    
    st.divider()
    
    # 모델 파라미터 설정
    st.subheader("🎛️ 모델 파라미터")
    
    max_tokens = st.slider(
        "Max Tokens:",
        min_value=100,
        max_value=8000,
        value=st.session_state.max_tokens,
        step=100
    )
    
    temperature = st.slider(
        "Temperature:",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.1
    )
    
    top_p = st.slider(
        "Top P:",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.top_p,
        step=0.1
    )
    
    st.divider()
    
    # 검색 설정
    st.subheader("🔍 검색 설정")
    
    max_results = st.number_input(
        "검색할 문서 수:",
        min_value=1,
        max_value=20,
        value=st.session_state.max_results,
        step=1
    )
    
    # 파라미터 업데이트
    st.session_state.max_tokens = max_tokens
    st.session_state.temperature = temperature
    st.session_state.top_p = top_p
    st.session_state.max_results = max_results


def extract_filename_from_location(location):
    """S3 Location에서 파일명을 추출하는 메소드"""
    if location and 's3Location' in location:
        s3_uri = location['s3Location'].get('uri', '')
        if s3_uri:
            return s3_uri.split('/')[-1]
    return "알 수 없는 파일"

def display_reference_documents(kb_results):
    """참고 문서 및 인용 정보를 표시하는 메소드"""
    with st.expander(f"📚 참고 문서 ({len(kb_results)}개)"):
        for i, result in enumerate(kb_results, 1):
            location = result.get('location', {})
            filename = extract_filename_from_location(location)
            
            st.write(f"**문서 {i}:** `{filename}` (점수: {result.get('score', 'N/A'):.3f})")
            st.write(f"출처: {filename}")
            doc_content = result["content"]
            st.write(doc_content[:300] + "..." if len(doc_content) > 300 else doc_content)
            st.divider()

# 메인 채팅 인터페이스
st.title(f"🤖 {PAGE_TITLE}")
st.caption(f"Amazon Bedrock Knowledge Base를 활용한 RAG 기반 채팅봇입니다. (현재 모델: {st.session_state.selected_model})")

# 채팅 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI 응답 생성
    with st.chat_message("assistant"):
        # Knowledge Base에서 검색
        kb_results = []
        context = ""
        if st.session_state.bedrock_rag.knowledge_base_id:
            with st.spinner("관련 문서를 검색하고 있습니다..."):
                kb_results = st.session_state.bedrock_rag.retrieve_only(prompt, max_results=st.session_state.max_results)
                context_docs = [result["content"] for result in kb_results]
                context = "\n\n".join(context_docs) if context_docs else ""
        
        # 검색 결과가 있을 때만 응답 생성
        if kb_results:
            # 스트리밍 응답 생성
            response_placeholder = st.empty()
            full_response = ""
            
            for chunk in st.session_state.bedrock_rag.generate_response_stream(
                prompt, 
                context, 
                max_tokens=st.session_state.max_tokens,
                temperature=st.session_state.temperature,
                top_p=st.session_state.top_p
            ):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            
            # 참고 문서 및 인용 정보 표시
            display_reference_documents(kb_results)
        else:
            full_response = "죄송합니다. 관련된 문서를 찾을 수 없어 답변을 드릴 수 없습니다. 다른 질문을 시도해 보세요."
            st.markdown(full_response)
            
            if not st.session_state.bedrock_rag.knowledge_base_id:
                st.info("💡 환경 변수에서 KNOWLEDGE_BASE_ID를 설정하면 RAG 기능을 사용할 수 있습니다.")
        
        response = full_response
    
    # AI 응답을 세션에 저장
    st.session_state.messages.append({"role": "assistant", "content": response})

# 채팅 기록 초기화 버튼
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("채팅 기록 초기화"):
        st.session_state.messages = []
        st.rerun()