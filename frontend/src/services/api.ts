import axios from "axios";

const API_URL = "http://localhost:8000/api";

interface ChatResponse {
  type: "chat" | "image";
  message: string;
}

export const sendMessage = async (message: string): Promise<ChatResponse> => {
  try {
    console.log("Sending request to API:", message);
    const response = await axios.post(
      `${API_URL}/chat`,
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
    console.log("Raw API Response:", response.data);

    // Validate response data
    if (!response.data || typeof response.data !== "object") {
      throw new Error("Invalid response format from server");
    }

    // Ensure we have the required fields
    if (!response.data.type || !response.data.message) {
      throw new Error("Missing required fields in response");
    }

    // Ensure the type is either "chat" or "image"
    if (response.data.type !== "chat" && response.data.type !== "image") {
      throw new Error("Invalid response type");
    }

    // For image responses, ensure the message is a string
    if (response.data.type === "image" && typeof response.data.message !== "string") {
      throw new Error("Invalid image data format");
    }

    return {
      type: response.data.type,
      message: response.data.message,
    };
  } catch (error) {
    console.error("API Error:", error);
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
