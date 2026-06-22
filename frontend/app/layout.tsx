import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ZomatoAI — AI-Powered Restaurant Recommendations",
  description:
    "Discover the perfect restaurant using AI. ZomatoAI combines real Zomato data with Groq LLM to give you personalized, explainable restaurant recommendations based on your location, budget, and cuisine preferences.",
  keywords: "restaurant recommendations, AI, Zomato, Groq, food, dining",
  openGraph: {
    title: "ZomatoAI — AI Restaurant Recommendations",
    description: "AI-powered restaurant discovery powered by Groq LLM and real Zomato data.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
