import os
import warnings

# Tüm uyarıları kapatıyoruz
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
warnings.filterwarnings("ignore")

from transformers import pipeline

en_to_tr_translator = pipeline("translation", model="Helsinki-NLP/opus-tatoeba-en-tr")
tr_to_en_translator = pipeline("translation", model="Helsinki-NLP/opus-mt-tr-en")

def en_to_tr(text):
    if not text:
        return ""
    result = en_to_tr_translator(text)
    return result[0]['translation_text']

def tr_to_en(text):
    if not text:
        return ""
    result = tr_to_en_translator(text)
    return result[0]['translation_text']