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
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle mobile viewport and keyboard
  useEffect(() => {
    const setMobileViewport = () => {
      // Set CSS custom property for real viewport height
      let vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    };

    const handleResize = () => {
      setMobileViewport();
      // Small delay to ensure DOM is updated
      setTimeout(scrollToBottom, 100);
    };

    const handleVisibilityChange = () => {
      if (!document.hidden) {
        setTimeout(() => {
          setMobileViewport();
          scrollToBottom();
        }, 300);
      }
    };

    // Initial setup
    setMobileViewport();

    // Event listeners
    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);
    window.addEventListener('focusin', handleResize);
    window.addEventListener('focusout', handleResize);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
      window.removeEventListener('focusin', handleResize);
      window.removeEventListener('focusout', handleResize);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
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

    // Scroll to bottom after adding user message
    setTimeout(scrollToBottom, 100);

    try {
      let response: string;
      
      if (files && files.length > 0) {
        response = await sendMessageToBotWithFiles(text, files);
      } else {
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
    <>
      
      
      <div className="chat-container w-full bg-white shadow-xl border border-gray-200">
        {/* Header - Fixed */}
        <ChatHeader />
        
        {/* Messages Area - Scrollable */}
        <div 
          ref={messagesContainerRef}
          className="messages-area bg-gradient-to-b from-gray-50 to-white hide-scrollbar"
        >
          <div className="messages-container">
            <div className="max-w-4xl mx-auto w-full">
              <div className="messages-content space-y-2">
                {messages.length === 0 && (
                  <div className="welcome-container flex flex-col items-center justify-center text-center">
                    <div className="welcome-icon bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
                      <MessageCircle className="w-8 h-8 md:w-10 md:h-10 text-white" />
                    </div>
                    <h3 className="welcome-title font-bold text-gray-800">Welcome to AI Assistant</h3>
                    <p className="welcome-text text-gray-500 max-w-md">
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
                  <div className="loading-container flex justify-start">
                    <div className="flex items-end space-x-2">
                      <div className="loading-avatar bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center shadow-sm">
                        <Bot className="loading-icon text-white" />
                      </div>
                      <div className="loading-bubble bg-white rounded-2xl shadow-sm border border-gray-200">
                        <div className="flex space-x-1 items-center">
                          <div className="loading-spinner border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                          <span className="loading-text text-gray-500 ml-2">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            </div>
          </div>
        </div>
        
        {/* Input - Fixed at bottom */}
        <div className="input-container">
          <MessageInput onSend={handleSend} isLoading={isLoading} />
        </div>
      </div>
    </>
  );
};

export default ChatContainer;