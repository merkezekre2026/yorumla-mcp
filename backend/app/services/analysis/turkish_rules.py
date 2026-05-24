import re
from collections import Counter
from app.schemas.analysis import TopicSummary
from app.schemas.reviews import Review


COMPLAINT_KEYWORDS: dict[str, list[str]] = {
    "Kargo ve teslimat": ["kargo", "geç geldi", "gecikti", "teslimat", "kurye", "dağıtım", "hasarlı geldi"],
    "Paketleme": ["paket", "paketleme", "ezik", "yırtık", "korumasız", "kutusu açık"],
    "Kalite": ["kalitesiz", "dayanıksız", "bozuldu", "kırıldı", "çizik", "defolu", "arıza", "sorunlu"],
    "Satıcı": ["satıcı", "mağaza", "ilgisiz", "cevap vermedi", "yanlış ürün", "eksik ürün"],
    "İade ve destek": ["iade", "değişim", "servis", "garanti", "müşteri hizmetleri", "para iadesi"],
    "Performans": ["performans", "yavaş", "ısınma", "batarya", "çekmiyor", "sesli çalışıyor"],
}

PRAISE_KEYWORDS: dict[str, list[str]] = {
    "Fiyat/performans": ["fiyat performans", "f/p", "parasını hak", "uygun fiyat", "değer"],
    "Kalite": ["kaliteli", "sağlam", "başarılı", "güzel", "memnun", "orijinal"],
    "Hızlı teslimat": ["hızlı geldi", "çabuk geldi", "ertesi gün", "hızlı teslimat", "kargo hızlı"],
    "Paketleme": ["iyi paketlenmiş", "paketleme güzel", "özenli paket", "sağlam paket"],
    "Kullanım": ["kullanışlı", "pratik", "kolay", "iş görüyor", "tavsiye ederim"],
}

NEGATIVE_WORDS = ["kötü", "berbat", "pişman", "almayın", "beğenmedim", "sorun", "iade", "kalitesiz", "rezalet"]
POSITIVE_WORDS = ["iyi", "güzel", "harika", "memnun", "başarılı", "tavsiye", "kaliteli", "mükemmel"]


def normalize_text(text: str) -> str:
    text = text.casefold().replace("ı", "i")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_topics(reviews: list[Review], keyword_map: dict[str, list[str]]) -> list[TopicSummary]:
    counts: Counter[str] = Counter()
    examples: dict[str, list[str]] = {topic: [] for topic in keyword_map}
    for review in reviews:
        normalized = normalize_text(review.text)
        for topic, keywords in keyword_map.items():
            if any(normalize_text(keyword) in normalized for keyword in keywords):
                counts[topic] += 1
                if len(examples[topic]) < 3:
                    examples[topic].append(review.text[:280])
    return [
        TopicSummary(topic=topic, count=count, examples=examples[topic])
        for topic, count in counts.most_common()
        if count > 0
    ]
