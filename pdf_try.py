import pytesseract
from pdf2image import convert_from_path
import re

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # For Apple Silicon Macs
# OR
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'  # For Intel Macs

def extract_text_between_phrases(pdf_path, start_phrase, end_phrase):
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    
    # Extract text from all pages with Marathi language support
    full_text = ""
    for image in images:
        # Use Tesseract with Marathi and English language
        page_text = pytesseract.image_to_string(image, lang='mar+eng')
        
        # Remove page numbers
        page_text = re.sub(r'\n\s*\d+\s*\n', '\n', page_text)
        
        # Remove N.C.R.B footer line
        page_text = re.sub(r'N\.C\.R\.B \(एन\.सी\.आर\.बी\).*', '', page_text)
        
        # Remove I.I.F.-1 footer line
        page_text = re.sub(r'I\.I\.F\.-1 \(एकीकृत अन् वेषणफॉर्म - १\).*', '', page_text)
        
        # Remove I.I.F.-1 text wherever it appears in the document (including variations)
        page_text = re.sub(r'I\.I\.F\.-1 \(एकीकृत अन् वेषणफॉर्म - १\)', '', page_text)
        page_text = re.sub(r'1\.1\.ए\.-\[ \(एकीकृत अन वेषणफॉर्म - १\)', '', page_text)
        page_text = re.sub(r'1\.1\.ए\.-\[ \(एकीकृत अन् वेषणफॉर्म - १\)', '', page_text)
        
        full_text += page_text + " "
    
    # Find text between phrases
    pattern = f"{re.escape(start_phrase)}(.*?){re.escape(end_phrase)}"
    match = re.search(pattern, full_text, re.DOTALL)
    
    if match:
        return start_phrase + match.group(1)
    else:
        return "The specified phrases were not found in the document."

# Example usage
pdf_path = "/Applications/Tushar/code/Data_extraction/0322 Publish FIR.pdf"
start_phrase = "First Information contents"
end_phrase = "Action taken: Since the above information reveals commission of offence"

extracted_text = extract_text_between_phrases(pdf_path, start_phrase, end_phrase)
print(extracted_text)
