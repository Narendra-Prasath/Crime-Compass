import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RotateCcw, Home, Compass } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallbackTitle?: string;
  onReset?: () => void;
  onNavigateHome?: () => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught rendering error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div
          role="alert"
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--accent-rose-border, rgba(244, 63, 94, 0.4))',
            borderRadius: 'var(--radius-lg, 12px)',
            padding: '32px',
            margin: '24px 0',
            boxShadow: 'var(--shadow-md, 0 4px 20px rgba(0,0,0,0.3))',
            maxWidth: '900px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '16px' }}>
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '10px',
                background: 'rgba(244, 63, 94, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--accent-rose, #f43f5e)'
              }}
            >
              <AlertTriangle size={24} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0, color: 'var(--text-main)' }}>
                {this.props.fallbackTitle || 'Rendering Error Prevented Blank Page'}
              </h2>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', margin: '4px 0 0' }}>
                Crime Compass detected an unexpected rendering issue and prevented the page from becoming blank. Navigation remains intact.
              </p>
            </div>
          </div>

          <div
            style={{
              background: 'rgba(0, 0, 0, 0.3)',
              borderRadius: 'var(--radius-md, 8px)',
              padding: '14px 18px',
              border: '1px solid var(--border-subtle)',
              marginBottom: '20px',
              fontSize: '0.82rem',
              color: 'var(--accent-rose, #f43f5e)',
              fontFamily: 'var(--font-mono, monospace)',
              overflowX: 'auto'
            }}
          >
            {this.state.error?.message || 'An unknown rendering exception occurred.'}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <button
              type="button"
              className="btn btn-primary"
              onClick={this.handleReset}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              <RotateCcw size={16} />
              <span>Retry / Recover View</span>
            </button>

            {this.props.onNavigateHome && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={this.props.onNavigateHome}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
              >
                <Home size={16} />
                <span>Return to Home</span>
              </button>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
