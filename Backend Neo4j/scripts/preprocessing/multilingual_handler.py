# scripts/preprocessing/multilingual_handler.py
from __future__ import annotations
from langdetect import detect, DetectorFactory
from unidecode import unidecode
from transformers import MarianMTModel, MarianTokenizer
import torch
import re

DetectorFactory.seed = 0

MODEL_CACHE = {}

def load_translator(src_lang: str, tgt_lang: str = "en"):
    model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
    if model_name not in MODEL_CACHE:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        MODEL_CACHE[model_name] = (tokenizer, model)
    return MODEL_CACHE[model_name]

def translate_text(text: str, src_lang: str, tgt_lang: str = "en") -> str:
    if src_lang == tgt_lang:
        return text
    try:
        tokenizer, model = load_translator(src_lang, tgt_lang)
        batch = tokenizer([text], return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            gen = model.generate(**batch)
        return tokenizer.decode(gen[0], skip_special_tokens=True)
    except Exception as e:
        print(f"[WARN] Translation failed ({src_lang}->{tgt_lang}): {e}")
        return text

def detect_language(text: str) -> str:
    try:
        return detect(text) if text and text.strip() else "en"
    except Exception:
        return "en"

def is_ascii(text: str) -> bool:
    return all(ord(c) < 128 for c in text)

def normalize_multilingual(text: str, target_lang: str = "en") -> dict:
    """
    - Detect language
    - Detect if ASCII transliteration (Hinglish etc.)
    - Translate to English for embeddings/LLM
    """
    lang = detect_language(text)
    ascii_flag = is_ascii(text)
    english_text = translate_text(text, lang, target_lang) if lang != target_lang else text
    
    return {
        "lang": lang,               # hi, en, ja...
        "original": text or "",
        "is_ascii": ascii_flag,     # True if Hinglish style
        "english": english_text     # always normalized English
    }

def back_translate(answer_en: str, user_info: dict) -> str:
    """
    Translate LLM output (English) back into user’s language or script style.
    """
    user_lang = user_info["lang"]
    if user_lang == "en":
        return answer_en
    
    if user_info.get("is_ascii") and user_lang == "hi":
        # Hinglish: instead of translating, keep ASCII
        return unidecode(translate_text(answer_en, "en", "hi"))
    
    return translate_text(answer_en, "en", user_lang)
