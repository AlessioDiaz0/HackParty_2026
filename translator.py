"""
Translation module using Lara Translate SDK.

Translates customer messages to English (or a chosen target language)
before classification.
"""

from lara_sdk import Translator, Credentials

from config import LARA_ACCESS_KEY_ID, LARA_ACCESS_KEY_SECRET

# Supported languages (subset — Lara supports 200+)
LANGUAGES = {
    "en": "en-US",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
    "pt": "pt-BR",
    "zh": "zh-CN",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "ru": "ru-RU",
    "ar": "ar-SA",
    "nl": "nl-NL",
    "pl": "pl-PL",
    "tr": "tr-TR",
    "hi": "hi-IN",
}


class LaraTranslator:
    """Wraps the Lara SDK for translating messages."""

    def __init__(self, target_lang: str = "en"):
        credentials = Credentials(
            access_key_id=LARA_ACCESS_KEY_ID,
            access_key_secret=LARA_ACCESS_KEY_SECRET,
        )
        self._lara = Translator(credentials)
        self.set_target(target_lang)

    def set_target(self, lang_code: str):
        """Set the target translation language (e.g. 'en', 'es', 'fr')."""
        self._target_code = lang_code
        self._target = LANGUAGES.get(lang_code, f"{lang_code}")

    @property
    def target_code(self) -> str:
        return self._target_code

    def translate(self, text: str) -> dict:
        """
        Translate text to the current target language.
        Source language is auto-detected by Lara.

        Returns dict with keys: original, translated, source_lang, target_lang.
        """
        res = self._lara.translate(text, target=self._target)

        return {
            "original": text,
            "translated": res.translation,
            "source_lang": res.source_language,
            "target_lang": self._target_code,
        }
