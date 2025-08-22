# 한국금융규제 관련 Q&A 채팅봇 🤖

Amazon Bedrock Knowledge Base를 활용한 RAG(Retrieval-Augmented Generation) 기반 한국어 채팅봇입니다. 한국 금융 규제 관련 질문에 대해 정확하고 신뢰할 수 있는 답변을 제공합니다.

## 🌟 주요 기능

- **다중 AI 모델 지원**: Claude Sonnet 4, Claude 3.7 Sonnet, Amazon Nova Pro
- **실시간 스트리밍 응답**: 빠른 대화형 경험
- **RAG 기반 검색**: Amazon Bedrock Knowledge Base 연동
- **한국어 최적화**: 한국 금융 규제에 특화된 응답
- **참고 문서 제공**: 답변 근거가 되는 문서 표시
- **설정 가능한 파라미터**: Temperature, Top-P, Max Tokens 조정

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │  Amazon Bedrock  │    │  Knowledge Base │
│   Frontend      │◄──►│    Runtime       │◄──►│   (Vector DB)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 빠른 시작

### 사전 요구사항

- Python 3.11+
- AWS 계정 및 자격 증명 설정
- Amazon Bedrock 모델 액세스 권한
- (선택사항) Amazon Bedrock Knowledge Base

### 로컬 설치

1. **저장소 클론**
   ```bash
   git clone <repository-url>
   cd korean-regulation-rag
   ```

2. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **환경 변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일을 편집하여 설정값 입력
   ```

4. **애플리케이션 실행**
   ```bash
   streamlit run app.py
   ```

### Docker 실행

1. **Docker 이미지 빌드**
   ```bash
   docker build -t korean-regulation-rag .
   ```

2. **컨테이너 실행**
   ```bash
   docker run -p 80:80 --env-file .env korean-regulation-rag
   ```

3. **브라우저에서 접속**
   ```
   http://localhost:80/regulation
   ```

## ⚙️ 환경 설정

### 필수 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `AWS_REGION` | AWS 리전 | `us-east-1` |
| `KNOWLEDGE_BASE_ID` | Bedrock Knowledge Base ID | (선택사항) |

### AWS 자격 증명

다음 중 하나의 방법으로 AWS 자격 증명을 설정하세요:

- AWS CLI: `aws configure`
- 환경 변수: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- IAM 역할 (EC2/ECS 환경)
- AWS 프로파일

### 필요한 AWS 권한

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:Retrieve"
            ],
            "Resource": "arn:aws:bedrock:*:*:knowledge-base/*"
        }
    ]
}
```

## 🎛️ 사용법

### 기본 채팅

1. 웹 인터페이스에서 질문을 입력하세요
2. AI가 실시간으로 스트리밍 응답을 제공합니다
3. 참고 문서와 인용 정보를 확인할 수 있습니다

### 설정 조정

사이드바에서 다음 설정을 조정할 수 있습니다:

- **모델 선택**: 사용할 AI 모델 변경
- **Max Tokens**: 응답 길이 제한 (100-8000)
- **Temperature**: 창의성 수준 (0.0-1.0)
- **Top P**: 응답 다양성 (0.0-1.0)
- **검색할 문서 수**: RAG 검색 결과 개수 (1-20)

## 📁 프로젝트 구조

```
korean-regulation-rag/
├── app.py                 # Streamlit 메인 애플리케이션
├── utils/
│   ├── __init__.py
│   └── bedrock_lib.py     # Bedrock RAG 핵심 로직
├── requirements.txt       # Python 의존성
├── Dockerfile            # Docker 컨테이너 설정
├── .env.example          # 환경 변수 템플릿
├── .env                  # 환경 변수 (git에서 제외)
└── README.md             # 프로젝트 문서
```

## 🔧 개발

### 로컬 개발 환경

```bash
# 개발 모드로 실행
streamlit run app.py --server.runOnSave true

# 디버그 모드
streamlit run app.py --logger.level debug
```

### 코드 구조

- `app.py`: Streamlit UI 및 사용자 인터페이스
- `utils/bedrock_lib.py`: Amazon Bedrock 연동 및 RAG 로직
- `BedrockRAG` 클래스: 핵심 RAG 기능 구현

## 🐳 Docker 배포

### 헬스체크

컨테이너는 30초마다 헬스체크를 수행합니다:
```
http://localhost:80/regulation/_stcore/health
```

### 프로덕션 배포

```bash
# 프로덕션 이미지 빌드
docker build -t korean-regulation-rag:prod .

# AWS ECS/EKS 배포 예시
docker tag korean-regulation-rag:prod <account>.dkr.ecr.<region>.amazonaws.com/korean-regulation-rag:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/korean-regulation-rag:latest
```

## 🔍 문제 해결

### 일반적인 문제

1. **모델 액세스 오류**
   - Amazon Bedrock 콘솔에서 모델 액세스 권한 확인
   - 올바른 리전 설정 확인

2. **Knowledge Base 연결 실패**
   - `KNOWLEDGE_BASE_ID` 환경 변수 확인
   - Knowledge Base 상태 및 권한 확인

3. **AWS 자격 증명 오류**
   - AWS CLI 설정 확인: `aws sts get-caller-identity`
   - IAM 권한 정책 검토

### 로그 확인

```bash
# Streamlit 로그
streamlit run app.py --logger.level debug

# Docker 컨테이너 로그
docker logs <container-id>
```

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요.

---

**Made with ❤️ using Amazon Bedrock and Streamlit**