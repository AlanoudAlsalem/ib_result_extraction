'use client';

import { DragEvent, useRef, useState } from 'react';

interface Props {
  onUpload: (file: File) => void;
  loading:  boolean;
  error:    string | null;
}

export default function FileUpload({ onUpload, loading, error }: Props) {
  const [dragging, setDragging]         = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const accept = (file: File) => {
    if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
      setSelectedFile(file);
    }
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) accept(file);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-cyan-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow-xl p-10 w-full max-w-lg">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🎓</div>
          <h1 className="text-3xl font-bold text-slate-800 tracking-tight">IB Results Extractor</h1>
          <p className="text-slate-500 mt-2 text-sm">Upload a candidate results PDF to extract and analyse grades</p>
        </div>

        {/* Drop zone */}
        <div
          onClick={() => !loading && inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={`
            relative border-2 border-dashed rounded-xl p-10 text-center cursor-pointer
            transition-all duration-200 select-none
            ${dragging
              ? 'border-[#30CDD7] bg-cyan-50 scale-[1.01]'
              : 'border-slate-200 hover:border-[#30CDD7] hover:bg-slate-50'}
            ${loading ? 'pointer-events-none opacity-50' : ''}
          `}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) accept(f); }}
          />
          {selectedFile ? (
            <div>
              <div className="text-4xl mb-2">📄</div>
              <p className="font-semibold text-slate-700">{selectedFile.name}</p>
              <p className="text-xs text-slate-400 mt-1">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB · Click to change
              </p>
            </div>
          ) : (
            <div>
              <div className="text-4xl mb-2">📤</div>
              <p className="font-semibold text-slate-600">Drag &amp; drop a PDF here</p>
              <p className="text-slate-400 text-sm mt-1">or click to browse</p>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm flex gap-2 items-start">
            <span>❌</span>
            <span>{error}</span>
          </div>
        )}

        {/* Submit */}
        <button
          onClick={() => selectedFile && onUpload(selectedFile)}
          disabled={!selectedFile || loading}
          className="
            mt-6 w-full py-3 px-6 rounded-xl font-semibold text-white text-sm
            bg-[#30CDD7] hover:bg-[#22B9C3] active:scale-95
            disabled:opacity-40 disabled:cursor-not-allowed
            transition-all duration-150 flex items-center justify-center gap-2
          "
        >
          {loading ? (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Processing…
            </>
          ) : (
            'Process Results'
          )}
        </button>
      </div>
    </div>
  );
}
