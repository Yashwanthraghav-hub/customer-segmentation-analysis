import { useEffect, useState, type ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';

export function SecureRoute({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  useEffect(() => {
    if (!supabase) { setReady(true); return; }
    supabase.auth.getSession().then(({ data }) => { setAuthenticated(Boolean(data.session)); setReady(true); });
    const { data } = supabase.auth.onAuthStateChange((_event, session) => setAuthenticated(Boolean(session)));
    return () => data.subscription.unsubscribe();
  }, []);
  if (!ready) return <main aria-live="polite">Checking your secure session…</main>;
  if (!supabase || !authenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
