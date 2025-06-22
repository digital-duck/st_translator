# src/pages/1_Translation.py
import streamlit as st
import os
from dotenv import load_dotenv
from src.db.database import TranslationDB
from src.utils.translation import create_translator, TranslationError

# Load environment variables from .env file
load_dotenv()

st.title("Translation")

# Check if project is selected
if 'current_project' not in st.session_state:
    st.error("Please select a project from the Home page first.")
    st.stop()

# Initialize database
db = TranslationDB()

# Initialize translator
DEEPL_AUTH_KEY = os.getenv('DEEPL_AUTH_KEY')
if not DEEPL_AUTH_KEY:
    st.error("DeepL API key not found. Please ensure DEEPL_AUTH_KEY is set in your .env file.")
    st.stop()

try:
    # Initialize translator service
    translator = create_translator("DeepL", auth_key=DEEPL_AUTH_KEY)
except Exception as e:
    st.error(f"Failed to initialize translator: {str(e)}")
    st.stop()

# Service provider and language selections
col_target_lang, col_source_lang, col_provider = st.columns(3)

with col_provider:
    provider = st.selectbox(
        "Select Service Provider",
        options=["Google Translate", "DeepL", ],
        index=0  # DeepL as default
    )

# Get available languages based on provider
try:
    source_languages = translator.get_source_languages()
    target_languages = translator.get_target_languages()
    
    # Prefer ZH-HANS over ZH for better Chinese translation
    chinese_codes = [code for code, name in target_languages.items() 
                    if "Chinese" in name]
    default_chinese_code = "ZH-HANS" if "ZH-HANS" in chinese_codes else "ZH"
    
except Exception as e:
    st.error(f"Error fetching languages: {str(e)}")
    source_languages = {}
    target_languages = {}

with col_target_lang:
    target_langs = list(target_languages.keys())
    # Sort languages by their display names
    target_langs = sorted(target_langs, key=lambda x: target_languages[x])        
    # Set default to ZH-HANS if available, otherwise ZH, or first language
    if any(code in target_langs for code in ['ZH-HANS', 'ZH']):
        default_tgt_index = target_langs.index(default_chinese_code)
    else:
        default_tgt_index = 0
        
    target_lang = st.selectbox(
        "Select Target Language (default='ZH-HANS')",
        options=target_langs,
        index=default_tgt_index,
        format_func=lambda x: target_languages[x]
    )

with col_source_lang:
    source_langs = list(source_languages.keys())
    # Sort languages by their display names
    source_langs = sorted(source_langs, key=lambda x: source_languages[x])
    # st.write(source_langs)
    default_src_index = source_langs.index('EN')
    source_lang = st.selectbox(
        "Select Source Language (default='EN')",
        options=['auto'] + source_langs,
        index=default_src_index+1,
        format_func=lambda x: 'Auto-detect' if x == 'auto' else source_languages.get(x, x)
    )
        
# Create two columns for source and target text
col1, col2 = st.columns(2)

with col1:
    st.subheader("Source Text")
    source_text = st.text_area("Enter text to translate", height=350)
    
    if source_text:
        try:
            # Detect source language only if auto is selected
            if source_lang == "auto":
                _, detected_lang, _ = translator.translate(source_text, "EN-US")
                if detected_lang:
                    st.info(f"Detected source language: {detected_lang}")
        except TranslationError as e:
            st.error(f"Error detecting language: {str(e)}")
            detected_lang = ""

    # Translate button
    if st.button("Translate") and source_text:
        try:
            translated_text, detected_lang, alt_text = translator.translate(
                source_text, 
                target_lang, 
                source_lang
            )
            if translated_text:
                st.session_state.translated_text = translated_text
        except TranslationError as e:
            st.error(str(e))

with col2:
    st.subheader("Translated Text")
    
    # Initialize translated text
    if 'translated_text' not in st.session_state:
        st.session_state.translated_text = ""
              
    # Editable translation output
    translated_text = st.text_area(
        "Translated text (editable)",
        value=st.session_state.translated_text,
        height=250
    )

    # Note input with alternatives
    note = st.text_area(
        "Notes (optional)", 
        value=st.session_state.get('alt_text', ""),
        placeholder="Add any comments, TODOs, or research items here", 
        height=100
    )

col_1, _, col_2, _ = st.columns([2,1,2,4])
with col_1:
    st.warning("If the translation looks good to you, please click Save button !")

with col_2:
    # Save button
    if st.button("Save"):
        if source_text and translated_text:
            try:
                db.save_translation(
                    project=st.session_state.current_project,
                    source_text=source_text,
                    target_text=translated_text,
                    source_lang=source_lang if source_lang != "auto" else detected_lang,
                    target_lang=target_lang,
                    provider=provider,
                    note=note,
                    user=None  # We'll add user handling later
                )
                st.success("Translation saved successfully!")
            except Exception as e:
                st.error(f"Error saving translation: {str(e)}")
        else:
            st.warning("Please provide both source and target text")