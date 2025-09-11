import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "https://llm-chatbot-4nk4.onrender.com/";

export const sendMessageToBot = async (message: string) => {
  const response = await axios.post(`${API_BASE}/chat`, { message });
  return response.data.response;
};

export const sendMessageToBotWithFiles = async (
  message: string,
  files: File[]
): Promise<string> => {
  const formData = new FormData();
  formData.append("message", message);

  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await axios.post(`${API_BASE}/chat-with-files`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data.response;
};
