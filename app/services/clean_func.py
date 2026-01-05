import re
import os
import pandas as pd
# --- Helper Functions ---
def _fix_thai_vowel_am(text):
    if not text: return ""
    return re.sub(r'([ก-๙])\sา', r'\1ำ', text)

def _remove_thai_chars(text):
    if not text: return ""
    return re.sub(r'[ก-๙]+', '', text).strip("- :").strip()  

def _remove_description_suffix(text):
    if not text: return ""
    return re.sub(r'\s*Description\s*', '', text, flags=re.IGNORECASE).strip()

def _split_thai_eng(text):
    if not text: return "", ""
    text = text.strip()
    match = re.search(r'[A-Za-z]', text)
    if match:
        idx = match.start()
        thai_part = text[:idx].strip("- :").strip()
        eng_part = text[idx:].strip("- :").strip()
        return thai_part, eng_part
    else:
        return text, ""

def _clean_markdown_garbage(text):
    if not text: return ""
    text = text.replace('|', '')
    text = re.sub(r'[-]{2,}', '', text)
    return text.strip()

def _process_description(raw_desc_text):
    if not raw_desc_text: return "", ""
    r = raw_desc_text.replace('\n', ' ').replace('\r', '')
    r = re.sub(r'\s+', ' ', r)
    r = _clean_markdown_garbage(r)
    th, en = _split_thai_eng(r)
    en = _remove_thai_chars(en)
    en = _clean_markdown_garbage(en)
    en = _remove_description_suffix(en)
    th = _fix_thai_vowel_am(th)
    return th, en