import axios from "axios";

const API_URL = "http://localhost:8000/api/gmail";

export const sendEmail = async (to, subject, body) => {
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
