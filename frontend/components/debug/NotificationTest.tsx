'use client';

import { useEffect, useState } from 'react';
import { wsClient } from '@/lib/websocket-client';

export default function NotificationTest() {
  const [logs, setLogs] = useState<string[]>([]);
  const [wsStatus, setWsStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  useEffect(() => {
    addLog('Component mounted');

    // Check notification permission
    if ('Notification' in window) {
      addLog(`Notification permission: ${Notification.permission}`);
      if (Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
          addLog(`Notification permission granted: ${permission}`);
        });
      }
    } else {
      addLog('❌ Notifications not supported in this browser');
    }

    // Subscribe to WebSocket notifications
    const unsubscribe = wsClient.subscribe((notification) => {
      addLog(`✅ Received notification: ${JSON.stringify(notification)}`);
    });

    // Connect WebSocket
    addLog('Connecting to WebSocket...');
    setWsStatus('connecting');
    wsClient.connect();

    // Check connection status after 2 seconds
    setTimeout(() => {
      if (wsClient['ws']?.readyState === WebSocket.OPEN) {
        addLog('✅ WebSocket connected successfully');
        setWsStatus('connected');
      } else {
        addLog('❌ WebSocket failed to connect');
        setWsStatus('disconnected');
      }
    }, 2000);

    return () => {
      unsubscribe();
    };
  }, []);

  const testNotification = () => {
    if (Notification.permission === 'granted') {
      new Notification('Test Notification', {
        body: 'This is a test notification from TaskFlow',
        icon: '/favicon.svg',
      });
      addLog('✅ Test notification sent');
    } else {
      addLog('❌ Notification permission not granted');
    }
  };

  return (
    <div className="fixed bottom-4 right-4 w-96 bg-white dark:bg-gray-900 border border-blue-200 dark:border-blue-800/30 rounded-lg shadow-lg p-4 max-h-96 overflow-hidden flex flex-col z-50">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-900 dark:text-white">Notification Test</h3>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${
            wsStatus === 'connected' ? 'bg-green-500' :
            wsStatus === 'connecting' ? 'bg-yellow-500' :
            'bg-red-500'
          }`} />
          <span className="text-xs text-gray-500 dark:text-gray-400">{wsStatus}</span>
        </div>
      </div>

      <button
        onClick={testNotification}
        className="mb-3 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
      >
        Test Browser Notification
      </button>

      <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-950 rounded p-2 text-xs font-mono space-y-1">
        {logs.map((log, i) => (
          <div key={i} className="text-gray-700 dark:text-gray-300">
            {log}
          </div>
        ))}
      </div>
    </div>
  );
}
