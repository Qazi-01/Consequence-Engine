const LABEL_STYLES = {
  'Most Likely': {
    badge: 'bg-indigo-100 text-indigo-700',
    bar: 'bg-indigo-500',
    border: 'border-indigo-200',
  },
  Likely: {
    badge: 'bg-emerald-100 text-emerald-700',
    bar: 'bg-emerald-500',
    border: 'border-emerald-200',
  },
  'Less Likely': {
    badge: 'bg-amber-100 text-amber-700',
    bar: 'bg-amber-500',
    border: 'border-amber-200',
  },
};

export default function OutcomeCard({ label, probability, outcome, reasoning, rippleEffect }) {
  const styles = LABEL_STYLES[label] ?? LABEL_STYLES['Less Likely'];
  const pct = Math.round(probability * 100);

  return (
    <div className={`flex flex-col gap-3 rounded-2xl border ${styles.border} bg-white p-5 shadow-sm`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className={`text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded-full ${styles.badge}`}>
          {label}
        </span>
        <span className="text-lg font-bold text-slate-800">{pct}%</span>
      </div>

      {/* Probability bar */}
      <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
        <div
          className={`h-full rounded-full ${styles.bar} transition-all duration-700`}
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Outcome */}
      <p className="font-semibold text-slate-800 text-sm leading-snug">{outcome}</p>

      {/* Reasoning */}
      <p className="text-slate-500 text-sm leading-relaxed">{reasoning}</p>

      {/* Ripple effect */}
      <p className="text-xs text-slate-400 italic border-t border-slate-100 pt-2">
        Then: {rippleEffect}
      </p>
    </div>
  );
}
