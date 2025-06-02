import { sendMessage } from "./api";

interface ChatResponse {
  type: "chat"; // Simplified type to only chat
  message?: string;
  content?: string;
}

export const processMessage = async (message: string): Promise<ChatResponse> => {
  // Removed Gmail command check
  // const gmailMatch =
  //   message.match(GMAIL_PATTERNS.SEND_EMAIL) || message.match(GMAIL_PATTERNS.SEND_EMAIL_SIMPLE);

  // if (gmailMatch) {
  //   // Removed Gmail handling logic
  // } else {
  // If not a tool command, process as regular chat message by sending to backend
  // The backend will now handle tool detection
  return await sendMessage(message);
  // }
};
