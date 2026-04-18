export default function SmarterDecision({ text }) {
  return (
    <div className="rounded-2xl border border-indigo-100 bg-indigo-50 p-5">
      <h2 className="text-base font-semibold text-indigo-800 mb-2">💡 Smarter Decision</h2>
      <p className="text-slate-700 text-sm leading-relaxed">{text}</p>
    </div>
  );
}
