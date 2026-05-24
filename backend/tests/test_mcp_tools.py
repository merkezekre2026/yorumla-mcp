from app.mcp.tools import TOOL_DEFINITIONS


def test_required_tools_exist():
    names = {tool["name"] for tool in TOOL_DEFINITIONS}
    assert names == {"analyze_product_reviews", "get_fake_review_score", "summarize_reviews", "seller_risk_analysis"}
