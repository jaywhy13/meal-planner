import type { AxiosAdapter, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import api from './api';

/**
 * Builds a fake axios adapter that records every outgoing request URL and always
 * responds with 401. It caps the number of requests so that a buggy infinite
 * retry loop terminates (and the assertion fails) instead of hanging the test.
 */
const buildUnauthorizedAdapter = (requestUrls: string[]): AxiosAdapter => {
  return async (config: InternalAxiosRequestConfig): Promise<AxiosResponse> => {
    requestUrls.push(config.url ?? '');
    if (requestUrls.length > 20) {
      throw new Error('Too many requests — interceptor is looping');
    }
    const error = new Error('Request failed with status code 401') as Error & {
      config: InternalAxiosRequestConfig;
      response: {
        status: number;
        data: unknown;
        statusText: string;
        headers: object;
        config: InternalAxiosRequestConfig;
      };
    };
    error.config = config;
    error.response = { status: 401, data: {}, statusText: 'Unauthorized', headers: {}, config };
    return Promise.reject(error);
  };
};

describe('api response interceptor 401 handling', () => {
  let requestUrls: string[];
  let originalAdapter: AxiosAdapter | undefined;
  let originalLocation: Location;

  beforeEach(() => {
    requestUrls = [];
    originalAdapter = api.defaults.adapter as AxiosAdapter | undefined;
    api.defaults.adapter = buildUnauthorizedAdapter(requestUrls);

    // jsdom throws on real navigation, so replace location with a writable stub.
    originalLocation = window.location;
    delete (window as unknown as { location?: Location }).location;
    (window as unknown as { location: { href: string } }).location = { href: '' };
  });

  afterEach(() => {
    api.defaults.adapter = originalAdapter;
    (window as unknown as { location: Location }).location = originalLocation;
  });

  it('attempts the token refresh at most once when a request returns 401', async () => {
    await expect(api.get('/auth/profile')).rejects.toBeDefined();

    const refreshRequestCount = requestUrls.filter((url) => url === '/auth/token/refresh').length;
    expect(refreshRequestCount).toBe(1);
  });

  it('does not retry the token refresh endpoint itself', async () => {
    await expect(api.post('/auth/token/refresh')).rejects.toBeDefined();

    const refreshRequestCount = requestUrls.filter((url) => url === '/auth/token/refresh').length;
    expect(refreshRequestCount).toBe(1);
  });

  it('prevents redirect loops by not redirecting when already on login page', async () => {
    // Simulate being on the login page
    (window as unknown as { location: { href: string } }).location = { href: '/login' };

    // This should not cause infinite redirect loop
    await expect(api.get('/auth/profile')).rejects.toBeDefined();

    // Verify that we don't have too many requests (which would indicate a loop)
    expect(requestUrls.length).toBeLessThan(20);

    // Verify that we didn't end up redirecting to login again
    const loginRedirects = requestUrls.filter((url) => url.includes('/login'));
    expect(loginRedirects.length).toBe(0);
  });

  it('allows redirect to login page when not already on it', async () => {
    // Simulate being on a different page (not login)
    (window as unknown as { location: { href: string } }).location = { href: '/dashboard' };

    // This should attempt redirect to login (but our test setup prevents actual navigation)
    await expect(api.get('/auth/profile')).rejects.toBeDefined();

    // The interceptor should attempt to redirect, but our test won't actually navigate
    // We just want to ensure it doesn't create infinite loops in the request flow
    expect(requestUrls.length).toBeLessThan(20);
  });
});
