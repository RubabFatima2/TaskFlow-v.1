type NotificationCallback = (notification: TaskNotification) => void;

interface TaskNotification {
  type: 'task_reminder';
  task_id: number;
  title: string;
  description: string | null;
  due_date: string;
  priority: string;
}

class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private callbacks: Set<NotificationCallback> = new Set();
  private isConnecting = false;

  // Get access token from cookies
  private getAccessToken(): string | null {
    if (typeof document === 'undefined') return null;

    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'access_token') {
        return value;
      }
    }
    return null;
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;

    // Get access token
    const token = this.getAccessToken();
    if (!token) {
      console.error('No access token found, cannot connect to WebSocket');
      this.isConnecting = false;
      return;
    }

    // WebSocket URL with token as query parameter
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.NEXT_PUBLIC_API_URL?.replace('http://', '').replace('https://', '') || 'localhost:8000';
    const wsUrl = `${protocol}//${host}/api/v1/notifications/ws?token=${token}`;

    console.log('Connecting to WebSocket...');

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.isConnecting = false;

        // Send ping every 30 seconds to keep connection alive
        const pingInterval = setInterval(() => {
          if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send('ping');
          } else {
            clearInterval(pingInterval);
          }
        }, 30000);
      };

      this.ws.onmessage = (event) => {
        if (event.data === 'pong') return;

        try {
          const notification: TaskNotification = JSON.parse(event.data);

          // Notify all registered callbacks
          this.callbacks.forEach(callback => callback(notification));

          // Show browser notification
          if (notification.type === 'task_reminder') {
            this.showBrowserNotification(notification);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected', event.code, event.reason);
        this.isConnecting = false;
        this.ws = null;

        // Don't reconnect on authentication errors (403, 401)
        if (event.code === 1008 || event.code === 1002) {
          console.log('WebSocket closed due to authentication error, not reconnecting');
          return;
        }

        // Attempt to reconnect after 5 seconds
        this.reconnectTimeout = setTimeout(() => {
          console.log('Attempting to reconnect...');
          this.connect();
        }, 5000);
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.isConnecting = false;
    }
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  subscribe(callback: NotificationCallback) {
    this.callbacks.add(callback);
    return () => this.callbacks.delete(callback);
  }

  private async showBrowserNotification(notification: TaskNotification) {
    if (!('Notification' in window)) {
      return;
    }

    if (Notification.permission === 'granted') {
      const dueDate = new Date(notification.due_date);
      const timeStr = dueDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      new Notification('Task Reminder', {
        body: `${notification.title}\nDue: ${timeStr}`,
        icon: '/favicon.svg',
        tag: `task-${notification.task_id}`,
        requireInteraction: true,
      });
    } else if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        this.showBrowserNotification(notification);
      }
    }
  }
}

export const wsClient = new WebSocketClient();
