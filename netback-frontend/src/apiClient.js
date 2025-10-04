import axios from "axios";

const baseURL = process.env.REACT_APP_API_URL || "/api";

const apiClient = axios.create({
  baseURL,
  timeout: 15000,
});

// Request interceptor: attach token if present
apiClient.interceptors.request.use(
  (config) => {
    try {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (e) {
      // Log at debug level in case of storage access errors (e.g. private mode)
      // eslint-disable-next-line no-console
      console.debug(e);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
      if (status === 401) {
      try {
        localStorage.removeItem("token");
      } catch (e) {
        // eslint-disable-next-line no-console
        console.debug(e);
      }
      // redirect to login
      if (typeof window !== "undefined") {
        window.location.href = "/";
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
