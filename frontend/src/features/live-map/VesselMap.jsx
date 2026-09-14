import { MapContainer, TileLayer, Marker, Tooltip } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const shipIcon = new L.DivIcon({
  className: "custom-ship-icon",
  html: `
    <svg width="28" height="28" viewBox="0 0 24 24" fill="#0d9488" stroke="#0f766e" stroke-width="0.5" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L4 14h16L12 2z" transform="rotate(180 12 12)"/>
      <path d="M3 16l1.5 4.5c.3.9 1.1 1.5 2 1.5h11c.9 0 1.7-.6 2-1.5L21 16H3z"/>
      <rect x="10" y="6" width="4" height="6" />
    </svg>
  `,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
});

const CENTER = [19.5, 85.5];

export default function VesselMap({ vessels }) {
  return (
    <div className="h-[560px] rounded-2xl overflow-hidden border border-slate-200">
      <MapContainer center={CENTER} zoom={5} className="w-full h-full">
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {vessels.map((v) => (
          <Marker key={v.mmsi} position={[v.latitude, v.longitude]} icon={shipIcon}>
            <Tooltip direction="top" offset={[0, -10]} opacity={1} sticky>
              <div className="text-xs">
                <p className="font-semibold text-navy">{v.vessel_name}</p>
                <p className="text-slate-500">MMSI: {v.mmsi}</p>
              </div>
            </Tooltip>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}