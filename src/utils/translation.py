# src/utils/translation.py
from abc import ABC, abstractmethod
import deepl
from google.cloud import translate_v2 as translate
# from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
# from azure.core.exceptions import ServiceRequestError, ClientAuthenticationError
import os
import requests # For Microsoft Translator language list
from typing import Tuple, List, Dict, Optional

class TranslationProvider(ABC):
    """Abstract base class for translation providers"""
    
    @abstractmethod
    def get_source_languages(self) -> Dict[str, str]:
        """Get available source languages"""
        pass

    @abstractmethod
    def get_target_languages(self) -> Dict[str, str]:
        """Get available target languages"""
        pass

    @abstractmethod
    def translate(self, text: str, target_lang: str, source_lang: str = "auto") -> Tuple[str, str, str]:
        """
        Translate text
        Returns: (translated_text, detected_language, alternatives_note)
        """
        pass

    @abstractmethod
    def get_alternatives(self, text: str, target_lang: str, num_alternatives: int = 3) -> List[str]:
        """Get alternative translations"""
        pass

class DeepLTranslator(TranslationProvider):
    def __init__(self, auth_key: str):
        self.translator = deepl.Translator(auth_key)

    def get_source_languages(self) -> Dict[str, str]:
        return {lang.code: lang.name for lang in self.translator.get_source_languages()}

    def get_target_languages(self) -> Dict[str, str]:
        return {lang.code: lang.name for lang in self.translator.get_target_languages()}

    def get_alternatives(self, text: str, target_lang: str, num_alternatives: int = 3) -> List[str]:
        try:
            alternatives = []
            for _ in range(num_alternatives):
                result = self.translator.translate_text(
                    text,
                    target_lang=target_lang,
                    formality="default"
                )
                if result.text not in alternatives:
                    alternatives.append(result.text)
            return alternatives
        except:
            return []

    def translate(self, text: str, target_lang: str, source_lang: str = "auto") -> Tuple[str, str, str]:
        try:
            if source_lang == "auto":
                source_lang_result = self.translator.translate_text(text, target_lang="EN-US")
                detected_lang = source_lang_result.detected_source_lang
            else:
                detected_lang = source_lang
            
            translation_result = self.translator.translate_text(
                text, 
                target_lang=target_lang,
                source_lang=detected_lang
            )
            
            alternatives = self.get_alternatives(text, target_lang)
            alternatives = [alt for alt in alternatives if alt != translation_result.text]
            
            alt_text = ""
            if alternatives:
                alt_text = "Alternative translations:\n" + "\n".join(f"• {alt}" for alt in alternatives)
            
            return translation_result.text, detected_lang, alt_text
            
        except Exception as e:
            raise TranslationError(f"Translation failed: {str(e)}")

class GoogleTranslator(TranslationProvider):
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initializes the Google Translator.
        Expects GOOGLE_APPLICATION_CREDENTIALS environment variable to be set,
        or credentials_path to be provided.
        """
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        try:
            self.client = translate.Client()
            # Attempt a simple call to ensure credentials are valid
            self.client.get_languages(target_language='en')
        except Exception as e:
            raise TranslationError(f"Failed to initialize Google Translate client: {e}. Ensure GOOGLE_APPLICATION_CREDENTIALS is set correctly.")

    def get_source_languages(self) -> Dict[str, str]:
        try:
            languages = self.client.get_languages(target_language='en') # target_language for language names
            return {lang['language']: lang['name'] for lang in languages}
        except Exception as e:
            raise TranslationError(f"Google: Error fetching source languages: {str(e)}")

    def get_target_languages(self) -> Dict[str, str]:
        try:
            languages = self.client.get_languages(target_language='en') # target_language for language names
            # Google Translate API v2 supports the same set for source and target
            return {lang['language']: lang['name'] for lang in languages}
        except Exception as e:
            raise TranslationError(f"Google: Error fetching target languages: {str(e)}")

    def get_alternatives(self, text: str, target_lang: str, num_alternatives: int = 3) -> List[str]:
        # Google Translate API v2 (google-cloud-translate library) does not directly support alternatives.
        # Returning an empty list as per plan.
        return []

    def translate(self, text: str, target_lang: str, source_lang: str = "auto") -> Tuple[str, str, str]:
        try:
            if source_lang == "auto" or not source_lang:
                # Detect language first
                detection_result = self.client.detect_language([text])
                detected_lang = detection_result[0]['language']
                # Google API might return 'und' for undefined if detection is poor
                if detected_lang == 'und':
                    raise TranslationError("Google: Could not reliably detect source language.")
            else:
                detected_lang = source_lang

            # Perform translation
            # The client.translate method can take a source_language argument.
            # If it's not provided, Google Translate attempts to detect it.
            # However, we provide detected_lang for consistency and explicit control.
            result = self.client.translate(
                text,
                target_language=target_lang,
                source_language=detected_lang if detected_lang != "auto" else None
            )

            translated_text = result['translatedText']
            # The 'detectedSourceLanguage' might be present if source_language was not specified
            # or if there was a mismatch. We rely on our earlier detection.

            # Alternatives are not supported by this API version directly
            alt_text = "Alternative translations not supported by Google Translate API v2."

            return translated_text, detected_lang, alt_text

        except Exception as e:
            raise TranslationError(f"Google: Translation failed: {str(e)}")

# class MicrosoftTranslator(TranslationProvider):
#     def __init__(self, api_key: str, region: str, endpoint: str = "https://api.cognitive.microsofttranslator.com/"):
#         """
#         Initializes the Microsoft Translator.
#         Requires API key and region. Endpoint is optional.
#         """
#         if not api_key:
#             raise TranslationError("Microsoft Translator: API key is required.")
#         if not region:
#             raise TranslationError("Microsoft Translator: Region is required.")

#         self.api_key = api_key
#         self.region = region
#         self.endpoint = endpoint
#         try:
#             credential = TranslatorCredential(self.api_key, self.region)
#             self.client = TextTranslationClient(endpoint=self.endpoint, credential=credential)
#             # Attempt a simple call to validate credentials somewhat (e.g., list languages)
#             self._get_ms_languages()
#         except ClientAuthenticationError as e:
#             raise TranslationError(f"Microsoft Translator: Authentication failed. Check API key and region. Details: {e}")
#         except ServiceRequestError as e:
#             raise TranslationError(f"Microsoft Translator: Service request error during initialization. Check endpoint and network. Details: {e}")
#         except Exception as e:
#             raise TranslationError(f"Microsoft Translator: Failed to initialize client: {e}")

#     def _get_ms_languages(self, scope="translation") -> Dict:
#         """Helper to fetch languages from Microsoft Translator API."""
#         # The SDK does not have a direct method to list all languages with their names easily for v3.
#         # We use the REST API endpoint for this.
#         url = f"{self.endpoint.rstrip('/')}/languages?api-version=3.0&scope={scope}"
#         headers = {
#             'Accept-Language': 'en' # Get language names in English
#         }
#         try:
#             response = requests.get(url, headers=headers, timeout=10)
#             response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             raise TranslationError(f"Microsoft Translator: Error fetching languages from REST API: {e}")

#     def get_source_languages(self) -> Dict[str, str]:
#         try:
#             languages_response = self._get_ms_languages()
#             # The response structure is like: {"translation": {"ar": {"name": "Arabic", "nativeName": "العربية", "dir": "rtl"}}}
#             return {code: data["name"] for code, data in languages_response.get("translation", {}).items()}
#         except Exception as e:
#             # Catching generic Exception as _get_ms_languages can raise TranslationError
#             raise TranslationError(f"Microsoft Translator: Error processing source languages: {str(e)}")

#     def get_target_languages(self) -> Dict[str, str]:
#         # For Microsoft Translator, source and target languages are generally the same.
#         return self.get_source_languages()

#     def get_alternatives(self, text: str, target_lang: str, num_alternatives: int = 3) -> List[str]:
#         # Microsoft Translator API (v3) does not directly support multiple alternative translations
#         # in a single call in the same way DeepL does.
#         # The 'Translate' method returns only one primary translation.
#         return []

#     def translate(self, text: str, target_lang: str, source_lang: str = "auto") -> Tuple[str, str, str]:
#         try:
#             detected_language = source_lang

#             if source_lang == "auto" or not source_lang:
#                 # Perform detection if source_lang is 'auto'
#                 detect_response = self.client.detect_language(content=[text])
#                 if detect_response and len(detect_response) > 0 and detect_response[0].primary_language:
#                     detected_language = detect_response[0].primary_language.language_code
#                 else:
#                     raise TranslationError("Microsoft Translator: Could not reliably detect source language.")

#             if not detected_language or detected_language == "auto": # Should not happen if detection worked
#                  raise TranslationError("Microsoft Translator: Invalid or undetected source language for translation.")

#             # Perform translation
#             # The SDK expects a list of strings for text_content
#             response = self.client.translate(
#                 content=[text],
#                 to_language=[target_lang],
#                 from_language=detected_language if detected_language != "auto" else None
#             )

#             if response and len(response) > 0 and response[0].translations:
#                 translated_text = response[0].translations[0].text
#                 # The response also contains `detected_language_info` if `from_language` was not specified.
#                 # We use our own `detected_language` from the separate call or input.
#                 if response[0].detected_language_info and detected_language == "auto": # Update if auto was used and SDK detected
#                     detected_language = response[0].detected_language_info.language_code

#             else:
#                 raise TranslationError("Microsoft Translator: No translation returned from API.")

#             alt_text = "Alternative translations not supported by Microsoft Translator."

#             return translated_text, detected_language, alt_text

#         except ClientAuthenticationError as e:
#             raise TranslationError(f"Microsoft Translator: Authentication failed during translation. Check API key and region. Details: {e}")
#         except ServiceRequestError as e:
#             raise TranslationError(f"Microsoft Translator: Service error during translation. Details: {e}")
#         except Exception as e:
#             raise TranslationError(f"Microsoft Translator: Translation failed: {str(e)}")


class TranslationError(Exception):
    """Custom exception for translation errors"""
    pass

def create_translator(provider: str, **kwargs) -> TranslationProvider:
    """Factory function to create appropriate translator instance"""
    providers = {
        "DeepL": DeepLTranslator,
        "Google Translate": GoogleTranslator, # Renaming for clarity in UI
        # "Microsoft Translator": MicrosoftTranslator,
    }
    
    if provider not in providers:
        raise ValueError(f"Unsupported provider: {provider}")
        
    return providers[provider](**kwargs)