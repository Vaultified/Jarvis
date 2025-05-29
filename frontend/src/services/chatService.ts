import { sendMessage } from "./api";
import { sendEmail } from "./gmailService";

interface ChatResponse {
  type: "chat" | "gmail";
  message?: string;
  content?: string;
  success?: boolean;
  error?: string;
  details?: {
    error?: string;
  };
}

// Regular expressions for matching Gmail commands
const GMAIL_PATTERNS = {
  SEND_EMAIL:
    /send (?:an |a )?email to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}) (?:with |about |subject )?(?:is |of )?['"]([^'"]+)['"] (?:saying |message |content |body )?['"]([^'"]+)['"]/i,
  SEND_EMAIL_SIMPLE:
    /send (?:an |a )?email to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}) (?:about |subject )?['"]([^'"]+)['"] (?:saying |message )?['"]([^'"]+)['"]/i,
};

export const processMessage = async (message: string): Promise<ChatResponse> => {
  // Check for Gmail commands first
  const gmailMatch =
    message.match(GMAIL_PATTERNS.SEND_EMAIL) || message.match(GMAIL_PATTERNS.SEND_EMAIL_SIMPLE);

  if (gmailMatch) {
    try {
      const [_, to, subject, body] = gmailMatch;
      const result = await sendEmail(to, subject, body);

      if (result.success) {
        return {
          type: "gmail",
          success: true,
          message: `Email sent successfully to ${to}!`,
          details: result.details,
        };
      } else {
        return {
          type: "gmail",
          success: false,
          message: `Failed to send email: ${result.message}`,
          error: result.details?.error,
        };
      }
    } catch (error) {
      return {
        type: "gmail",
        success: false,
        message: "Failed to send email",
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  }

  // If not a Gmail command, process as regular chat message
  return await sendMessage(message);
};
