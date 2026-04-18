import OutcomeCard from './OutcomeCard';

export default function ResultsGrid({ outcomes }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {outcomes.map((item) => (
        <OutcomeCard key={item.label} {...item} />
      ))}
    </div>
  );
}
