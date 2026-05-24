export type Recommendation = "ALINIR" | "DİKKATLİ AL" | "UZAK DUR";
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";

export interface TopicSummary {
  topic: string;
  count: number;
  examples: string[];
}

export interface Signal {
  name: string;
  score: number;
  explanation: string;
  evidence: string[];
}

export interface ReviewAnalysis {
  url: string;
  product_name?: string | null;
  review_count: number;
  rating_distribution: {
    total: number;
    average?: number | null;
    stars: Record<string, number>;
  };
  overall_sentiment: "positive" | "mixed" | "negative" | "unknown";
  summary: string;
  top_complaints: TopicSummary[];
  top_praised_features: TopicSummary[];
  shipping_issues: TopicSummary[];
  seller_risk: {
    risk_score: number;
    risk_level: RiskLevel;
    seller_names: string[];
    evidence: string[];
  };
  quality_consistency: string;
  fake_review: {
    fake_review_score: number;
    risk_level: RiskLevel;
    signals: Signal[];
  };
  purchase_recommendation: Recommendation;
  reasoning: string[];
  warnings: string[];
}
