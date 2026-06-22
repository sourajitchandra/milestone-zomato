"use client";

interface EmptyStateProps {
  icon?: string;
  title: string;
  subtitle?: string;
}

export default function EmptyState({
  icon = "🍽️",
  title,
  subtitle,
}: EmptyStateProps) {
  return (
    <div className="empty-state" role="status">
      <div className="empty-state-icon" aria-hidden="true">{icon}</div>
      <div className="empty-state-title">{title}</div>
      {subtitle && <p className="empty-state-sub">{subtitle}</p>}
    </div>
  );
}

export function LoadingState() {
  return (
    <div className="spinner-wrap" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      <p className="spinner-text">🤖 Analyzing restaurants with Groq LLM…</p>
    </div>
  );
}
