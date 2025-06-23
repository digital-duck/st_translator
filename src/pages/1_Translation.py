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

# --- Provider Selection and Initialization ---
# Service provider and language selections
# Place provider selection first, as it determines key requirements and translator init
available_providers = [
    "DeepL", 
    "Google Translate", 
    # "Microsoft Translator"
]
col_target_lang, col_source_lang, col_provider_selector = st.columns(3)

with col_provider_selector:
    provider_name = st.selectbox(
        "Select Service Provider",
        options=available_providers,
        index=available_providers.index("Google Translate"),  # Default to DeepL
        key="provider_select" # Add a key to help Streamlit manage state if needed
    )

# Initialize translator based on selected provider
translator = None
source_languages = {}
target_languages = {}

try:
    if provider_name == "DeepL":
        DEEPL_AUTH_KEY = os.getenv('DEEPL_AUTH_KEY')
        if not DEEPL_AUTH_KEY:
            st.error("DeepL API key not found. Please set DEEPL_AUTH_KEY in your .env file.")
            st.stop()
        translator = create_translator("DeepL", auth_key=DEEPL_AUTH_KEY)
    
    elif provider_name == "Google Translate":
        GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not GOOGLE_CREDENTIALS_PATH:
            st.error("Google Cloud credentials path not found. Please set GOOGLE_APPLICATION_CREDENTIALS in your .env file.")
            st.stop()
        # The GoogleTranslator class handles the credential path via os.environ or direct path
        translator = create_translator("Google Translate", credentials_path=GOOGLE_CREDENTIALS_PATH)

    # elif provider_name == "Microsoft Translator":
    #     MS_TRANSLATOR_KEY = os.getenv('MS_TRANSLATOR_KEY')
    #     MS_TRANSLATOR_REGION = os.getenv('MS_TRANSLATOR_REGION')
    #     MS_TRANSLATOR_ENDPOINT = os.getenv('MS_TRANSLATOR_ENDPOINT', "https://api.cognitive.microsofttranslator.com/") # Default endpoint

    #     if not MS_TRANSLATOR_KEY:
    #         st.error("Microsoft Translator API key not found. Please set MS_TRANSLATOR_KEY in your .env file.")
    #         st.stop()
    #     if not MS_TRANSLATOR_REGION:
    #         st.error("Microsoft Translator region not found. Please set MS_TRANSLATOR_REGION in your .env file.")
    #         st.stop()
    #     translator = create_translator("Microsoft Translator",
    #                                    api_key=MS_TRANSLATOR_KEY,
    #                                    region=MS_TRANSLATOR_REGION,
    #                                    endpoint=MS_TRANSLATOR_ENDPOINT)
    
    if translator:
        source_languages = translator.get_source_languages()
        target_languages = translator.get_target_languages()
    else:
        # This case should ideally be caught by specific provider checks, but as a fallback:
        st.error(f"Could not initialize translator for {provider_name}.")
        st.stop()

except TranslationError as e: # Catch custom TranslationError for initialization issues
    st.error(f"Error initializing {provider_name}: {str(e)}")
    st.stop()
except Exception as e: # Catch any other unexpected errors during init
    st.error(f"An unexpected error occurred while setting up {provider_name}: {str(e)}")
    st.stop()

# --- Language Selection ---
# Now that translator is initialized and languages are fetched:
with col_target_lang:
    target_langs = list(target_languages.keys())
    # Sort languages by their display names
    target_langs = sorted(target_langs, key=lambda x: target_languages.get(x, x)) # Use .get for safety

    # Prefer ZH-HANS over ZH for better Chinese translation (specific to DeepL, adapt if needed for others)
    # For Google/MS, 'zh-CN' (Simplified) or 'zh-TW' (Traditional) are common.
    # We'll keep a generic approach for now, or select the first available Chinese variant.
    default_tgt_lang_code = None
    if target_languages: # Ensure target_languages is not empty
        potential_chinese_codes = [code for code in target_langs if "zh" in code.lower() or "chinese" in target_languages.get(code, "").lower()]
        if "ZH-HANS" in potential_chinese_codes and provider_name == "DeepL": # Specific DeepL preference
             default_tgt_lang_code = "ZH-HANS"
        elif "zh-CN" in potential_chinese_codes: # Common for Google/MS
            default_tgt_lang_code = "zh-CN"
        elif potential_chinese_codes: # Pick first available Chinese
            default_tgt_lang_code = potential_chinese_codes[0]

        if default_tgt_lang_code and default_tgt_lang_code in target_langs:
            default_tgt_index = target_langs.index(default_tgt_lang_code)
        elif target_langs: # If no Chinese or preferred not found, default to first language
            default_tgt_index = 0
        else: # No languages available
            default_tgt_index = 0
    else: # No languages loaded
        default_tgt_index = 0
        
    target_lang = st.selectbox(
        f"Select Target Language ({provider_name})",
        options=target_langs,
        index=default_tgt_index,
        format_func=lambda x: target_languages[x]
    )

with col_source_lang:
    source_langs = list(source_languages.keys())
    # Sort languages by their display names
    source_langs = sorted(source_langs, key=lambda x: source_languages.get(x,x)) # Use .get for safety

    default_src_lang_code = 'EN' # Default to English
    if source_langs: # Ensure source_languages is not empty
        if default_src_lang_code in source_langs:
            default_src_index = source_langs.index(default_src_lang_code) +1 # +1 because of 'auto'
        elif source_langs:
             default_src_index = 1 # Default to first language after 'auto' if EN not found
        else: # No languages available
            default_src_index = 0 # Only 'auto'
    else: # No languages loaded
        default_src_index = 0 # Only 'auto'

    source_lang = st.selectbox(
        f"Select Source Language ({provider_name})",
        options=['auto'] + source_langs,
        index=default_src_index,
        format_func=lambda x: 'Auto-detect' if x == 'auto' else source_languages.get(x, x)
    )
        
# Create two columns for source and target text
col1, col2 = st.columns(2)

with col1:
    st.subheader("Source Text")
    source_text = st.text_area("Enter text to translate", height=350, key="source_text_area")
    
    # Language detection display logic
    detected_lang_display = ""
    if 'detected_lang_cache' not in st.session_state:
        st.session_state.detected_lang_cache = ""

    if source_text and source_lang == "auto" and translator:
        try:
            # This is a preview detection; actual detection for translation happens on button click
            # To avoid excessive API calls, this could be debounced or manually triggered
            # For now, let's assume it's okay for a live update if source_lang is "auto"
            # However, the main detection will be tied to the "Translate" button.
            # Let's make this part less aggressive or remove live auto-detection display here
            # to prevent issues with partially typed text and API limits.
            # We will perform detection when "Translate" is clicked if source_lang is "auto".
            pass # Detection will occur on translate button press
        except TranslationError as e:
            st.warning(f"Note: Error during preliminary language detection attempt: {str(e)}")
            # Do not stop the app, just inform the user.

    # Translate button
    if st.button("Translate") and source_text and translator:
        if not target_lang:
            st.error("Please select a target language.")
        else:
            try:
                # Perform actual translation and detection (if auto)
                translated_text_val, detected_lang_val, alt_text_val = translator.translate(
                    source_text,
                    target_lang,
                    source_lang # Pass 'auto' if selected, translator handles detection
                )
                st.session_state.translated_text = translated_text_val
                st.session_state.alt_text = alt_text_val # For notes
                if source_lang == "auto":
                    st.session_state.detected_lang_cache = detected_lang_val # Cache detected language for saving
                    detected_lang_display = detected_lang_val # For immediate display
                else:
                    st.session_state.detected_lang_cache = source_lang # Use selected source lang
                    detected_lang_display = source_lang

                # Display detected language
                if detected_lang_display:
                    st.info(f"Source language used for translation: {source_languages.get(detected_lang_display, detected_lang_display)}")

            except TranslationError as e:
                st.error(f"Translation Error ({provider_name}): {str(e)}")
            except Exception as e:
                st.error(f"An unexpected error occurred during translation ({provider_name}): {str(e)}")

    # Display cached detected language if translate button was pressed and source_lang was auto
    if st.session_state.get('detected_lang_cache') and source_lang == 'auto':
        st.info(f"Last auto-detected source language: {source_languages.get(st.session_state.detected_lang_cache, st.session_state.detected_lang_cache)}")


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
        final_source_lang = st.session_state.get('detected_lang_cache', source_lang if source_lang != "auto" else None)
        if not final_source_lang: # If still None (e.g. detection failed and source_lang was 'auto')
            st.error("Could not determine source language. Please select it manually or try auto-detection again.")
        elif source_text and translated_text: # Ensure translated_text (from text_area) is used
            try:
                db.save_translation(
                    project=st.session_state.current_project,
                    source_text=source_text, # from source_text_area
                    target_text=translated_text, # from translated_text_area
                    source_lang=final_source_lang,
                    target_lang=target_lang,
                    provider=provider_name, # Use the selected provider_name
                    note=note, # from note_area
                    user=None  # We'll add user handling later
                )
                st.success("Translation saved successfully!")
            except Exception as e:
                st.error(f"Error saving translation: {str(e)}")
        else:
            st.warning("Please provide both source and target text")