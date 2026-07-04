'use client';

import { useState } from 'react';
import type { ExtractionResult } from '@/lib/types';
import StudentTable from './StudentTable';
import { SubjectAveragesChart, ThresholdChart } from './Charts';

interface Props {
  result:  ExtractionResult;
  onReset: () => void;
}

type Tab = 'overview' | 'diploma' | 'courses';

function downloadExcel(base64: string) {
  const bytes  = atob(base64);
  const arr    = new Uint8Array(bytes.length);
  for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
  const blob   = new Blob([arr], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  const url    = URL.createObjectURL(blob);
  const a      = document.createElement('a');
  a.href       = url;
  a.download   = 'extracted_results.xlsx';
  a.click();
  URL.revokeObjectURL(url);
}

function MetricCard({ icon, label, value }: { icon: string; label: string; value: string }) {
  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5 flex items-center gap-4">
      <span className="text-3xl">{icon}</span>
      <div>
        <p className="text-xs text-slate-500 uppercase tracking-wide font-medium">{label}</p>
        <p className="text-2xl font-bold text-slate-800 mt-0.5">{value}</p>
      </div>
    </div>
  );
}

export default function Dashboard({ result, onReset }: Props) {
  const [tab, setTab] = useState<Tab>('overview');
  const { analytics, messages, excel_base64 } = result;

  const tabs: { id: Tab; label: string }[] = [
    { id: 'overview', label: '📊 Overview'          },
    { id: 'diploma',  label: '🎓 Diploma Students'  },
    { id: 'courses',  label: '📚 Courses Students'  },
  ];

  const warnings = messages.filter(m => m.type === 'warning');
  const errors   = messages.filter(m => m.type === 'error');

  // Build threshold chart data
  const thresholdData = Object.entries(analytics.thresholds).map(([k, v]) => ({
    threshold: k,
    students:  v,
  }));

  // Build subject averages chart data (sorted descending)
  const avgData = Object.entries(analytics.subject_averages)
    .sort((a, b) => b[1] - a[1])
    .map(([subject, average]) => ({ subject, average }));

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">

      {/* ── Top bar ── */}
      <header className="sticky top-0 z-10 bg-white border-b border-slate-100 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🎓</span>
            <h1 className="text-lg font-bold text-slate-800">IB Results Extractor</h1>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onReset}
              className="px-4 py-2 rounded-lg text-sm font-medium border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors"
            >
              ↑ Upload New File
            </button>
            {excel_base64 && (
              <button
                onClick={() => downloadExcel(excel_base64)}
                className="px-4 py-2 rounded-lg text-sm font-semibold text-white bg-[#30CDD7] hover:bg-[#22B9C3] transition-colors flex items-center gap-1.5"
              >
                <span>📥</span> Download Excel
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 w-full flex-1 space-y-6">

        {/* ── Messages ── */}
        {messages.length > 0 && (
          <div className="space-y-2">
            {errors.map((m, i) => (
              <div key={i} className="flex gap-2 items-start p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                <span className="shrink-0">❌</span>
                <span>{m.message}</span>
              </div>
            ))}
            {warnings.map((m, i) => (
              <div key={i} className="flex gap-2 items-start p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-sm">
                <span className="shrink-0">⚠️</span>
                <span>{m.message}</span>
              </div>
            ))}
          </div>
        )}

        {/* ── Metrics ── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard icon="🎓" label="Diploma students"    value={String(result.diploma_rows.length)} />
          <MetricCard icon="📚" label="Courses students"    value={String(result.courses_rows.length)} />
          <MetricCard icon="📈" label="Avg diploma score"   value={analytics.avg_diploma ? `${analytics.avg_diploma}` : '—'} />
          <MetricCard icon="🎯" label="Scoring ≥ 40"        value={analytics.diploma_totals.length ? `${analytics.percent_40_plus}%` : '—'} />
        </div>

        {/* ── Tabs ── */}
        <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
          <div className="flex border-b border-slate-100">
            {tabs.map(t => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`
                  px-5 py-3 text-sm font-medium transition-colors border-b-2
                  ${tab === t.id
                    ? 'border-[#30CDD7] text-[#30CDD7]'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50'}
                `}
              >
                {t.label}
              </button>
            ))}
          </div>

          <div className="p-6">

            {/* ── Overview ── */}
            {tab === 'overview' && (
              <div className="space-y-8">
                {/* Avg subject scores */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="bg-slate-50 rounded-xl p-5 text-center">
                    <p className="text-xs text-slate-500 uppercase tracking-wide font-medium mb-1">Avg Subject Score — Diploma</p>
                    <p className="text-3xl font-bold text-slate-800">{analytics.avg_diploma_subject}</p>
                    <p className="text-xs text-slate-400 mt-1">out of 7</p>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-5 text-center">
                    <p className="text-xs text-slate-500 uppercase tracking-wide font-medium mb-1">Avg Subject Score — Courses</p>
                    <p className="text-3xl font-bold text-slate-800">{analytics.avg_courses_subject}</p>
                    <p className="text-xs text-slate-400 mt-1">out of 7</p>
                  </div>
                </div>

                {/* Threshold chart */}
                {analytics.diploma_totals.length > 0 && thresholdData.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-slate-600 mb-4">Diploma students scoring above threshold</h3>
                    <ThresholdChart data={thresholdData} />
                  </div>
                )}

                {/* Subject averages chart */}
                {avgData.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-slate-600 mb-4">Subject averages</h3>
                    <SubjectAveragesChart data={avgData} />
                  </div>
                )}
              </div>
            )}

            {/* ── Diploma students ── */}
            {tab === 'diploma' && (
              result.diploma_rows.length > 0
                ? <StudentTable rows={result.diploma_rows} columns={result.diploma_cols} />
                : <p className="text-slate-400 text-sm py-4">No diploma students found.</p>
            )}

            {/* ── Courses students ── */}
            {tab === 'courses' && (
              result.courses_rows.length > 0
                ? <StudentTable rows={result.courses_rows} columns={result.courses_cols} />
                : <p className="text-slate-400 text-sm py-4">No courses students found.</p>
            )}

          </div>
        </div>
      </main>
    </div>
  );
}
