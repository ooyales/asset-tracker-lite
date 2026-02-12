import { Check } from 'lucide-react';

export interface WizardStep {
  key: string;
  label: string;
  icon?: React.ReactNode;
}

interface WizardProgressProps {
  steps: WizardStep[];
  currentIndex: number;
  onStepClick?: (index: number) => void;
}

export default function WizardProgress({
  steps,
  currentIndex,
  onStepClick,
}: WizardProgressProps) {
  return (
    <div className="flex items-center gap-1 overflow-x-auto pb-2">
      {steps.map((step, idx) => {
        const isComplete = idx < currentIndex;
        const isCurrent = idx === currentIndex;
        const isClickable = onStepClick && idx <= currentIndex;

        return (
          <div key={step.key} className="flex items-center">
            {/* Step indicator */}
            <button
              disabled={!isClickable}
              onClick={() => isClickable && onStepClick?.(idx)}
              className={`flex items-center gap-2 px-3 py-2 rounded text-xs font-medium transition-colors whitespace-nowrap ${
                isCurrent
                  ? 'bg-eaw-primary text-white'
                  : isComplete
                  ? 'bg-green-50 text-eaw-success cursor-pointer hover:bg-green-100'
                  : 'bg-gray-100 text-eaw-muted'
              } ${isClickable ? 'cursor-pointer' : 'cursor-default'}`}
            >
              {isComplete ? (
                <Check size={14} />
              ) : (
                <span
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    isCurrent
                      ? 'bg-white/20 text-white'
                      : 'bg-gray-200 text-eaw-muted'
                  }`}
                >
                  {idx + 1}
                </span>
              )}
              <span className="hidden sm:inline">{step.label}</span>
            </button>

            {/* Connector */}
            {idx < steps.length - 1 && (
              <div
                className={`w-6 h-px mx-1 ${
                  idx < currentIndex ? 'bg-eaw-success' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
