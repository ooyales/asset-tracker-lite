import { useState } from 'react';
import { Upload, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import PasteArea from './PasteArea';

interface DataEntryStepProps {
  entityType: string;
  title: string;
  description: string;
  columns: string[];
  sampleData?: string;
  onImport: (data: string) => Promise<{ created: number; errors: string[] }>;
  importResult?: { created: number; errors: string[] } | null;
}

export default function DataEntryStep({
  entityType,
  title,
  description,
  columns,
  sampleData,
  onImport,
  importResult,
}: DataEntryStepProps) {
  const [pasteValue, setPasteValue] = useState('');
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(importResult || null);

  const handleImport = async () => {
    if (!pasteValue.trim()) return;
    setImporting(true);
    try {
      const res = await onImport(pasteValue);
      setResult(res);
    } catch (err: any) {
      setResult({
        created: 0,
        errors: [err?.response?.data?.error || err.message || 'Import failed'],
      });
    } finally {
      setImporting(false);
    }
  };

  return (
    <div>
      <h2 className="text-lg font-bold text-eaw-font mb-1">{title}</h2>
      <p className="text-sm text-eaw-muted mb-4">{description}</p>

      {/* Expected Columns */}
      <div className="bg-gray-50 rounded p-3 mb-4">
        <h4 className="text-xs font-semibold uppercase text-eaw-muted tracking-wide mb-2">
          Expected Columns (tab-separated)
        </h4>
        <div className="flex flex-wrap gap-1.5">
          {columns.map((col) => (
            <span
              key={col}
              className="px-2 py-0.5 bg-white border border-eaw-border rounded text-xs font-mono text-eaw-font"
            >
              {col}
            </span>
          ))}
        </div>
      </div>

      {/* Paste Area */}
      <PasteArea
        value={pasteValue}
        onChange={setPasteValue}
        entityType={entityType}
        sampleData={sampleData}
      />

      {/* Import Button */}
      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={handleImport}
          disabled={!pasteValue.trim() || importing}
          className="btn-primary"
        >
          {importing ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Upload size={16} />
          )}
          {importing ? 'Importing...' : `Import ${title}`}
        </button>

        {result && result.created > 0 && (
          <span className="flex items-center gap-1 text-sm text-eaw-success">
            <CheckCircle size={16} />
            {result.created} record{result.created !== 1 ? 's' : ''} imported
          </span>
        )}
      </div>

      {/* Errors */}
      {result && result.errors.length > 0 && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded">
          <div className="flex items-center gap-1 text-sm font-medium text-red-700 mb-1">
            <AlertCircle size={14} />
            Import Errors
          </div>
          <ul className="list-disc list-inside text-xs text-red-600 space-y-0.5">
            {result.errors.map((err, i) => (
              <li key={i}>{err}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
