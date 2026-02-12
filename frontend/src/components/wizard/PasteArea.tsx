import { useState } from 'react';
import { Clipboard, FileText, Download } from 'lucide-react';

interface PasteAreaProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  sampleData?: string;
  entityType: string;
}

export default function PasteArea({
  value,
  onChange,
  placeholder,
  sampleData,
  entityType,
}: PasteAreaProps) {
  const [dragOver, setDragOver] = useState(false);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      onChange(text);
    } catch {
      // Clipboard permission denied
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const text = e.dataTransfer.getData('text/plain');
    if (text) {
      onChange(text);
      return;
    }
    // File drop
    const file = e.dataTransfer.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        const content = ev.target?.result as string;
        if (content) onChange(content);
      };
      reader.readAsText(file);
    }
  };

  const loadSample = () => {
    if (sampleData) onChange(sampleData);
  };

  const lineCount = value ? value.split('\n').filter((l) => l.trim()).length : 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 mb-2">
        <button onClick={handlePaste} className="btn-secondary text-xs" type="button">
          <Clipboard size={14} />
          Paste from Clipboard
        </button>
        {sampleData && (
          <button onClick={loadSample} className="btn-secondary text-xs" type="button">
            <Download size={14} />
            Load Sample Data
          </button>
        )}
      </div>

      <div
        className={`relative ${dragOver ? 'ring-2 ring-eaw-primary' : ''}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={
            placeholder ||
            `Paste tab-separated ${entityType} data here...\nFirst row should be column headers.`
          }
          className="input-field font-mono text-xs min-h-[200px] resize-y"
          rows={10}
        />
        {dragOver && (
          <div className="absolute inset-0 bg-eaw-primary/10 border-2 border-dashed border-eaw-primary rounded flex items-center justify-center">
            <div className="text-sm font-medium text-eaw-primary flex items-center gap-2">
              <FileText size={18} />
              Drop file or text here
            </div>
          </div>
        )}
      </div>

      {value && (
        <div className="text-xs text-eaw-muted">
          {lineCount} line{lineCount !== 1 ? 's' : ''} of data (including header)
        </div>
      )}
    </div>
  );
}
