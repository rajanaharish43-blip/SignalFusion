import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import React from 'react'
import './index.css'
import App from './App.jsx'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', color: 'white', background: '#0f172a', height: '100vh', fontFamily: 'sans-serif' }}>
          <h2>Something went wrong loading the dashboard.</h2>
          <pre style={{ background: '#1e293b', padding: '10px', overflowX: 'auto', color: '#f87171' }}>
            {this.state.error?.toString()}
          </pre>
          <p>Please share this error message with the AI.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
