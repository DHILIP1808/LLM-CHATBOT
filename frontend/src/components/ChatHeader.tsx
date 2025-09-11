import { Bot } from "lucide-react";

const ChatHeader = () => (
  <div className="bg-white border-b border-gray-200 px-6 py-4">
    <div className="flex items-center justify-between max-w-screen-2xl mx-auto">
      <div className="flex items-center space-x-4">
        <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
          <Bot className="w-5 h-5 text-blue-600" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-gray-900">AI Assistant</h1>
          <p className="text-sm text-gray-500">Enterprise Intelligence</p>
        </div>
      </div>
      
    </div>
  </div>
);

export default ChatHeader;