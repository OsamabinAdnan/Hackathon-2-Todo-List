'use client';

import { useState, useRef, useEffect } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SendIcon, BotIcon, XIcon, MessageSquareIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { sendMessage } from '@/lib/api/chat';
import { getUserId } from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';

// Toast styling consistent with the rest of the app
const toastClassNames = {
  toast: 'glass-toast font-mono',
  title: 'glass-toast-title font-mono',
  description: 'glass-toast-description font-mono',
};

const toastSuccessClassNames = {
  toast: 'glass-toast-success font-mono',
  title: 'glass-toast-title font-mono',
  description: 'glass-toast-description font-mono',
};

const toastErrorClassNames = {
  toast: 'glass-toast-error font-mono',
  title: 'glass-toast-title font-mono',
  description: 'glass-toast-description font-mono',
};

const toastInfoClassNames = {
  toast: 'glass-toast-info font-mono',
  title: 'glass-toast-title font-mono',
  description: 'glass-toast-description font-mono',
};

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatKitWrapperProps {
  // No props needed - userId is obtained from auth token
}

export default function ChatKitWrapper({}: ChatKitWrapperProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your AI Todo Assistant. I can help you manage tasks using natural language. Try saying: "Add a task called Buy groceries" or "Show me all my pending tasks".',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');

    // Add user message
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Get user ID from JWT token
      const userId = getUserId();

      // Send to backend API
      const response = await sendMessage(userId, {
        conversation_id: conversationId,
        message: userMessage
      });

      // Update conversation ID if new
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMsg]);

      // Show notification for tool calls if any
      if (response.tool_calls && response.tool_calls.length > 0) {
        const action = response.tool_calls[0].tool.replace('_', ' ');
        toast.success(`Task ${action} completed`, {
          description: `Action completed successfully via chat`,
          duration: 4000,
          unstyled: true,
          classNames: toastSuccessClassNames,
        });

        // Invalidate the tasks cache to trigger a refresh on the dashboard
        queryClient.invalidateQueries({ queryKey: ['tasks'] });
      }

    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Message failed', {
        description: 'Failed to send message. Please try again.',
        duration: 4000,
        unstyled: true,
        classNames: toastErrorClassNames,
      });

      // Add error message
      const errorMsg: ChatMessage = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or check your connection.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: 'Hello! I\'m your AI Todo Assistant. I can help you manage tasks using natural language. Try saying: "Add a task called Buy groceries" or "Show me all my pending tasks".',
        timestamp: new Date()
      }
    ]);
    setConversationId(undefined);
    toast.info('Chat cleared', {
      description: 'Conversation history has been cleared',
      duration: 4000,
      unstyled: true,
      classNames: toastInfoClassNames,
    });
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 xs:bottom-6 xs:right-6 sm:bottom-8 sm:right-8 z-40 w-12 h-12 xs:w-14 xs:h-14 sm:w-16 sm:h-16 rounded-full bg-primary text-primary-foreground shadow-2xl hover:shadow-primary/40 flex items-center justify-center transition-all duration-300 transform hover:scale-110 active:scale-95 focus:outline-none focus:ring-4 focus:ring-primary/40"
        // size="icon"
      >
        <BotIcon className="h-10 w-10" />
      </button>
    );
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40"
        onClick={() => setIsOpen(false)}
      />

      {/* Chat Panel */}
      <Card className="fixed bottom-24 right-6 z-50 w-96 h-[600px] flex flex-col shadow-2xl border-white/20 bg-white/10 backdrop-blur-md">
        <CardHeader className="pb-3 border-b border-white/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                <BotIcon className="h-5 w-5 text-white" />
              </div>
              <div>
                <CardTitle className="text-lg font-semibold">Taskify Assistant</CardTitle>
                <p className="text-sm text-muted-foreground">Ask me to manage your tasks</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(false)}
              className="h-8 w-8 rounded-full hover:bg-white/20"
            >
              <XIcon className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="flex-1 overflow-hidden p-0">
          {/* Messages Container */}
          <div className="h-full flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex gap-3',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && (
                    <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex-shrink-0 flex items-center justify-center">
                      <BotIcon className="h-4 w-4 text-white" />
                    </div>
                  )}

                  <div
                    className={cn(
                      'max-w-[80%] rounded-2xl px-4 py-3',
                      message.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-none'
                        : 'bg-white/20 backdrop-blur-sm border border-white/30 rounded-bl-none'
                    )}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className={cn(
                      'text-xs mt-1',
                      message.role === 'user' ? 'text-blue-200' : 'text-muted-foreground'
                    )}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>

                  {message.role === 'user' && (
                    <div className="h-8 w-8 rounded-full bg-gray-600 flex-shrink-0 flex items-center justify-center">
                      <MessageSquareIcon className="h-4 w-4 text-white" />
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-white/20 p-4 bg-white/5">
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Input
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message here..."
                    className="pr-10 bg-white/10 border-white/20 focus:border-blue-500"
                    disabled={isLoading}
                  />
                  {isLoading && (
                    <div className="absolute right-3 top-3">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    </div>
                  )}
                </div>
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  <SendIcon className="h-4 w-4" />
                </Button>
              </div>

              {/* Quick Actions */}
              <div className="flex gap-2 mt-3 flex-wrap">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInputValue('Show me all my tasks')}
                  className="text-xs bg-white/5 border-white/20 hover:bg-white/10"
                >
                  Show tasks
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInputValue('Add a task to buy groceries')}
                  className="text-xs bg-white/5 border-white/20 hover:bg-white/10"
                >
                  Add task
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInputValue('What tasks are pending?')}
                  className="text-xs bg-white/5 border-white/20 hover:bg-white/10"
                >
                  Pending
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearChat}
                  className="text-xs bg-white/5 border-white/20 hover:bg-white/10"
                >
                  Clear
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </>
  );
}