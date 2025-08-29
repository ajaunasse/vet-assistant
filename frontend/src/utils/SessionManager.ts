/**
 * Global session manager to prevent duplicate session creation
 */
class SessionManager {
  private static instance: SessionManager | null = null;
  private sessionId: string | null = null;
  private sessionPromise: Promise<string> | null = null;
  private isInitializing: boolean = false;

  private constructor() {}

  static getInstance(): SessionManager {
    if (!SessionManager.instance) {
      SessionManager.instance = new SessionManager();
    }
    return SessionManager.instance;
  }

  async getSessionId(createSessionFn: () => Promise<string>): Promise<string> {
    // If we already have a session ID, return it
    if (this.sessionId) {
      console.log('[SessionManager] Returning existing session:', this.sessionId);
      return this.sessionId;
    }

    // If we're already initializing, wait for the existing promise
    if (this.isInitializing && this.sessionPromise) {
      console.log('[SessionManager] Waiting for existing session initialization');
      return this.sessionPromise;
    }

    // Start initialization
    console.log('[SessionManager] Starting session initialization');
    this.isInitializing = true;

    this.sessionPromise = createSessionFn()
      .then(sessionId => {
        console.log('[SessionManager] Session initialized:', sessionId);
        this.sessionId = sessionId;
        this.isInitializing = false;
        return sessionId;
      })
      .catch(error => {
        console.error('[SessionManager] Session initialization failed:', error);
        this.isInitializing = false;
        this.sessionPromise = null;
        throw error;
      });

    return this.sessionPromise;
  }

  reset(): void {
    console.log('[SessionManager] Resetting session');
    this.sessionId = null;
    this.sessionPromise = null;
    this.isInitializing = false;
  }

  getCurrentSessionId(): string | null {
    return this.sessionId;
  }
}

export default SessionManager;