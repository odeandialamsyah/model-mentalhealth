import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text: str) -> str:
    text = text.lower()  # Mengubah semua teks menjadi huruf kecil
    text = re.sub(r'\[.*?\]', '', text)  # Menghapus teks yang tertutup kurung siku
    text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Menghapus URL/link
    text = re.sub(r'<.*?>+', '', text)  # Menghapus tag HTML
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)  # Menghapus semua tanda baca
    text = re.sub(r'\n', '', text)  # Menghapus karakter baris baru
    text = re.sub(r'\w*\d\w*', '', text)  # Menghapus kata yang mengandung angka
    tokens = word_tokenize(text)
    tokens = [
        lemmatizer.lemmatize(w)
        for w in tokens
        if w.isalpha() and w not in stop_words
    ]
    return " ".join(tokens)
