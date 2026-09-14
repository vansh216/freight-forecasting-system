import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

export default apiClient;