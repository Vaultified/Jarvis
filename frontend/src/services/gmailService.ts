import axios from "axios";

const API_URL = "http://localhost:8000/api/gmail";

interface EmailResponse {
  success: boolean;
  message: string;
  details?: {
    error?: string;
  };
}

export const sendEmail = async (
  to: string,
  subject: string,
  body: string
): Promise<EmailResponse> => {
  try {
    const response = await axios.post(`${API_URL}/send`, {
      to: [to],
      subject,
      body,
    });
    return response.data;
  } catch (error) {
    console.error("Error sending email:", error);
    throw error;
  }
};
