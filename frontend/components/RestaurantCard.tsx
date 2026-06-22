"use client";

interface RecommendationItem {
  rank: number;
  name: string;
  cuisine: string;
  rating: number | null;
  estimated_cost: number | null;
  explanation: string;
}

interface RestaurantCardProps {
  rec: RecommendationItem;
  delayIndex: number;
}

export default function RestaurantCard({ rec, delayIndex }: RestaurantCardProps) {
  const ratingDisplay = rec.rating != null ? `★ ${rec.rating.toFixed(1)}` : "★ N/A";
  const costDisplay =
    rec.estimated_cost != null
      ? `₹${rec.estimated_cost.toLocaleString("en-IN")} for two`
      : "Cost N/A";

  const cuisineParts = rec.cuisine
    .split(",")
    .map((c) => c.trim())
    .filter(Boolean)
    .slice(0, 3);

  const delayS = (0.05 * (delayIndex + 1)).toFixed(2);

  return (
    <article
      className="restaurant-card"
      style={{ animationDelay: `${delayS}s` }}
      aria-label={`Restaurant: ${rec.name}, Rank ${rec.rank}`}
    >
      <div className="card-body">
        <div className="card-top-row">
          <span className="rank-badge">#{rec.rank}</span>
          <span className="restaurant-name" title={rec.name}>
            {rec.name}
          </span>
          <span className="rating-pill" aria-label={`Rating: ${ratingDisplay}`}>
            {ratingDisplay}
          </span>
        </div>

        <div className="tags-row">
          {cuisineParts.map((c) => (
            <span key={c} className="cuisine-tag">
              {c}
            </span>
          ))}
          <span className="cost-tag">💰 {costDisplay}</span>
        </div>

        <blockquote className="card-explanation">
          &ldquo;{rec.explanation}&rdquo;
        </blockquote>
      </div>
    </article>
  );
}
