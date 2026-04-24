'use client';

import { useEffect } from 'react';
import { wsClient } from '@/lib/websocket-client';
import { useAuth } from '@/context/AuthContext';

export default function NotificationProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      // Connect to WebSocket when user is authenticated
      wsClient.connect();

      // Request notification permission
      if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
      }

      return () => {
        // Disconnect when user logs out or component unmounts
        wsClient.disconnect();
      };
    }
  }, [user]);

  return <>{children}</>;
}
