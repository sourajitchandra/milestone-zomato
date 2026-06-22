"use client";

interface AIBannerProps {
  summary: string;
  candidatesConsidered: number;
  filtersApplied: string[];
}

export default function AIBanner({
  summary,
  candidatesConsidered,
  filtersApplied,
}: AIBannerProps) {
  const filtersStr =
    filtersApplied.length > 0 ? filtersApplied.join(", ") : "none";

  return (
    <div className="ai-banner" role="status" aria-live="polite">
      <div className="ai-banner-icon" aria-hidden="true">✨</div>
      <div>
        <div className="ai-banner-title">AI Recommendation Engine</div>
        <p className="ai-banner-text">{summary}</p>
        <div className="ai-banner-meta">
          {candidatesConsidered} candidates considered &nbsp;·&nbsp; Filters:{" "}
          {filtersStr}
        </div>
      </div>
    </div>
  );
}
