import { useState, useEffect } from "react";
import { type Message } from "../types/message";
import { Bot, User } from "lucide-react";

interface Props {
  message: Message;
  isLatest?: boolean;
  formatResponse?: (text: string) => string;
}

const MessageBubble = ({ message, isLatest, formatResponse }: Props) => {
  const isUser = message.sender === "user";
  const [displayedContent, setDisplayedContent] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const parseCodeBlocks = (content: string) => {
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)\n```/g;
    const inlineCodeRegex = /`([^`]+)`/g;
    let result = content;

    // Replace code blocks without copy button
    result = result.replace(codeBlockRegex, (_match, language, code) => {
      const languageLabel = language || 'text';
      const escapedCode = code.replace(/</g, '&lt;').replace(/>/g, '&gt;');

      return `<div class="code-block-container my-4 relative">
        <div class="bg-gray-900 rounded-lg overflow-hidden">
          <div class="px-4 py-2 bg-gray-800 text-gray-300 text-sm font-mono">
            ${languageLabel}
          </div>
          <pre class="p-4 overflow-x-auto"><code class="text-gray-100 font-mono text-sm leading-relaxed whitespace-pre">${escapedCode}</code></pre>
        </div>
      </div>`;
    });

    // Replace inline code
    result = result.replace(inlineCodeRegex, (_, code) => {
      const escapedCode = code.replace(/</g, '&lt;').replace(/>/g, '&gt;');
      return `<code class="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-gray-800">${escapedCode}</code>`;
    });

    // Convert line breaks to HTML
    result = result.replace(/\n/g, '<br>');

    return result;
  };

  useEffect(() => {
    if (!isUser && isLatest && message.content) {
      setIsTyping(true);
      setDisplayedContent("");

      let contentToFormat = message.content;
      if (formatResponse) {
        contentToFormat = formatResponse(message.content);
      }

      const formattedContent = parseCodeBlocks(contentToFormat);
      let currentIndex = 0;

      const typeWriter = () => {
        if (currentIndex < formattedContent.length) {
          setDisplayedContent(formattedContent.slice(0, currentIndex + 1));
          currentIndex++;
          setTimeout(typeWriter, 20);
        } else {
          setIsTyping(false);
        }
      };

      setTimeout(typeWriter, 300);
    } else {
      let formatted = isUser ? message.content : message.content;
      if (!isUser && formatResponse) {
        formatted = formatResponse(message.content);
      }
      formatted = parseCodeBlocks(formatted);
      setDisplayedContent(formatted);
    }
  }, [message.content, isUser, isLatest, formatResponse]);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex items-end space-x-2 max-w-[85%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-sm ${
          isUser 
            ? 'bg-gradient-to-br from-blue-500 to-blue-600' 
            : 'bg-gradient-to-br from-emerald-500 to-emerald-600'
        }`}>
          {isUser ? (
            <User className="w-4 h-4 text-white" />
          ) : (
            <Bot className="w-4 h-4 text-white" />
          )}
        </div>

        {/* Message Content */}
        <div className={`rounded-2xl px-4 py-3 shadow-sm border transition-all duration-200 hover:shadow-md overflow-hidden ${
          isUser
            ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white border-blue-300'
            : 'bg-white text-gray-800 border-gray-200'
        }`}>
          <div 
            className={`text-sm leading-relaxed ${isUser ? 'text-white' : 'text-gray-800'}`}
            dangerouslySetInnerHTML={{ __html: displayedContent }}
          />
          {isTyping && (
            <span className="inline-block w-2 h-4 bg-gray-400 ml-1 animate-pulse"></span>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
