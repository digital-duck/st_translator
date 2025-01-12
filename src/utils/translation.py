# src/utils/translation.py
from abc import ABC, abstractmethod
import deepl
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
        # TODO: Implement Google Translate initialization
        pass

    def get_source_languages(self) -> Dict[str, str]:
        # TODO: Implement Google Translate source languages
        return {}

    def get_target_languages(self) -> Dict[str, str]:
        # TODO: Implement Google Translate target languages
        return {}

    def get_alternatives(self, text: str, target_lang: str, num_alternatives: int = 3) -> List[str]:
        # TODO: Implement Google Translate alternatives
        return []

    def translate(self, text: str, target_lang: str, source_lang: str = "auto") -> Tuple[str, str, str]:
        # TODO: Implement Google Translate translation
        raise NotImplementedError("Google Translate not yet implemented")

class TranslationError(Exception):
    """Custom exception for translation errors"""
    pass

def create_translator(provider: str, **kwargs) -> TranslationProvider:
    """Factory function to create appropriate translator instance"""
    providers = {
        "DeepL": DeepLTranslator,
        "Google": GoogleTranslator,
        # Add more providers here
    }
    
    if provider not in providers:
        raise ValueError(f"Unsupported provider: {provider}")
        
    return providers[provider](**kwargs)