import axios from "axios";

export const sendMessageToBot = async (message: string) => {
  const response = await axios.post("http://localhost:8000/chat", { message });
  return response.data.response;
};

export const sendMessageToBotWithFiles = async (message: string, files: File[]): Promise<string> => {
  const formData = new FormData();
  formData.append('message', message);
  
  files.forEach((file) => {
    formData.append('files', file);
  });

  const response = await axios.post("http://localhost:8000/chat-with-files", formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data.response;
};