'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ThemeToggle } from './ThemeToggle';
import { Home, Clock, Heart, UtensilsCrossed, User } from 'lucide-react';

export function Navbar() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Dashboard', icon: Home },
    { href: '/history', label: 'History', icon: Clock },
    { href: '/favorites', label: 'Favorites', icon: Heart },
  ];

  return (
    <nav
      className="sticky top-0 z-50 border-b"
      style={{
        borderColor: 'var(--border)',
        background: 'var(--bg-secondary)',
      }}
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="container mx-auto px-4 max-w-[480px] md:max-w-[1100px] flex items-center justify-between h-14">
        <Link href="/" className="flex items-center gap-2">
          <div
            className="flex items-center justify-center w-8 h-8 rounded-lg"
            style={{ background: 'var(--accent-muted)', color: 'var(--accent)' }}
          >
            <UtensilsCrossed className="w-4 h-4" aria-hidden="true" />
          </div>
          <span className="font-bold text-lg" style={{ color: 'var(--accent)' }}>
            DineWise AI
          </span>
        </Link>

        <div className="flex items-center gap-1">
          <div className="hidden md:flex items-center gap-1">
            {links.map(({ href, label, icon: Icon }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-medium transition-colors"
                  style={
                    active
                      ? { background: 'var(--accent-muted)', color: 'var(--accent)' }
                      : { color: 'var(--text-secondary)' }
                  }
                  aria-current={active ? 'page' : undefined}
                >
                  <Icon className="w-4 h-4" aria-hidden="true" />
                  <span>{label}</span>
                </Link>
              );
            })}
            <ThemeToggle />
          </div>
          <button
            type="button"
            className="flex md:hidden items-center justify-center w-9 h-9 rounded-full border"
            style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}
            aria-label="User profile"
          >
            <User className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </nav>
  );
}
