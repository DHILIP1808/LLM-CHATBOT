import { useState, useRef, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import { sendMessageToBot, sendMessageToBotWithFiles } from "../utils/api";
import MessageBubble from "./MessageBubble";
import MessageInput from "./MessageInput";
import ChatHeader from "./ChatHeader";
import { type Message } from "../types/message";
import { MessageCircle, Bot } from "lucide-react";

const ChatContainer = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle viewport height for mobile devices
  useEffect(() => {
    const setViewportHeight = () => {
      const vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    };

    setViewportHeight();
    window.addEventListener('resize', setViewportHeight);
    window.addEventListener('orientationchange', setViewportHeight);

    return () => {
      window.removeEventListener('resize', setViewportHeight);
      window.removeEventListener('orientationchange', setViewportHeight);
    };
  }, []);

  const handleSend = async (text: string, files?: File[]) => {
    // Create user message with text and file info
    let messageContent = text;
    if (files && files.length > 0) {
      const fileNames = files.map(f => f.name).join(', ');
      messageContent = text 
        ? `${text}\n\n📎 Attached files: ${fileNames}`
        : `📎 Attached files: ${fileNames}`;
    }

    const userMsg: Message = { 
      id: uuidv4(), 
      sender: "user", 
      content: messageContent,
      files: files
    };
    
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      let response: string;
      
      if (files && files.length > 0) {
        // Handle file upload
        response = await sendMessageToBotWithFiles(text, files);
      } else {
        // Regular text message
        response = await sendMessageToBot(text);
      }
      
      const botMsg: Message = { 
        id: uuidv4(), 
        sender: "bot", 
        content: response 
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMsg: Message = {
        id: uuidv4(),
        sender: "bot",
        content: "I apologize, but I'm having trouble connecting right now. Please try again.",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="w-full flex flex-col bg-white shadow-xl overflow-hidden border border-gray-200"
      style={{ height: 'calc(var(--vh, 1vh) * 100)' }}
    >
      <ChatHeader />
      
      <div className="flex-1 overflow-hidden bg-gradient-to-b from-gray-50 to-white min-h-0">
        <style>{`
          .hide-scrollbar {
            -ms-overflow-style: none;
            scrollbar-width: none;
          }
          .hide-scrollbar::-webkit-scrollbar {
            display: none;
          }
          
          /* Mobile-specific adjustments */
          @media (max-width: 768px) {
            .mobile-container {
              height: calc(100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom));
              height: calc(100dvh);
            }
            
            .mobile-messages {
              padding: 1rem 0.75rem;
            }
            
            .mobile-welcome {
              padding: 1rem;
            }
          }
          
          /* Support for dynamic viewport units */
          @supports (height: 100dvh) {
            .mobile-container {
              height: 100dvh;
            }
          }
        `}</style>
        
        <div className="h-full overflow-y-auto hide-scrollbar">
          <div className="max-w-4xl mx-auto px-6 py-6 space-y-2 mobile-messages">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center mobile-welcome">
                <div className="w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4 md:mb-6 shadow-lg">
                  <MessageCircle className="w-8 h-8 md:w-10 md:h-10 text-white" />
                </div>
                <h3 className="text-xl md:text-2xl font-bold text-gray-800 mb-2 md:mb-3">Welcome to AI Assistant</h3>
                <p className="text-gray-500 max-w-md text-base md:text-lg leading-relaxed px-4">
                  Start a conversation by typing a message below. You can also attach files! I'm here to help with any questions you have.
                </p>
              </div>
            )}
            
            {messages.map((msg, index) => (
              <MessageBubble 
                key={msg.id} 
                message={msg} 
                isLatest={index === messages.length - 1}
              />
            ))}
            
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="flex items-end space-x-2">
                  <div className="w-6 h-6 md:w-8 md:h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center shadow-sm">
                    <Bot className="w-3 h-3 md:w-4 md:h-4 text-white" />
                  </div>
                  <div className="bg-white rounded-2xl px-3 py-2 md:px-4 md:py-3 shadow-sm border border-gray-200">
                    <div className="flex space-x-1 items-center">
                      <div className="w-3 h-3 md:w-4 md:h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-xs md:text-sm text-gray-500 ml-2">Thinking...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>
      
      <MessageInput onSend={handleSend} isLoading={isLoading} />
    </div>
  );
};

export default ChatContainer;