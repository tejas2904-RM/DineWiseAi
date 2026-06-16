'use client';

import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import type { RecommendationItem } from '@/lib/api';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix default Leaflet icon in webpack/Next.js bundling.
const DefaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

// Approximate coordinates for Bangalore neighborhoods.
const LOCATION_COORDS: Record<string, [number, number]> = {
  indiranagar: [12.9784, 77.6408],
  koramangala: [12.9279, 77.6271],
  bellandur: [12.926, 77.6762],
  whitefield: [12.9698, 77.7499],
  marathahalli: [12.9569, 77.7011],
  jayanagar: [12.9293, 77.5829],
  btm: [12.9166, 77.6101],
  hsr: [12.9116, 77.6446],
  electronic_city: [12.8456, 77.6603],
  bangalore: [12.9716, 77.5946],
};

export interface MapViewProps {
  location: string;
  recommendations: RecommendationItem[];
  height?: string;
}

export function MapView({ location, recommendations, height = '500px' }: MapViewProps) {
  const key = location.toLowerCase().replace(/\s+/g, '_');
  const center: [number, number] = LOCATION_COORDS[key] || LOCATION_COORDS.bangalore;

  useEffect(() => {
    // Force Leaflet to recalculate map size after mount.
    setTimeout(() => window.dispatchEvent(new Event('resize')), 100);
  }, []);

  // Spread markers around center using small offsets per index.
  const markers = recommendations.map((item, idx) => {
    const angle = (idx / Math.max(recommendations.length, 1)) * 2 * Math.PI;
    const radius = 0.005;
    return {
      position: [center[0] + Math.cos(angle) * radius, center[1] + Math.sin(angle) * radius] as [number, number],
      item,
    };
  });

  return (
    <div className="card overflow-hidden" style={{ height }}>
      <MapContainer center={center} zoom={14} scrollWheelZoom={false}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {markers.map(({ position, item }) => (
          <Marker key={item.restaurantId} position={position}>
            <Popup>
              <div className="text-sm">
                <p className="font-semibold">{item.name}</p>
                <p>{item.cuisine}</p>
                <p>★ {item.rating.toFixed(1)} · ₹{Math.round(item.estimatedCost)}</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
