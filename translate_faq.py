import os
import time
from deep_translator import GoogleTranslator

def translate_directory(directory):
    translator = GoogleTranslator(source='tr', target='en')
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            print(f"Translating {filename}...")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                
            # split text into chunks if it's too long (Google Translator limit is 5000)
            chunks = []
            while len(text) > 4000:
                split_idx = text.rfind('\n', 0, 4000)
                if split_idx == -1: split_idx = 4000
                chunks.append(text[:split_idx])
                text = text[split_idx:]
            if text:
                chunks.append(text)
                
            translated_text = ""
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    try:
                        translated_text += translator.translate(chunk) + "\n"
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"Error translating chunk {i}: {e}")
                        translated_text += chunk + "\n"
                        
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(translated_text)
                
    print("Done translating FAQ files.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    faq_dir = os.path.join(base_dir, "data", "faq")
    translate_directory(faq_dir)
