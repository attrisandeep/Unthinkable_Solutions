import { motion, AnimatePresence } from "framer-motion";
import { Copy, Check, ExternalLink } from "lucide-react";
import { Button } from "./ui/button";
import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";

interface ChatMessage {
  id: string;
  query: string;
  response: string;
  sources?: string[];
}

interface ChatOutputProps {
  messages: ChatMessage[];
}

const ChatOutput = ({ messages }: ChatOutputProps) => {
  return (
    <div className="space-y-4">
      <AnimatePresence mode="popLayout">
        {messages.map((message, index) => (
          <MessageBubble key={message.id} message={message} index={index} />
        ))}
      </AnimatePresence>
    </div>
  );
};

const MessageBubble = ({ message, index }: { message: ChatMessage; index: number }) => {
  const [copied, setCopied] = useState(false);
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    if (message.response) {
      let currentIndex = 0;
      const typingInterval = setInterval(() => {
        if (currentIndex < message.response.length) {
          setDisplayedText(message.response.slice(0, currentIndex + 1));
          currentIndex++;
        } else {
          setIsTyping(false);
          clearInterval(typingInterval);
        }
      }, 20);

      return () => clearInterval(typingInterval);
    }
  }, [message.response]);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.response);
    setCopied(true);
    toast({
      title: "Copied to clipboard",
      description: "Response copied successfully",
    });
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className="space-y-3"
    >
      {/* Query Bubble */}
      <div className="flex justify-end">
        <motion.div
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          className="glass-card rounded-2xl rounded-tr-sm p-4 max-w-[80%] bg-gradient-to-r from-primary/10 to-secondary/10 border-primary/20"
        >
          <p className="text-sm">{message.query}</p>
        </motion.div>
      </div>

      {/* Response Bubble */}
      <div className="flex justify-start">
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="glass-card rounded-2xl rounded-tl-sm p-5 max-w-[85%] space-y-3"
        >
          <div className="prose prose-sm max-w-none">
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {displayedText}
              {isTyping && (
                <motion.span
                  animate={{ opacity: [1, 0] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                  className="inline-block w-1 h-4 ml-1 bg-primary"
                />
              )}
            </p>
          </div>

          {message.sources && message.sources.length > 0 && (
            <div className="pt-3 border-t border-border/50">
              <p className="text-xs font-medium text-muted-foreground mb-2">Sources:</p>
              <div className="space-y-1">
                {message.sources.map((source, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * idx }}
                    className="flex items-center gap-2 text-xs text-primary hover:text-secondary transition-colors"
                  >
                    <ExternalLink className="w-3 h-3" />
                    <span>{source}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end pt-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className="h-7 text-xs hover:bg-primary/10"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3 mr-1" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3 mr-1" />
                  Copy
                </>
              )}
            </Button>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default ChatOutput;
