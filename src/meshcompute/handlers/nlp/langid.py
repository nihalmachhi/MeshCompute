"""Language identification from character n-gram profiles."""

PROFILES = {
    "en": set("etaoinshrdlu"),
    "es": set("aeionstrldc"),
    "fr": set("easitnrulod"),
}


def detect_language(text: str) -> str:
    chars = set(text.lower())
    best = "en"
    best_score = -1
    for lang, profile in PROFILES.items():
        score = len(chars & profile)
        if score > best_score:
            best_score = score
            best = lang
    return best
