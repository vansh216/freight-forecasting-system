import apiClient from "../../shared/apiClient";

export async function getForecast(payload) {
  const response = await apiClient.post("/api/forecast", payload);
  return response.data;
}