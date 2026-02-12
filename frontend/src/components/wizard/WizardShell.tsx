import { ChevronLeft, ChevronRight } from 'lucide-react';
import WizardProgress, { type WizardStep } from './WizardProgress';

interface WizardShellProps {
  steps: WizardStep[];
  currentIndex: number;
  onNext: () => void;
  onBack: () => void;
  onStepClick: (index: number) => void;
  canNext?: boolean;
  nextLabel?: string;
  children: React.ReactNode;
}

export default function WizardShell({
  steps,
  currentIndex,
  onNext,
  onBack,
  onStepClick,
  canNext = true,
  nextLabel,
  children,
}: WizardShellProps) {
  const isFirst = currentIndex === 0;
  const isLast = currentIndex === steps.length - 1;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress */}
      <div className="eaw-card mb-4">
        <WizardProgress
          steps={steps}
          currentIndex={currentIndex}
          onStepClick={onStepClick}
        />
      </div>

      {/* Content */}
      <div className="eaw-card mb-4 min-h-[400px]">{children}</div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          disabled={isFirst}
          className="btn-secondary"
        >
          <ChevronLeft size={16} />
          Back
        </button>

        <span className="text-xs text-eaw-muted">
          Step {currentIndex + 1} of {steps.length}
        </span>

        <button
          onClick={onNext}
          disabled={!canNext}
          className={isLast ? 'btn-success' : 'btn-primary'}
        >
          {nextLabel || (isLast ? 'Finish' : 'Next')}
          {!isLast && <ChevronRight size={16} />}
        </button>
      </div>
    </div>
  );
}
