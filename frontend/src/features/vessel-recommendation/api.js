import apiClient from "../../shared/apiClient";

export async function getVesselRecommendation(payload) {
  const response = await apiClient.post("/api/recommend", payload);
  return response.data;
}