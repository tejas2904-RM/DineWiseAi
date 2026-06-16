'use client';

import { useState } from 'react';
import type { RecommendationItem } from '@/lib/api';
import { addFavorite, removeFavorite, sendFeedback } from '@/lib/api';
import { getRestaurantImage, budgetSymbols } from '@/lib/restaurant-images';
import { Star, Heart, Share2, ThumbsUp, ThumbsDown, Sparkles } from 'lucide-react';

interface RecommendationCardProps {
  item: RecommendationItem;
  requestId: string;
  location?: string;
  budget?: string;
  onFavoriteToggle?: (restaurantId: string, favorited: boolean) => void;
}

function toTitle(s: string): string {
  return s
    .split(' ')
    .map((w) => (w.length === 0 ? w : w[0].toUpperCase() + w.slice(1)))
    .join(' ');
}

export function RecommendationCard({
  item,
  requestId,
  location,
  budget = 'medium',
  onFavoriteToggle,
}: RecommendationCardProps) {
  const [favorited, setFavorited] = useState(false);
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);
  const imageUrl = getRestaurantImage(item.restaurantId);

  async function toggleFavorite() {
    try {
      if (favorited) {
        await removeFavorite(item.restaurantId);
        setFavorited(false);
        onFavoriteToggle?.(item.restaurantId, false);
      } else {
        await addFavorite({
          restaurantId: item.restaurantId,
          name: item.name,
          cuisine: item.cuisine,
          rating: item.rating,
          estimatedCost: item.estimatedCost,
        });
        setFavorited(true);
        onFavoriteToggle?.(item.restaurantId, true);
      }
    } catch (e) {
      console.error('favorite toggle failed', e);
    }
  }

  async function vote(value: 'up' | 'down') {
    setFeedback(value);
    try {
      await sendFeedback(requestId, item.restaurantId, value === 'up');
    } catch (e) {
      console.error('feedback failed', e);
    }
  }

  function share() {
    const text = `Check out ${item.name} (${item.cuisine}, ${item.rating}★)`;
    const url = `${window.location.origin}/?restaurant=${encodeURIComponent(item.restaurantId)}`;
    if (navigator.share) {
      navigator.share({ title: item.name, text, url }).catch(() => {});
    } else {
      navigator.clipboard.writeText(`${text} — ${url}`).catch(() => {});
      alert('Link copied to clipboard');
    }
  }

  return (
    <article className="card overflow-hidden" aria-label={`Recommendation ${item.rank}: ${item.name}`}>
      <div className="relative h-44 w-full">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={imageUrl}
          alt=""
          className="w-full h-full object-cover"
          loading="lazy"
        />
        <button
          onClick={toggleFavorite}
          className="absolute top-3 right-3 flex items-center justify-center w-9 h-9 rounded-full transition-colors"
          style={{
            background: 'rgba(255,255,255,0.92)',
            color: favorited ? 'var(--danger)' : 'var(--text-secondary)',
          }}
          aria-label={favorited ? 'Remove from favorites' : 'Add to favorites'}
          aria-pressed={favorited}
        >
          <Heart className="w-4 h-4" fill={favorited ? 'currentColor' : 'none'} aria-hidden="true" />
        </button>
      </div>

      <div className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-lg font-bold leading-tight">{item.name}</h3>
          <span className="rating-badge" aria-label={`Rating ${item.rating}`}>
            {item.rating.toFixed(1)} <Star className="w-3.5 h-3.5 fill-current" aria-hidden="true" />
          </span>
        </div>

        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          {toTitle(item.cuisine.split(',')[0] || item.cuisine)}
          {location && <> · {toTitle(location)}</>}
          {' · '}{budgetSymbols(budget)}
        </p>

        <div className="ai-insight">
          <p className="text-xs font-semibold mb-1 flex items-center gap-1" style={{ color: 'var(--accent)' }}>
            <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
            AI Insight
          </p>
          <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
            {item.reason}
          </p>
        </div>

        <footer className="flex items-center justify-between pt-1">
          <div className="flex gap-1">
            <button
              onClick={() => vote('up')}
              className="p-2 rounded-lg transition-colors"
              style={
                feedback === 'up'
                  ? { background: 'var(--accent-muted)', color: 'var(--accent)' }
                  : { color: 'var(--text-muted)' }
              }
              aria-label="Helpful"
              aria-pressed={feedback === 'up'}
            >
              <ThumbsUp className="w-4 h-4" aria-hidden="true" />
            </button>
            <button
              onClick={() => vote('down')}
              className="p-2 rounded-lg transition-colors"
              style={
                feedback === 'down'
                  ? { background: 'color-mix(in srgb, var(--danger) 14%, transparent)', color: 'var(--danger)' }
                  : { color: 'var(--text-muted)' }
              }
              aria-label="Not helpful"
              aria-pressed={feedback === 'down'}
            >
              <ThumbsDown className="w-4 h-4" aria-hidden="true" />
            </button>
          </div>
          <button
            onClick={share}
            className="inline-flex items-center gap-1 text-xs p-2 rounded-lg transition-colors"
            style={{ color: 'var(--text-muted)' }}
            aria-label="Share recommendation"
          >
            <Share2 className="w-3.5 h-3.5" aria-hidden="true" />
            Share
          </button>
        </footer>
      </div>
    </article>
  );
}
