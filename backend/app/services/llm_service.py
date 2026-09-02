import time
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.core.logging import logger


class LLMService:
    def __init__(self, api_key: Optional[str] = None, provider: str = "groq"):
        self.api_key = api_key if (api_key and api_key.strip()) else settings.effective_groq_key
        self.provider = provider

    def get_model(self, model_name: str = "llama-3.1-8b-instant"):
        if self.provider == "openai" or (self.api_key and self.api_key.startswith("sk-")):
            openai_key = self.api_key if self.api_key.startswith("sk-") else (settings.OPENAI_API_KEY or "")
            return ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)
        return ChatGroq(model=model_name, api_key=self.api_key)

    def invoke_chain_with_retry(self, prompt: ChatPromptTemplate, variables: dict, max_retries: int = 2) -> str:
        model = self.get_model()
        chain = prompt | model

        last_exception = None
        for attempt in range(max_retries):
            try:
                res = chain.invoke(variables)
                return str(res.content)
            except Exception as e:
                err_str = str(e)
                logger.warning(f"LLM attempt {attempt + 1} failed: {err_str}")
                last_exception = e
                if "401" in err_str or "invalid_api_key" in err_str or "unauthorized" in err_str.lower():
                    break
                time.sleep(1)

        raise RuntimeError(f"LLM failed: {last_exception}")


llm_service = LLMService()
