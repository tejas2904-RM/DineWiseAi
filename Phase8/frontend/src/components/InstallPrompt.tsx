'use client';

import { useEffect, useState } from 'react';
import { Download, X } from 'lucide-react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

const STORAGE_KEY = 'dinewise-install-dismissed';

export function InstallPrompt() {
  const [event, setEvent] = useState<BeforeInstallPromptEvent | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (localStorage.getItem(STORAGE_KEY) === '1') return;

    const handler = (e: Event) => {
      e.preventDefault();
      setEvent(e as BeforeInstallPromptEvent);
      setVisible(true);
    };
    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  function dismiss() {
    setVisible(false);
    try {
      localStorage.setItem(STORAGE_KEY, '1');
    } catch {
      /* ignore */
    }
  }

  async function install() {
    if (!event) return;
    try {
      await event.prompt();
      await event.userChoice;
    } catch {
      /* ignore */
    } finally {
      setVisible(false);
      setEvent(null);
    }
  }

  if (!visible) return null;

  return (
    <div className="install-banner" role="region" aria-label="Install DineWise AI">
      <Download className="w-4 h-4" aria-hidden="true" />
      <span className="flex-1">
        Install <strong>DineWise AI</strong> for the best experience.
      </span>
      <button
        onClick={install}
        className="btn btn-primary"
        style={{ padding: '0.35rem 0.8rem', fontSize: '0.8rem' }}
      >
        Install
      </button>
      <button
        onClick={dismiss}
        aria-label="Dismiss install prompt"
        title="Dismiss"
        className="p-1 rounded-md"
        style={{ color: 'var(--text-secondary)' }}
      >
        <X className="w-4 h-4" aria-hidden="true" />
      </button>
    </div>
  );
}
