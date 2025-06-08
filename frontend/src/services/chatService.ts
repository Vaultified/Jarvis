import { sendMessage } from "./api";

interface ChatResponse {
  type: "chat";
  message: string;
}

export const processMessage = async (message: string): Promise<ChatResponse> => {
  try {
    const response = await sendMessage(message);
    console.log("API Response:", response); // Add logging
    return {
      type: "chat",
      message: response.message || "No response received",
    };
  } catch (error) {
    console.error("Error processing message:", error);
    throw error;
  }
};
