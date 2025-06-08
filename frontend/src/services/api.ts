import axios from "axios";

const API_URL = "http://localhost:8000/api";

interface ChatResponse {
  type: string;
  message: string;
}

export const sendMessage = async (message: string): Promise<ChatResponse> => {
  try {
    const response = await axios.post(
      "http://localhost:8000/api/chat",
      {
        prompt: message,
      },
      {
        timeout: 120000, // 2 minutes timeout for Drive operations
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    console.log("Raw API Response:", response.data); // Add logging
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.code === "ECONNABORTED") {
        throw new Error("Request timed out. Please try again.");
      }
      if (error.response?.status === 401) {
        throw new Error("Authentication expired. Please re-authenticate.");
      }
      throw new Error(
        error.response?.data?.detail || "An error occurred while processing your request."
      );
    }
    throw error;
  }
};
