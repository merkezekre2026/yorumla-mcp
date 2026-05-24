from app.schemas.analysis import SellerRiskAnalysis
from app.services.analysis.recommendation import recommendation


def test_high_risk_recommendation():
    seller = SellerRiskAnalysis(risk_score=80, risk_level="HIGH", seller_names=[], shipping_issues=[], seller_issues=[], return_refund_issues=[], evidence=[])
    rec, _ = recommendation("mixed", 75, seller, 10, 20)
    assert rec == "UZAK DUR"
