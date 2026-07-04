'use client';

import { useState } from 'react';
import type { StudentRow } from '@/lib/types';

interface Props {
  rows:    StudentRow[];
  columns: string[];
}

function gradeClass(grade: string | number): string {
  const g = String(grade).trim().toUpperCase();
  switch (g) {
    case '7': return 'bg-emerald-100 text-emerald-800 font-semibold';
    case '6': return 'bg-green-50 text-green-700 font-semibold';
    case '5': return 'bg-lime-50 text-lime-700';
    case '4': return 'bg-yellow-50 text-yellow-700';
    case '3': return 'bg-orange-50 text-orange-700';
    case '2':
    case '1': return 'bg-red-50 text-red-700';
    case 'A': return 'bg-violet-100 text-violet-800 font-semibold';
    case 'B': return 'bg-indigo-50 text-indigo-700';
    case 'C': return 'bg-slate-50 text-slate-600';
    case 'D':
    case 'E': return 'bg-slate-50 text-slate-400';
    default:  return 'bg-amber-50 text-amber-700';
  }
}

function GradeCell({ value }: { value: string | number }) {
  const str = String(value ?? '—');
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs ${gradeClass(str)}`}>
      {str}
    </span>
  );
}

export default function StudentTable({ rows, columns }: Props) {
  const [sortAsc, setSortAsc] = useState(false);

  const sorted = [...rows].sort((a, b) =>
    sortAsc ? a.total - b.total : b.total - a.total
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs text-slate-500">{rows.length} students</p>
        <button
          onClick={() => setSortAsc(p => !p)}
          className="text-xs px-3 py-1 rounded-full border border-slate-200 text-slate-500 hover:bg-slate-50 transition-colors"
        >
          Sort: {sortAsc ? 'Lowest first ↑' : 'Highest first ↓'}
        </button>
      </div>

      <div className="overflow-x-auto scrollbar-thin rounded-lg border border-slate-100">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-slate-50 text-left border-b border-slate-100">
              <th className="px-3 py-2.5 font-semibold text-slate-500 text-xs w-8">#</th>
              <th className="px-3 py-2.5 font-semibold text-slate-600 text-xs whitespace-nowrap sticky left-0 bg-slate-50 min-w-[160px]">Name</th>
              {columns.map(col => (
                <th key={col} className="px-3 py-2.5 font-semibold text-slate-500 text-xs whitespace-nowrap max-w-[120px]">
                  <span className="block truncate max-w-[110px]" title={col}>{col}</span>
                </th>
              ))}
              <th className="px-3 py-2.5 font-semibold text-[#22B9C3] text-xs whitespace-nowrap">Total</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((row, idx) => (
              <tr
                key={row.name}
                className={`border-b border-slate-50 transition-colors hover:bg-slate-50 ${idx % 2 === 0 ? '' : 'bg-slate-50/40'}`}
              >
                <td className="px-3 py-2.5 text-slate-400 text-xs">{idx + 1}</td>
                <td className="px-3 py-2.5 font-medium text-slate-800 whitespace-nowrap sticky left-0 bg-white">
                  {row.name}
                </td>
                {columns.map(col => (
                  <td key={col} className="px-3 py-2.5 text-center">
                    {row[col] !== undefined
                      ? <GradeCell value={row[col]} />
                      : <span className="text-slate-200">—</span>}
                  </td>
                ))}
                <td className="px-3 py-2.5 text-center">
                  <span className="inline-block px-2 py-0.5 rounded text-xs bg-[#E0F7FA] text-[#0097A7] font-bold">
                    {row.total}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
