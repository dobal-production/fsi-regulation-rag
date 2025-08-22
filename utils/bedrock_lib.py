import boto3
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# 상수 정의
SYSTEM_PROMPT = "당신은 한국어로 답변하는 도움이 되는 AI 어시스턴트입니다."

class BedrockRAG:
    def __init__(self, model_id: str = None, region_name: str = None, knowledge_base_id: str = None):
        self.region_name = region_name or os.getenv("AWS_REGION")
        self.knowledge_base_id = knowledge_base_id or os.getenv("KNOWLEDGE_BASE_ID")
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region_name
        )
        self.bedrock_agent_runtime = boto3.client(
            service_name="bedrock-agent-runtime",
            region_name=self.region_name
        )
        self.model_id = model_id
    
    def generate_response_stream(self, prompt: str, context: str = "", max_tokens: int = 1000, temperature: float = 0.0, top_p: float = 0.9):
        """Bedrock Converse Stream API를 사용하여 스트리밍 응답 생성"""
        system_prompt = SYSTEM_PROMPT
        
        if context:
            system_prompt += f"\n\n다음 컨텍스트를 참고하여 답변하세요:\n{context}"
        
        try:
            response = self.bedrock_runtime.converse_stream(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                system=[{"text": system_prompt}],
                inferenceConfig={
                    "maxTokens": max_tokens,
                    "temperature": temperature,
                    "topP": top_p
                }
            )
            
            for event in response["stream"]:
                if "contentBlockDelta" in event:
                    delta = event["contentBlockDelta"]["delta"]
                    if "text" in delta:
                        yield delta["text"]
                        
        except Exception as e:
            yield f"오류가 발생했습니다: {str(e)}"
    
    def retrieve_only(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Knowledge Base에서 관련 문서만 검색"""
        if not self.knowledge_base_id:
            return []
            
        try:
            response = self.bedrock_agent_runtime.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={
                    "text": query
                },
                retrievalConfiguration={
                    "vectorSearchConfiguration": {
                        "numberOfResults": max_results
                    }
                }
            )
            
            results = []
            for result in response["retrievalResults"]:
                results.append({
                    "content": result["content"]["text"],
                    "score": result["score"],
                    "location": result.get("location", {})
                })
            
            return results
            
        except Exception as e:
            print(f"검색 오류: {str(e)}")
            return []

