import { useState } from "react";
import RecommendationForm from "../features/vessel-recommendation/RecommendationForm";
import RecommendationResult from "../features/vessel-recommendation/RecommendationResult";
import RiskAlertSection from "../features/vessel-recommendation/RiskAlertSection";

export default function VesselRecommendationPage() {
  const [result, setResult] = useState(null);

  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <div className="mb-10">
        <span className="text-xs font-semibold tracking-widest uppercase text-teal-dark">
          Vessel Optimizer
        </span>
        <h1 className="text-3xl font-bold text-navy mt-2 mb-2">
          Vessel Recommendation
        </h1>
        <p className="text-slate-600">
          Enter cargo quantity and route to get the optimal vessel type based
          on draft, LOA and beam constraints at both ports.
        </p>
      </div>

      <RecommendationForm onResult={setResult} />
      <RecommendationResult result={result} />
      {result && <RiskAlertSection />}
    </div>
  );
}