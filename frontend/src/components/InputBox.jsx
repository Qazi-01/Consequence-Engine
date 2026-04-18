export default function InputBox({ scenario, onChange, onSubmit, loading }) {
  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!loading && scenario.trim()) onSubmit();
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <textarea
        className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-800 text-base shadow-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 placeholder:text-slate-400"
        rows={4}
        placeholder="Describe your decision scenario… e.g. 'I'm thinking about quitting my job to start a business.'"
        value={scenario}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={loading}
      />
      <button
        onClick={onSubmit}
        disabled={loading || !scenario.trim()}
        className="self-center px-8 py-3 rounded-xl bg-indigo-600 text-white font-semibold text-base shadow hover:bg-indigo-700 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Simulating…' : 'Simulate Outcome'}
      </button>
    </div>
  );
}
