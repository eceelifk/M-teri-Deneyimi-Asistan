import os
import fitz
import time
from deep_translator import GoogleTranslator

def translate_pdfs():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_dir = os.path.join(base_dir, "data", "pdf")
    faq_dir = os.path.join(base_dir, "data", "faq")
    
    if not os.path.exists(pdf_dir):
        print(f"PDF directory not found: {pdf_dir}")
        return
        
    translator = GoogleTranslator(source='tr', target='en')
    
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            print(f"Translating {filename}...")
            
            try:
                pdf = fitz.open(pdf_path)
                full_text = ""
                for page in pdf:
                    full_text += page.get_text() + "\n"
                pdf.close()
                
                # split text into chunks
                chunks = []
                text = full_text
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
                            
                txt_filename = filename.replace(".pdf", "_en.txt")
                txt_path = os.path.join(faq_dir, txt_filename)
                
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(translated_text)
                    
                print(f"Saved translated text to {txt_filename}")
                
                # Delete the original PDF
                os.remove(pdf_path)
                print(f"Deleted original PDF: {filename}")
                
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    translate_pdfs()
