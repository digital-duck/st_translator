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

def get_alternatives(text, target_lang, num_alternatives=3):
    """Get alternative translations from DeepL"""
    try:
        alternatives = []
        for _ in range(num_alternatives):
            result = deepl_translator.translate_text(
                text,
                target_lang=target_lang,
                formality="default"
            )
            if result.text not in alternatives:
                alternatives.append(result.text)
        return alternatives
    except:
        return []

def translate_text(text, target_lang, provider="DeepL", source_lang="auto"):
    """Translate text using DeepL"""
    try:
        if provider == "DeepL":
            if source_lang == "auto":
                # First detect the source language
                source_lang_result = deepl_translator.translate_text(text, target_lang="EN-US")
                detected_lang = source_lang_result.detected_source_lang
            else:
                detected_lang = source_lang
            
            # Then perform the actual translation
            translation_result = deepl_translator.translate_text(
                text, 
                target_lang=target_lang,
                source_lang=detected_lang
            )
            
            # Get alternative translations
            alternatives = get_alternatives(text, target_lang)
            # Remove the main translation from alternatives if present
            alternatives = [alt for alt in alternatives if alt != translation_result.text]
            
            # Format alternatives as a note if they exist
            alt_text = ""
            if alternatives:
                alt_text = "Alternative translations:\n" + "\n".join(f"• {alt}" for alt in alternatives)
            
            return translation_result.text, detected_lang, alt_text
        else:
            st.warning("Google Translate is currently disabled")
            return "", "", ""
    except deepl.exceptions.DeepLException as e:
        st.error(f"DeepL API error: {str(e)}")
        return "", "", ""
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return "", "", ""

def main():
    st.title("Translation App")
    
    # Initialize database
    init_db()
    
    alt_text = ""
    # Service provider and language selections
    col_provider, col_target_lang, col_source_lang = st.columns(3)
    
    with col_provider:
        provider = st.selectbox(
            "Select Service Provider",
            options=["DeepL", "Google Translate"],
            index=0  # DeepL as default
        )
    
    # Get available languages based on provider
    if provider == "DeepL":
        try:
            source_languages = {lang.code: lang.name for lang in deepl_translator.get_source_languages()}
            target_languages = {lang.code: lang.name for lang in deepl_translator.get_target_languages()}
            
            # Prefer ZH-HANS over ZH for better Chinese translation
            chinese_codes = [code for code, name in target_languages.items() 
                           if "Chinese" in name]
            default_chinese_code = "ZH-HANS" if "ZH-HANS" in chinese_codes else "ZH"
            
        except Exception as e:
            st.error(f"Error fetching DeepL languages: {str(e)}")
            source_languages = {}
            target_languages = {}
    else:
        source_languages = {}
        target_languages = get_google_languages()
    
    with col_target_lang:
        target_langs = list(target_languages.keys())
        # Sort languages by their display names
        target_langs = sorted(target_langs, key=lambda x: target_languages[x])        
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

    with col_source_lang:
        source_langs = list(source_languages.keys())
        # Sort languages by their display names
        source_langs = sorted(source_langs, key=lambda x: source_languages[x])
        source_lang = st.selectbox(
            "Override source language (optional)",
            options=['auto'] + source_langs,
            format_func=lambda x: 'Auto-detect' if x == 'auto' else source_languages.get(x, x)
        )
            
    # Create two columns for source and target text
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Source Text")
        source_text = st.text_area("Enter text to translate", height=200)
        
        if source_text:
            try:
                # Detect source language only if auto is selected
                if source_lang == "auto":
                    _, detected_lang, _ = translate_text(source_text, "EN-US", provider)
                    if detected_lang:
                        st.info(f"Detected source language: {detected_lang}")
            except Exception as e:
                st.error(f"Error detecting language: {str(e)}")
                detected_lang = ""

        # Translate button
        if st.button("Translate") and source_text:
            translated_text, detected_lang, alt_text = translate_text(
                source_text, 
                target_lang, 
                provider,
                source_lang
            )
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
        note = st.text_area(
            "Notes (optional)", 
            value=alt_text,
            placeholder="Add any comments, TODOs, or research items here", 
            height=100
        )
    
    # Save button
    if st.button("Save Translation"):
        if source_text and translated_text:
            try:
                save_translation(
                    source_text, 
                    translated_text, 
                    source_lang if source_lang != "auto" else detected_lang, 
                    target_lang, 
                    provider, 
                    note
                )
                st.success("Translation saved successfully!")
            except Exception as e:
                st.error(f"Error saving translation: {str(e)}")
        else:
            st.warning("Please provide both source and target text")

if __name__ == "__main__":
    main()