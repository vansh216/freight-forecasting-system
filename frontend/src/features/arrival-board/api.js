import apiClient from "../../shared/apiClient";

export async function getArrivals(port = null) {
  const params = port && port !== "All Ports" ? { port } : {};
  const response = await apiClient.get("/api/arrivals", { params });
  return response.data;
}