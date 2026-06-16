'use client';

import { useState, useEffect } from 'react';
import { getRecentSearches, type SavedSearch } from '@/lib/user-store';
import { MapPin, Clock } from 'lucide-react';

interface RecentSearchesProps {
  onSelect: (payload: SavedSearch['payload']) => void;
}

export function RecentSearches({ onSelect }: RecentSearchesProps) {
  const [searches, setSearches] = useState<SavedSearch[]>([]);

  useEffect(() => {
    setSearches(getRecentSearches());
  }, []);

  if (searches.length === 0) return null;

  function toTitle(s: string): string {
    return s
      .split(' ')
      .map((w) => (w.length === 0 ? w : w[0].toUpperCase() + w.slice(1)))
      .join(' ');
  }

  function budgetLabel(budget: string): string {
    if (budget === 'low') return 'Low';
    if (budget === 'high') return 'High';
    return 'Medium';
  }

  return (
    <div className="card p-4">
      <h3 className="text-base font-bold mb-3">Recent searches</h3>
      <div className="flex flex-col gap-2">
        {searches.map((search, i) => (
          <button
            key={search.id}
            onClick={() => onSelect(search.payload)}
            className="chip w-full justify-start transition-colors hover:border-[var(--accent)]"
            style={{ cursor: 'pointer' }}
            title="Re-run this search"
            aria-label={`Re-run search: ${search.payload.location}, ${search.payload.cuisine}, ${search.payload.budget}`}
          >
            {i === 0 ? (
              <MapPin className="w-3.5 h-3.5 shrink-0" style={{ color: 'var(--accent)' }} aria-hidden="true" />
            ) : (
              <Clock className="w-3.5 h-3.5 shrink-0" style={{ color: 'var(--text-muted)' }} aria-hidden="true" />
            )}
            {toTitle(search.payload.location)} · {toTitle(search.payload.cuisine)} · {budgetLabel(search.payload.budget)}
          </button>
        ))}
      </div>
    </div>
  );
}
