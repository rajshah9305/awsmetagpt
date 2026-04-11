import React from 'react';
import { AlertCircle, RefreshCcw } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-surface px-4">
          <div className="card p-10 max-w-md w-full text-center border-t-4 border-error-500 shadow-elevation-2">
            <div className="w-16 h-16 bg-error-50 rounded-2xl flex items-center justify-center mx-auto mb-7">
              <AlertCircle className="h-8 w-8 text-error-600" />
            </div>
            <h1 className="text-2xl font-display font-bold text-neutral-900 mb-3">
              Something went wrong
            </h1>
            <p className="body-md text-neutral-500 mb-10 leading-relaxed">
              An unexpected error occurred. Please try refreshing the page or contact support if the problem persists.
            </p>
            <div className="space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <RefreshCcw className="h-4 w-4" />
                Refresh Page
              </button>
              <button
                onClick={() => this.setState({ hasError: false })}
                className="btn-secondary w-full"
              >
                Try Again
              </button>
            </div>
            {process.env.NODE_ENV === 'development' && (
              <div className="mt-8 text-left p-4 bg-neutral-100 rounded-xl overflow-auto max-h-40">
                <p className="text-xs font-mono text-error-700 whitespace-pre-wrap">
                  {this.state.error && this.state.error.toString()}
                </p>
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
