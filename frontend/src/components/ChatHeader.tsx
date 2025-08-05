import { Bot } from "lucide-react";

const ChatHeader = () => (
  <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 shadow-sm">
    <div className="flex items-center space-x-3">
      <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
        <Bot className="w-5 h-5 text-white" />
      </div>
      <div>
        <h1 className="text-lg font-semibold">AI Assistant</h1>
        <p className="text-blue-100 text-sm">Always here to help</p>
      </div>
      <div className="ml-auto">
        <div className="w-3 h-3 bg-green-400 rounded-full shadow-sm"></div>
      </div>
    </div>
  </div>
);

export default ChatHeader;