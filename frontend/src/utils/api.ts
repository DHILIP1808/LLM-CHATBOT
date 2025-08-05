import axios from "axios";

export const sendMessageToBot = async (message: string) => {
  const response = await axios.post("http://localhost:8000/chat", { message });
  return response.data.response;
};
