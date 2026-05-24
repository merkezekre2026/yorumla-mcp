from app.schemas.analysis import Recommendation, SellerRiskAnalysis


def quality_consistency(complaint_count: int, review_count: int) -> str:
    if review_count == 0:
        return "Yeterli veri yok."
    ratio = complaint_count / review_count
    if ratio >= 0.28:
        return "Kalite tutarlılığı zayıf; tekrarlayan ürün/arıza şikayetleri var."
    if ratio >= 0.12:
        return "Kalite tutarlılığı karışık; bazı kullanıcılar sorun yaşamış."
    return "Kalite tutarlılığı iyi görünüyor; ciddi tekrar eden sorun az."


def recommendation(sentiment: str, fake_score: int, seller_risk: SellerRiskAnalysis, complaint_count: int, review_count: int) -> tuple[Recommendation, list[str]]:
    complaint_ratio = complaint_count / max(1, review_count)
    reasons: list[str] = []
    if fake_score >= 70:
        reasons.append("Sahte yorum riski yüksek.")
    if seller_risk.risk_score >= 70:
        reasons.append("Satıcı/kargo riski yüksek.")
    if complaint_ratio >= 0.30:
        reasons.append("Şikayet oranı yüksek.")
    if sentiment == "negative":
        reasons.append("Genel duygu negatif.")
    if reasons:
        return "UZAK DUR", reasons

    cautious = []
    if fake_score >= 40:
        cautious.append("Sahte yorum riski orta seviyede.")
    if seller_risk.risk_score >= 40:
        cautious.append("Satıcı veya teslimat tarafında dikkat gerektiren sinyaller var.")
    if sentiment == "mixed":
        cautious.append("Yorumlar karışık.")
    if complaint_ratio >= 0.14:
        cautious.append("Tekrarlayan bazı şikayetler var.")
    if cautious:
        return "DİKKATLİ AL", cautious

    return "ALINIR", ["Yorum profili genel olarak olumlu, sahte yorum ve satıcı riski düşük."]
