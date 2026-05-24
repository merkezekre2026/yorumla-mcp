"use client";

import { useState } from "react";
import { AlertCircle } from "lucide-react";
import { AnalysisResult } from "@/components/analysis-result";
import { UrlForm } from "@/components/url-form";
import { analyzeProduct } from "@/lib/api";
import type { ReviewAnalysis } from "@/lib/types";

export default function Home() {
  const [analysis, setAnalysis] = useState<ReviewAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(url: string) {
    setLoading(true);
    setError(null);
    try {
      setAnalysis(await analyzeProduct(url));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analiz yapılamadı.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      <section className="mb-6 space-y-4">
        <div>
          <p className="text-sm font-medium text-primary">AI satın alma karar motoru</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-normal">Hepsiburada yorum analizi</h1>
        </div>
        <UrlForm onSubmit={handleSubmit} loading={loading} />
        {error ? (
          <div className="flex items-center gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        ) : null}
      </section>
      {analysis ? <AnalysisResult analysis={analysis} /> : null}
    </main>
  );
}
