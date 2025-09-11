// types/message.ts
export interface Message {
  id: string;
  sender: "user" | "bot";
  content: string;
  files?: File[]; // Optional files array
  timestamp?: Date;
}