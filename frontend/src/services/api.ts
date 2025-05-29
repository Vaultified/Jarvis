import axios from "axios";

const API_URL = "http://localhost:8000/api";

interface ChatResponse {
  type: "chat";
  message?: string;
  content?: string;
}

export const sendMessage = async (message: string): Promise<ChatResponse> => {
  try {
    const response = await axios.post(`${API_URL}/chat`, { prompt: message });
    return {
      type: "chat",
      content: response.data.response,
    };
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
};
