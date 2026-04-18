import { useState } from 'react';
import InputBox from './components/InputBox';
import ResultsGrid from './components/ResultsGrid';
import SmarterDecision from './components/SmarterDecision';
import ProjectionSection from './components/ProjectionSection';

export default function App() {
  const [scenario, setScenario] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSimulate() {
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const res = await fetch('/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error ?? `Server error ${res.status}`);
      }
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      <div className="mx-auto max-w-[960px] px-4 py-12 flex flex-col gap-10">
        {/* Header */}
        <header className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900">
            ⚡ Consequence Engine
          </h1>
          <p className="mt-2 text-slate-500 text-base">
            Enter a decision scenario and explore probable outcomes with reasoning, ripple effects, and a 30-day projection.
          </p>
        </header>

        {/* Input */}
        <InputBox
          scenario={scenario}
          onChange={setScenario}
          onSubmit={handleSimulate}
          loading={loading}
        />

        {/* Error */}
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <section className="flex flex-col gap-8">
            <ResultsGrid outcomes={result.outcomes} />
            <SmarterDecision text={result.betterDecision} />
            <ProjectionSection projection={result.projection} />
          </section>
        )}
      </div>
    </div>
  );
}
