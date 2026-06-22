"use client";

interface NavbarProps {
  groqActive: boolean;
}

export default function Navbar({ groqActive }: NavbarProps) {
  return (
    <nav className="navbar" role="banner">
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div className="navbar-logo">🍽️ ZomatoAI</div>
        <div className="navbar-tagline">AI-Powered · Groq LLM · Real Zomato Data</div>
      </div>

      <div className="groq-badge" aria-label={`Groq status: ${groqActive ? "active" : "inactive"}`}>
        <span className={`groq-dot ${groqActive ? "active" : "inactive"}`} />
        Groq:&nbsp;
        <span style={{ color: groqActive ? "#10B981" : "#EF4444", marginLeft: "2px" }}>
          {groqActive ? "Active" : "Unavailable"}
        </span>
      </div>
    </nav>
  );
}
