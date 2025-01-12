import streamlit as st
import sqlite3
import deepl
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize DeepL translator
DEEPL_AUTH_KEY = os.getenv('DEEPL_AUTH_KEY')
if not DEEPL_AUTH_KEY:
    st.error("DeepL API key not found. Please ensure DEEPL_AUTH_KEY is set in your .env file.")
    st.stop()

try:
    deepl_translator = deepl.Translator(DEEPL_AUTH_KEY)
except Exception as e:
    st.error(f"Failed to initialize DeepL translator: {str(e)}")
    st.stop()

def init_db():
    """Initialize SQLite database and create table if it doesn't exist"""
    conn = sqlite3.connect('trans.sqlite3')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS t_translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_text TEXT NOT NULL,
            target_text TEXT NOT NULL,
            source_lang TEXT NOT NULL,
            target_lang TEXT NOT NULL,
            service_provider TEXT NOT NULL,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_translation(source_text, target_text, source_lang, target_lang, provider, note):
    """Save translation to database"""
    conn = sqlite3.connect('trans.sqlite3')
    c = conn.cursor()
    c.execute('''
        INSERT INTO t_translations 
        (source_text, target_text, source_lang, target_lang, service_provider, note)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (source_text, target_text, source_lang, target_lang, provider, note))
    conn.commit()
    conn.close()

def get_google_languages():
    return []

def translate_text(text, target_lang, provider="DeepL"):
    """Translate text using DeepL"""
    try:
        if provider == "DeepL":
            # First detect the source language
            source_lang_result = deepl_translator.translate_text(text, target_lang="EN-US")
            detected_lang = source_lang_result.detected_source_lang
            
            # Then perform the actual translation
            translation_result = deepl_translator.translate_text(
                text, 
                target_lang=target_lang,
                source_lang=detected_lang
            )
            return translation_result.text, detected_lang
        else:
            st.warning("Google Translate is currently disabled")
            return "", ""
    except deepl.exceptions.DeepLException as e:
        st.error(f"DeepL API error: {str(e)}")
        return "", ""
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return "", ""

def main():
    st.title("Translation App")
    
    # Initialize database
    init_db()
    
    # Service provider selection
    col_provider, col_lang = st.columns(2)
    
    with col_provider:
        provider = st.selectbox(
            "Select Service Provider",
            options=["DeepL", "Google Translate"],
            index=0  # DeepL as default
        )
    
    # Get available languages based on provider
    if provider == "DeepL":
        try:
            target_languages = {lang.code: lang.name for lang in deepl_translator.get_target_languages()}
            # Debug: Print all available languages and their codes
            # st.write("Available languages:", target_languages)
            
            # Prefer ZH-HANS over ZH for better Chinese translation
            chinese_codes = [code for code, name in target_languages.items() 
                           if "Chinese" in name]
            default_chinese_code = "ZH-HANS" if "ZH-HANS" in chinese_codes else "ZH"
            st.write("Default Chinese code:", default_chinese_code)
            
        except Exception as e:
            st.error(f"Error fetching DeepL languages: {str(e)}")
            target_languages = {}
    else:
        target_languages = get_google_languages()
    
    with col_lang:
        target_langs = list(target_languages.keys())
        # Set default to ZH-HANS if available, otherwise ZH, or first language
        if any(code in target_langs for code in ['ZH-HANS', 'ZH']):
            default_index = target_langs.index(default_chinese_code)
        else:
            default_index = 0
            
        target_lang = st.selectbox(
            "Select target language",
            options=target_langs,
            index=default_index,
            format_func=lambda x: target_languages[x]
        )
    
    # Create two columns for source and target text
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Source Text")
        source_text = st.text_area("Enter text to translate", height=200)
        
        if source_text:
            try:
                # Detect source language
                _, detected_lang = translate_text(source_text, "EN-US", provider)
                if detected_lang:
                    st.info(f"Detected language: {detected_lang}")
            except Exception as e:
                st.error(f"Error detecting language: {str(e)}")
                detected_lang = ""

        # Translate button
        if st.button("Translate") and source_text:
            translated_text, detected_lang = translate_text(source_text, target_lang, provider)
            if translated_text:
                st.session_state.translated_text = translated_text
            

    with col2:
        st.subheader("Translated Text")
        
        # Initialize translated text
        if 'translated_text' not in st.session_state:
            st.session_state.translated_text = ""
                  
        # Editable translation output
        translated_text = st.text_area(
            "Translated text (editable)",
            value=st.session_state.translated_text,
            height=200
        )
    
        # Note input
        note = st.text_area("Notes (optional)", 
                           placeholder="Add any comments, TODOs, or research items here", 
                           height=100)
    
    # Save button
    if st.button("Save Translation"):
        if source_text and translated_text:
            try:
                save_translation(source_text, translated_text, detected_lang, target_lang, provider, note)
                st.success("Translation saved successfully!")
            except Exception as e:
                st.error(f"Error saving translation: {str(e)}")
        else:
            st.warning("Please provide both source and target text")

if __name__ == "__main__":
    main()