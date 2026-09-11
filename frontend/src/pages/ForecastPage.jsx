import { useState } from "react";
import ForecastForm from "../features/freight-forecast/ForecastForm";
import ForecastChart from "../features/freight-forecast/ForecastChart";

export default function ForecastPage() {
  const [result, setResult] = useState(null);

  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <div className="mb-10">
        <span className="text-xs font-semibold tracking-widest uppercase text-teal-dark">
          Freight Forecast
        </span>
        <h1 className="text-3xl font-bold text-navy mt-2 mb-2">
          Freight Rate Forecast
        </h1>
        <p className="text-slate-600">
          Forecasted freight rate trend and confidence range for a given
          vessel class and route.
        </p>
      </div>

      <ForecastForm onResult={setResult} />
      <ForecastChart result={result} />
    </div>
  );
}