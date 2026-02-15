/**
 * Authentication utilities for the Todo application
 */

/**
 * Get authentication headers for API requests
 */
export function getAuthHeaders(): Record<string, string> {
  // Try to get token from localStorage (client-side)
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };
    }
  }

  // Fallback for server-side or when no token
  return {
    'Content-Type': 'application/json'
  };
}

/**
 * Get current user ID from JWT token
 * Note: This is a simplified implementation. In a real app,
 * you would properly decode the JWT token.
 */
export function getCurrentUserId(): string | null {
  if (typeof window !== 'undefined') {
    // Try to get from localStorage
    const userId = localStorage.getItem('user_id');
    if (userId) return userId;

    // Fallback: try to extract from token if available
    const token = localStorage.getItem('token');
    if (token) {
      try {
        // Simple base64 decode (real implementation would use JWT library)
        const payload = token.split('.')[1];
        if (payload) {
          const decoded = JSON.parse(atob(payload));
          return decoded.user_id || decoded.sub || null;
        }
      } catch (e) {
        console.error('Error decoding token:', e);
      }
    }
  }
  return null;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (!token) return false;

    // Simple check for token expiration (real implementation would decode JWT)
    // For now, just check if token exists
    return true;
  }
  return false;
}

/**
 * Save authentication data
 */
export function saveAuthData(token: string, userId: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('token', token);
    localStorage.setItem('user_id', userId);
  }
}

/**
 * Clear authentication data (logout)
 */
export function clearAuthData(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
  }
}