import { sendMessage } from "./api";

interface ChatResponse {
  type: "chat" | "image";
  message: string;
}

export const processMessage = async (message: string): Promise<ChatResponse> => {
  console.log("processMessage called with:", message);
  try {
    console.log("Processing message:", message);
    const response = await sendMessage(message);
    console.log("Raw API response:", response);

    if (!response || typeof response !== "object") {
      throw new Error("Invalid response from server");
    }

    const { type, message: responseMessage } = response;
    console.log("Response type:", type);
    console.log("Response message length:", responseMessage?.length);

    // Handle image response
    if (type === "image" && responseMessage) {
      console.log("Processing image response");
      // Ensure the message is a base64 string
      if (typeof responseMessage !== "string") {
        throw new Error("Invalid image data format");
      }

      // Check if it's already a data URL
      if (responseMessage.startsWith("data:image")) {
        console.log("Message is already a data URL");
        return {
          type: "image",
          message: responseMessage,
        };
      }

      // Construct data URL from base64
      console.log("Constructing data URL from base64");
      const dataUrl = `data:image/png;base64,${responseMessage}`;
      console.log("Data URL constructed:", dataUrl.substring(0, 100) + "...");

      // Create a new response object
      const imageResponse: ChatResponse = {
        type: "image",
        message: dataUrl,
      };
      console.log("Returning image response:", imageResponse);
      return imageResponse;
    }

    // Handle text response
    const textResponse: ChatResponse = {
      type: "chat",
      message: responseMessage || "No response received",
    };
    console.log("Returning text response:", textResponse);
    return textResponse;
  } catch (error) {
    console.error("Error processing message:", error);
    throw error;
  }
};
