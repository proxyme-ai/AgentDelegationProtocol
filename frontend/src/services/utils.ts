import type { TokenInfo } from '../types';
import { APIException } from '../types';

// ============================================================================
// ERROR HANDLING UTILITIES
// ============================================================================

/**
 * Format API error for user display
 */
export function formatAPIError(error: APIException | Error | null): string {
    if (!error) return '';

    if (error instanceof APIException) {
        // Handle specific error codes
        switch (error.code) {
            case 400:
                return error.details?.missing_fields
                    ? `Missing required fields: ${error.details.missing_fields.join(', ')}`
                    : error.message || 'Invalid request';
            case 401:
                return 'Authentication required';
            case 403:
                return 'Access denied';
            case 404:
                return 'Resource not found';
            case 409:
                return 'Resource already exists';
            case 408:
                return 'Request timed out. Please try again.';
            case 429:
                return 'Too many requests. Please wait and try again.';
            case 500:
                return 'Server error. Please try again later.';
            case 503:
                return 'Service temporarily unavailable';
            default:
                return error.message || 'An unexpected error occurred';
        }
    }

    return error.message || 'An unexpected error occurred';
}

/**
 * Check if error is a network error
 */
export function isNetworkError(error: any): boolean {
    return error instanceof TypeError && error.message.includes('fetch');
}

/**
 * Check if error is a timeout error
 */
export function isTimeoutError(error: any): boolean {
    return error instanceof APIException && error.code === 408;
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error: any): boolean {
    if (error instanceof APIException) {
        return error.code >= 500 || error.code === 408;
    }
    return isNetworkError(error);
}

// ============================================================================
// TOKEN UTILITIES
// ============================================================================

/**
 * Parse JWT token payload (without verification)
 */
export function parseJWTPayload(token: string): Record<string, any> | null {
    try {
        const parts = token.split('.');
        if (parts.length !== 3) return null;

        const payload = parts[1];
        const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
        return JSON.parse(decoded);
    } catch {
        return null;
    }
}

/**
 * Check if token is expired
 */
export function isTokenExpired(token: string): boolean {
    const payload = parseJWTPayload(token);
    if (!payload || !payload.exp) return true;

    const now = Math.floor(Date.now() / 1000);
    return payload.exp < now;
}

/**
 * Get token expiry time in seconds
 */
export function getTokenExpiryTime(token: string): number | null {
    const payload = parseJWTPayload(token);
    return payload?.exp || null;
}

/**
 * Get time until token expires (in seconds)
 */
export function getTimeToExpiry(token: string): number {
    const expiryTime = getTokenExpiryTime(token);
    if (!expiryTime) return 0;

    const now = Math.floor(Date.now() / 1000);
    return Math.max(0, expiryTime - now);
}

/**
 * Format token for display (truncated)
 */
export function formatTokenForDisplay(token: string, length: number = 20): string {
    if (token.length <= length) return token;
    return `${token.substring(0, length)}...`;
}

/**
 * Get token type from payload
 */
export function getTokenType(token: string): 'delegation' | 'access' | 'unknown' {
    const payload = parseJWTPayload(token);
    if (!payload) return 'unknown';

    // Check for delegation token characteristics
    if (payload.delegator && payload.sub) return 'delegation';

    // Check for access token characteristics
    if (payload.actor && payload.sub) return 'access';

    return 'unknown';
}

/**
 * Extract scopes from token
 */
export function getTokenScopes(token: string): string[] {
    const payload = parseJWTPayload(token);
    return payload?.scope || [];
}

/**
 * Create TokenInfo object from JWT token
 */
export function createTokenInfo(token: string): TokenInfo | null {
    const payload = parseJWTPayload(token);
    if (!payload) return null;

    const tokenType = getTokenType(token);
    const expiryTime = getTokenExpiryTime(token);
    const timeToExpiry = getTimeToExpiry(token);

    // Only return valid token types
    if (tokenType === 'unknown') return null;

    return {
        token,
        type: tokenType,
        subject: payload.sub || '',
        expires_at: expiryTime ? new Date(expiryTime * 1000).toISOString() : '',
        issued_at: payload.iat ? new Date(payload.iat * 1000).toISOString() : '',
        scopes: getTokenScopes(token),
        time_to_expiry_seconds: timeToExpiry,
        claims: payload,
        isValid: !isTokenExpired(token)
    };
}

// ============================================================================
// VALIDATION UTILITIES
// ============================================================================

/**
 * Validate agent name
 */
export function validateAgentName(name: string): string | null {
    if (!name || name.trim().length === 0) {
        return 'Agent name is required';
    }

    if (name.length < 2) {
        return 'Agent name must be at least 2 characters long';
    }

    if (name.length > 100) {
        return 'Agent name must be less than 100 characters';
    }

    if (!/^[a-zA-Z0-9\s\-_]+$/.test(name)) {
        return 'Agent name can only contain letters, numbers, spaces, hyphens, and underscores';
    }

    return null;
}

/**
 * Validate scopes array
 */
export function validateScopes(scopes: string[]): string | null {
    if (!Array.isArray(scopes)) {
        return 'Scopes must be an array';
    }

    if (scopes.length === 0) {
        return 'At least one scope is required';
    }

    for (const scope of scopes) {
        if (typeof scope !== 'string' || scope.trim().length === 0) {
            return 'All scopes must be non-empty strings';
        }

        if (!/^[a-zA-Z0-9:_-]+$/.test(scope)) {
            return 'Scopes can only contain letters, numbers, colons, hyphens, and underscores';
        }
    }

    return null;
}

/**
 * Validate user ID
 */
export function validateUserId(userId: string): string | null {
    if (!userId || userId.trim().length === 0) {
        return 'User ID is required';
    }

    if (userId.length < 2) {
        return 'User ID must be at least 2 characters long';
    }

    if (userId.length > 50) {
        return 'User ID must be less than 50 characters';
    }

    if (!/^[a-zA-Z0-9_-]+$/.test(userId)) {
        return 'User ID can only contain letters, numbers, hyphens, and underscores';
    }

    return null;
}

// ============================================================================
// FORMATTING UTILITIES
// ============================================================================

/**
 * Format timestamp for display
 */
export function formatTimestamp(timestamp: string): string {
    try {
        const date = new Date(timestamp);
        return date.toLocaleString();
    } catch {
        return timestamp;
    }
}

/**
 * Format relative time (e.g., "2 minutes ago")
 */
export function formatRelativeTime(timestamp: string): string {
    try {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffSeconds = Math.floor(diffMs / 1000);
        const diffMinutes = Math.floor(diffSeconds / 60);
        const diffHours = Math.floor(diffMinutes / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffSeconds < 60) {
            return 'just now';
        } else if (diffMinutes < 60) {
            return `${diffMinutes} minute${diffMinutes === 1 ? '' : 's'} ago`;
        } else if (diffHours < 24) {
            return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
        } else if (diffDays < 7) {
            return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`;
        } else {
            return formatTimestamp(timestamp);
        }
    } catch {
        return timestamp;
    }
}

/**
 * Format duration in seconds to human readable format
 */
export function formatDuration(seconds: number): string {
    if (seconds < 60) {
        return `${seconds}s`;
    }

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    if (minutes < 60) {
        return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
    }

    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;

    if (hours < 24) {
        return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
    }

    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;

    return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
}

/**
 * Get status color for UI components
 */
export function getStatusColor(status: string): string {
    switch (status.toLowerCase()) {
        case 'active':
        case 'approved':
        case 'success':
            return 'green';
        case 'pending':
            return 'yellow';
        case 'inactive':
        case 'suspended':
        case 'denied':
        case 'revoked':
        case 'expired':
            return 'red';
        case 'error':
        case 'failed':
            return 'red';
        default:
            return 'gray';
    }
}

/**
 * Debounce function for search inputs
 */
export function debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
): (...args: Parameters<T>) => void {
    let timeout: number;

    return (...args: Parameters<T>) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait) as any;
    };
}

/**
 * Deep clone object
 */
export function deepClone<T>(obj: T): T {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime()) as any;
    if (obj instanceof Array) return obj.map(item => deepClone(item)) as any;
    if (typeof obj === 'object') {
        const clonedObj = {} as any;
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                clonedObj[key] = deepClone(obj[key]);
            }
        }
        return clonedObj;
    }
    return obj;
}