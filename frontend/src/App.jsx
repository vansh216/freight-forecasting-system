import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./shared/components/Navbar";
import Footer from "./shared/components/Footer";
import LandingPage from "./pages/landingPage.jsx";
import VesselRecommendationPage from "./pages/VesselRecommendationPage";
import ForecastPage from "./pages/ForecastPage";
import ArrivalBoardPage from "./pages/ArrivalBoardPage.jsx";
import LiveMapPage from "./pages/LiveMapPage.jsx";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-slate-bg">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/vessel-recommendation" element={<VesselRecommendationPage />} />
            <Route path="/forecast" element={<ForecastPage />} />
            <Route path="/arrivals" element={<ArrivalBoardPage />} />
            <Route path="/live-map" element={<LiveMapPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;