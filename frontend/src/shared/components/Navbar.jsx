import { NavLink } from "react-router-dom";
import { Ship, TrendingUp, Anchor, Map, Home } from "lucide-react";

const navItems = [
    {to:"/",label:"Home", icon:Home},
  { to: "/vessel-recommendation", label: "Vessel Recommendation", icon: Ship },
  { to: "/forecast", label: "Freight Forecast", icon: TrendingUp },
  { to: "/arrivals", label: "Arrival Board", icon: Anchor },
  { to: "/live-map", label: "Live Map", icon: Map },
];

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
        <NavLink to="/" className="flex items-center gap-2">
          <span className="font-bold text-lg text-navy tracking-tight">
            Freight<span className="text-teal">DSS</span>
          </span>
        </NavLink>

        <div className="flex items-center gap-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-teal/10 text-teal-dark"
                    : "text-slate-600 hover:text-navy hover:bg-slate-100"
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  );
}