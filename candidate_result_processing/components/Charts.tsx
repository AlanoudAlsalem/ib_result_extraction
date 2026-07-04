'use client';

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, ReferenceLine,
} from 'recharts';

// ---------------------------------------------------------------------------
// Threshold line chart
// ---------------------------------------------------------------------------

interface ThresholdDatum { threshold: string; students: number; }

export function ThresholdChart({ data }: { data: ThresholdDatum[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="threshold" tick={{ fontSize: 12, fill: '#64748b' }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#64748b' }} />
        <Tooltip
          contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
          formatter={(v) => [v, 'Students']}
        />
        <Line
          type="monotone"
          dataKey="students"
          stroke="#30CDD7"
          strokeWidth={2.5}
          dot={{ fill: '#30CDD7', r: 5 }}
          activeDot={{ r: 7 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

// ---------------------------------------------------------------------------
// Subject averages horizontal bar chart
// ---------------------------------------------------------------------------

interface SubjectDatum { subject: string; average: number; }

// Truncate long subject names for the Y-axis
function truncate(str: string, n = 22) {
  return str.length > n ? str.slice(0, n) + '…' : str;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function CustomYAxisTick({ x, y, payload }: any) {
  return (
    <text x={x} y={y} dy={4} textAnchor="end" fontSize={11} fill="#64748b">
      {truncate(payload.value)}
    </text>
  );
}

export function SubjectAveragesChart({ data }: { data: SubjectDatum[] }) {
  const barHeight = 32;
  const chartHeight = Math.max(260, data.length * barHeight + 60);

  return (
    <ResponsiveContainer width="100%" height={chartHeight}>
      <BarChart
        layout="vertical"
        data={data}
        margin={{ top: 4, right: 40, left: 170, bottom: 4 }}
        barSize={18}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
        <XAxis
          type="number"
          domain={[0, 7]}
          ticks={[1, 2, 3, 4, 5, 6, 7]}
          tick={{ fontSize: 11, fill: '#64748b' }}
        />
        <YAxis
          type="category"
          dataKey="subject"
          tick={<CustomYAxisTick />}
          width={170}
        />
        <Tooltip
          contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
          formatter={(v) => [typeof v === 'number' ? v.toFixed(2) : v, 'Average']}
        />
        <ReferenceLine x={4} stroke="#e2e8f0" strokeDasharray="4 4" />
        <Bar dataKey="average" fill="#30CDD7" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
