from openai import AsyncOpenAI


class OpenAIClient:
    def __init__(self, config) -> None:
        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.model = config.openai_model

    async def create_response(self, messages) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""
