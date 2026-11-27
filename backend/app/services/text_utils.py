"""Small text helpers shared by keyword search and option matching.

Works for English, Roman Urdu/Sindhi and Urdu/Sindhi in Arabic script. Arabic-script
text is folded so that common keyboard variants compare equal: diacritics (zer, zabar,
hamza marks) are dropped, Arabic/Urdu/Sindhi forms of yeh and heh are unified, and
Urdu/Arabic-Indic digits become 0-9. Both the farmer's text and the data go through the
same folding, so this only affects matching, never what is displayed.
"""
import re
import unicodedata

_TOKEN_RE = re.compile(r"[^\W_]+")

_FOLD = str.maketrans(
    {
        "ي": "ی",  # Arabic yeh (used in Sindhi) -> Farsi/Urdu yeh
        "ى": "ی",  # alef maksura -> yeh
        "ہ": "ه",  # Urdu heh goal -> heh
        "ە": "ه",  # ae -> heh
        "ة": "ه",  # teh marbuta -> heh
        "ك": "ک",  # Arabic kaf -> keheh (Urdu kaf). Sindhi's own kaf (U+06AA) is left alone.
        **{chr(0x06F0 + i): str(i) for i in range(10)},  # Extended Arabic-Indic (Urdu) digits
        **{chr(0x0660 + i): str(i) for i in range(10)},  # Arabic-Indic digits
    }
)

_STOPWORDS_RAW = (
    # English
    "a an and are about can do does for from give how i in is it me my of on or please should "
    "tell the to what which with you your "
    # Roman Urdu / Sindhi
    # ("when" words stay searchable: "when" is a knowledge-base keyword in every language.)
    "kya kaise kese mein main ki ka ke hai hain ko se par aur ya mujhe mera meri batao bataen "
    "karna karen chahiye kitna kitni kon kaun liye "
    # Urdu
    "کیا کیسے کیسا کس میں کی کا کے ہے ہیں ہو کو سے پر اور یا مجھے میرا میری میرے بتائیں بتاؤ "
    "کریں کرنا کروں چاہیے چاہئے کتنا کتنی کتنے کون کونسا کونسی یہ وہ لیے لئے "
    # Sindhi
    "ڇا ڪيئن ڪيترو ڪيتري ڪيترا ڪهڙو ڪهڙي ڪهڙا ۾ جو جي جا آهي آهن کي کان تي يا مون "
    "منهنجو منهنجي ٻڌايو ڪريان ڪرڻ ڪريون گهرجي هي اهو لاءِ"
)


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    # Drop combining marks (diacritics) and format characters such as zero-width non-joiners.
    stripped = "".join(c for c in decomposed if unicodedata.category(c) not in ("Mn", "Cf"))
    return stripped.translate(_FOLD)


def normalize(text: str | None) -> str:
    return " ".join(_TOKEN_RE.findall(_fold(text or "")))


STOPWORDS = frozenset(normalize(_STOPWORDS_RAW).split())


def stem(token: str) -> str:
    """Very light English stemming: sowing -> sow, seeds -> seed, dates -> date."""
    if not token.isascii():
        return token
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def tokens(text: str | None, drop_stopwords: bool = False) -> list[str]:
    words = normalize(text).split()
    if drop_stopwords:
        words = [w for w in words if w not in STOPWORDS]
    return [stem(w) for w in words]
