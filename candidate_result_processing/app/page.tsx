'use client';

import { useState } from 'react';
import FileUpload from '@/components/FileUpload';
import Dashboard from '@/components/Dashboard';
import type { ExtractionResult } from '@/lib/types';

export default function Home() {
  const [result, setResult]   = useState<ExtractionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append('file', file);
      const res  = await fetch('/api/extract', { method: 'POST', body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? 'Extraction failed');
      setResult(data as ExtractionResult);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return <Dashboard result={result} onReset={() => setResult(null)} />;
  }

  return <FileUpload onUpload={handleUpload} loading={loading} error={error} />;
}
