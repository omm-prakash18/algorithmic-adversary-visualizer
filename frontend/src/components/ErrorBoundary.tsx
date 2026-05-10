import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen w-screen bg-slate-950 flex flex-col items-center justify-center p-8 text-center font-mono">
          <div className="text-red-500 text-2xl font-bold mb-4 uppercase tracking-widest">System Kernel Panic</div>
          <div className="bg-slate-900 border border-red-500/30 p-6 rounded-lg max-w-2xl w-full overflow-hidden">
            <pre className="text-xs text-red-400 whitespace-pre-wrap text-left leading-relaxed">
              {this.state.error?.stack}
            </pre>
          </div>
          <button 
            onClick={() => window.location.reload()}
            className="mt-8 px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs rounded uppercase tracking-widest transition"
          >
            Reboot System
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
