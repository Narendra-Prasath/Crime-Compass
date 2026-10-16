import React from 'react';
import { AlertCircle, FolderOpen, RefreshCw } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ message = 'Analyzing behavioral patterns...' }) => (
  <div className="state-box" role="status" aria-live="polite">
    <div className="spinner" style={{ marginBottom: '16px' }}></div>
    <div className="state-title">Processing</div>
    <div className="state-desc">{message}</div>
  </div>
);

interface ErrorStateProps {
  error: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({ error, onRetry }) => (
  <div className="state-box" role="alert" style={{ borderColor: 'var(--accent-rose-border)' }}>
    <AlertCircle className="state-icon" size={36} style={{ color: 'var(--accent-rose)' }} />
    <div className="state-title" style={{ color: 'var(--accent-rose)' }}>Unable to Complete Request</div>
    <div className="state-desc">{error}</div>
    {onRetry && (
      <button
        type="button"
        className="btn btn-secondary"
        onClick={onRetry}
        style={{ marginTop: '16px' }}
        aria-label="Retry action"
      >
        <RefreshCw size={14} /> Try Again
      </button>
    )}
  </div>
);

interface EmptyStateProps {
  title?: string;
  message?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No Incidents Found',
  message = 'Try searching with a valid incident identifier (e.g. INC_136975) or select one of the suggested sample cases.',
  action,
}) => (
  <div className="state-box">
    <FolderOpen className="state-icon" size={36} />
    <div className="state-title">{title}</div>
    <div className="state-desc">{message}</div>
    {action && (
      <button
        type="button"
        className="btn btn-primary"
        onClick={action.onClick}
        style={{ marginTop: '16px' }}
      >
        {action.label}
      </button>
    )}
  </div>
);
