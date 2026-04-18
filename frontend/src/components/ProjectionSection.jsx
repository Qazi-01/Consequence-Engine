const PROJECTION_META = [
  { key: 'mentalState', label: '🧠 Mental State', color: 'text-violet-700 bg-violet-50 border-violet-100' },
  { key: 'performance', label: '📈 Performance', color: 'text-emerald-700 bg-emerald-50 border-emerald-100' },
  { key: 'riskLevel', label: '⚠️ Risk Level', color: 'text-amber-700 bg-amber-50 border-amber-100' },
];

export default function ProjectionSection({ projection }) {
  return (
    <div>
      <h2 className="text-base font-semibold text-slate-700 mb-3">📅 30-Day Projection</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {PROJECTION_META.map(({ key, label, color }) => (
          <div key={key} className={`rounded-2xl border p-4 ${color}`}>
            <p className="text-xs font-semibold uppercase tracking-wide mb-1">{label}</p>
            <p className="text-sm leading-relaxed">{projection[key]}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
