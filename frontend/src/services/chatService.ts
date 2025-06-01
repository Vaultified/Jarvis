import { sendMessage } from "./api";
// import { sendEmail } from "./gmailService"; // Removed Gmail service import

interface ChatResponse {
  type: "chat"; // Simplified type to only chat
  message?: string;
  content?: string;
  // Removed gmail related fields
  // isGmail?: boolean;
  // success?: boolean;
  // error?: string;
  // details?: {
  //   error?: string;
  // };
}

// Removed Gmail command regex patterns
// const GMAIL_PATTERNS = {
//   SEND_EMAIL:
//     /send (?:an |a )?email to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}) (?:with the |about |subject |with |and the )?subject ["|']([^"]+)["|'] (?:saying |message |content |body |and the )?body ["|']([^"]+)["|']/i,
//   SEND_EMAIL_SIMPLE:
//     /send (?:an |a )?email to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}) (?:about |subject )?['"]([^'"]+)['"] (?:saying |message )?['"]([^'"]+)['']/i,
// };

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
