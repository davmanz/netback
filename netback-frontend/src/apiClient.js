import axios from "axios";
import { getAccessToken, setAccessToken, clearAuth } from "./auth";
import { getCookie } from "./csrf";

const baseURL = process.env.REACT_APP_API_URL || "/api";

const apiClient = axios.create({
  baseURL,
  timeout: 15000,
  withCredentials: true, // send cookies (refresh token)
});

// Request interceptor: attach access token from memory
apiClient.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Attach X-CSRF-Token for mutating requests (double-submit)
    const method = (config.method || "GET").toUpperCase();
    if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
      const xsrf = getCookie("XSRF-TOKEN");
      if (xsrf) {
        config.headers = config.headers || {};
        config.headers["X-CSRF-Token"] = xsrf;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 with refresh flow
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((p) => {
    if (error) p.reject(error);
    else p.resolve(token);
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error?.response?.status;

    if (status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Refresh endpoint should read refresh cookie and return new access
        const refreshRes = await axios.post(`${baseURL}/token/refresh/`, {}, { withCredentials: true });
        const newAccess = refreshRes.data?.access;
        if (newAccess) {
          setAccessToken(newAccess);
          apiClient.defaults.headers.common["Authorization"] = `Bearer ${newAccess}`;
        }
        processQueue(null, newAccess);
        isRefreshing = false;
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return apiClient(originalRequest);
      } catch (err) {
        processQueue(err, null);
        isRefreshing = false;
        clearAuth();
        if (typeof window !== "undefined") {
          window.location.href = "/";
        }
        return Promise.reject(err);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
