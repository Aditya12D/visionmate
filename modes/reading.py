from llm.qwen import Qwen
from llm.prompts import READING_PROMPT

qwen = Qwen()


def process(text: str) -> str:
    """Reading Mode

    Corrects character-level OCR errors and reassembles broken text segments
    into full, natural paragraphs without omitting data or answering questions.
    """
    if not text.strip():
        return ""

    formatted_prompt = READING_PROMPT.format(ocr_text=text)
    return qwen.read(formatted_prompt)