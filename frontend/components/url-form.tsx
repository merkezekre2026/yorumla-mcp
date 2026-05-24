"use client";

import { FormEvent, useState } from "react";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function UrlForm({ onSubmit, loading }: { onSubmit: (url: string) => void; loading: boolean }) {
  const [url, setUrl] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    onSubmit(url);
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-3 sm:flex-row">
      <Input
        value={url}
        onChange={(event) => setUrl(event.target.value)}
        placeholder="https://www.hepsiburada.com/..."
        aria-label="Hepsiburada ürün URL'i"
      />
      <Button disabled={loading || !url.trim()} className="gap-2">
        <Search className="h-4 w-4" />
        {loading ? "Analiz ediliyor" : "Analiz Et"}
      </Button>
    </form>
  );
}
