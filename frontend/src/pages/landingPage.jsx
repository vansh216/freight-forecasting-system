import Hero from "../features/landing/Hero.jsx";
import ProblemStatement from "../features/landing/ProblemStatement.jsx";
import FeaturesGrid from "../features/landing/FeatureGrid.jsx";
import HowItWorks from "../features/landing/HowItsWork.jsx";

export default function LandingPage() {
  return (
    <>
      <Hero />
      <ProblemStatement />
      <FeaturesGrid />
      <HowItWorks />
    </>
  );
}