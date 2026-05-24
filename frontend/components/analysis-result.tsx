import { Card } from "@/components/ui/card";
import { RecommendationBadge } from "@/components/recommendation-badge";
import { RiskMeter } from "@/components/risk-meter";
import type { ReviewAnalysis, TopicSummary } from "@/lib/types";

function TopicList({ title, items }: { title: string; items: TopicSummary[] }) {
  return (
    <Card>
      <h2 className="mb-3 text-base font-semibold">{title}</h2>
      {items.length === 0 ? (
        <p className="text-sm text-muted-foreground">Belirgin sinyal yok.</p>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.topic}>
              <div className="flex items-center justify-between gap-3 text-sm font-medium">
                <span>{item.topic}</span>
                <span className="text-muted-foreground">{item.count}</span>
              </div>
              {item.examples[0] ? <p className="mt-1 text-sm text-muted-foreground">{item.examples[0]}</p> : null}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

export function AnalysisResult({ analysis }: { analysis: ReviewAnalysis }) {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Card className="lg:col-span-3">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{analysis.review_count} yorum analiz edildi</p>
            <h1 className="mt-1 text-2xl font-semibold">{analysis.product_name ?? "Hepsiburada ürünü"}</h1>
          </div>
          <RecommendationBadge value={analysis.purchase_recommendation} />
        </div>
        <p className="mt-4 text-sm leading-6 text-muted-foreground">{analysis.summary}</p>
      </Card>

      <Card>
        <RiskMeter label="Sahte yorum riski" value={analysis.fake_review.fake_review_score} />
      </Card>
      <Card>
        <RiskMeter label="Satıcı/kargo riski" value={analysis.seller_risk.risk_score} />
      </Card>
      <Card>
        <h2 className="mb-2 text-base font-semibold">Kalite tutarlılığı</h2>
        <p className="text-sm text-muted-foreground">{analysis.quality_consistency}</p>
      </Card>

      <TopicList title="Başlıca şikayetler" items={analysis.top_complaints} />
      <TopicList title="Öne çıkan övgüler" items={analysis.top_praised_features} />
      <Card>
        <h2 className="mb-3 text-base font-semibold">Karar gerekçesi</h2>
        <ul className="space-y-2 text-sm text-muted-foreground">
          {analysis.reasoning.map((reason) => <li key={reason}>{reason}</li>)}
        </ul>
      </Card>
    </div>
  );
}
