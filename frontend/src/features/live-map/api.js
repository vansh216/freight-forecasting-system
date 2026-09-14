import apiClient from "../../shared/apiClient";

export async function getLiveVessels(port = null) {
  const params = port && port !== "All Ports" ? { port } : {};
  const response = await apiClient.get("/api/live-vessels", { params });
  return response.data;
}