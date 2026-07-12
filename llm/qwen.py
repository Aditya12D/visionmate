from ollama import chat
from config import MODEL_NAME, TEMPERATURE
from llm.prompts import (
    READING_PROMPT,
    EXPLAIN_PROMPT,
    SUMMARY_PROMPT,
)

class Qwen:

    def __init__(self):
        self.model = MODEL_NAME

    def generate(self, system_prompt, user_prompt):

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            options={
                "temperature": TEMPERATURE
            }
        )

        return response["message"]["content"].strip()
    
    
    def read(self, text):
        return self.generate(READING_PROMPT, text)

    def explain(self, text):
        return self.generate(EXPLAIN_PROMPT, text)

    def summarize(self, text):
        return self.generate(SUMMARY_PROMPT, text)