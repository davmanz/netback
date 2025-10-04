// Minimal in-memory auth helper. Not using localStorage for tokens.
let accessToken = null;
const subscribers = new Set();

export const setAccessToken = (token) => {
  accessToken = token;
  subscribers.forEach((s) => s(accessToken));
};

export const getAccessToken = () => accessToken;

export const clearAuth = () => {
  accessToken = null;
  subscribers.forEach((s) => s(accessToken));
};

export const subscribeAuth = (fn) => {
  subscribers.add(fn);
  return () => subscribers.delete(fn);
};

export default { setAccessToken, getAccessToken, clearAuth, subscribeAuth };
