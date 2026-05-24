import type { ReviewAnalysis } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const API_TOKEN = process.env.NEXT_PUBLIC_MCP_AUTH_TOKEN;

export async function analyzeProduct(url: string): Promise<ReviewAnalysis> {
  const response = await fetch(`${API_BASE_URL}/api/products/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(API_TOKEN ? { Authorization: `Bearer ${API_TOKEN}` } : {})
    },
    body: JSON.stringify({ url })
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Analiz yapılamadı." }));
    throw new Error(error.message ?? "Analiz yapılamadı.");
  }
  return response.json();
}
