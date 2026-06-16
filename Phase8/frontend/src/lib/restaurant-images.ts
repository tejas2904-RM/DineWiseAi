const FOOD_IMAGES = [
  'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=640&q=80',
  'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=640&q=80',
  'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=640&q=80',
  'https://images.unsplash.com/photo-1493779387763-b78f0bb2f2e7?w=640&q=80',
  'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=640&q=80',
  'https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=640&q=80',
  'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=640&q=80',
  'https://images.unsplash.com/photo-1552566626-52f8b828add9?w=640&q=80',
];

export function getRestaurantImage(id: string): string {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = (hash + id.charCodeAt(i)) % FOOD_IMAGES.length;
  }
  return FOOD_IMAGES[hash];
}

export function budgetSymbols(budget: string): string {
  if (budget === 'low') return '₹';
  if (budget === 'high') return '₹₹₹';
  return '₹₹';
}
