import { useState } from "react";
import { motion } from "framer-motion";
import { Send, Sparkles, Paperclip } from "lucide-react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";

interface QueryInputProps {
  onSubmit: (query: string) => void;
  disabled?: boolean;
  onAttachClick?: () => void;
  hasFiles?: boolean;
}

const QueryInput = ({ onSubmit, disabled, onAttachClick, hasFiles }: QueryInputProps) => {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !disabled) {
      onSubmit(query);
      setQuery("");
    }
  };

  const exampleQueries = [
    "Summarize the key findings from these documents",
    "What are the main themes discussed?",
    "Compare and contrast the documents",
  ];

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="flex items-end gap-2">
        {/* Attach Button */}
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={onAttachClick}
          disabled={disabled}
          className="shrink-0 hover:bg-primary/10 hover:text-primary transition-colors"
        >
          <Paperclip className={`w-5 h-5 ${hasFiles ? 'text-primary' : ''}`} />
        </Button>

        {/* Input Area */}
        <div className="flex-1 relative">
          <Textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything... (attach documents if needed)"
            disabled={disabled}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            className="min-h-[60px] max-h-[200px] bg-background/50 border-border/50 focus:border-primary resize-none pr-12"
          />
          
          {/* Example queries on focus */}
          {query === "" && !disabled && (
            <div className="absolute top-full left-0 right-0 mt-2 glass-card rounded-xl p-3 space-y-2 z-10">
              <p className="text-xs text-muted-foreground">Quick examples:</p>
              <div className="flex flex-wrap gap-2">
                {exampleQueries.map((example, index) => (
                  <motion.button
                    key={index}
                    type="button"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.05 * index }}
                    onClick={() => setQuery(example)}
                    className="text-xs px-2 py-1 rounded-full bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 transition-colors"
                  >
                    {example}
                  </motion.button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Send Button */}
        <Button
          type="submit"
          disabled={!query.trim() || disabled}
          size="icon"
          className="shrink-0 bg-gradient-to-r from-primary to-secondary hover:shadow-lg hover:shadow-primary/30 transition-all disabled:opacity-50"
        >
          <Send className="w-5 h-5" />
        </Button>
      </div>
    </form>
  );
};

export default QueryInput;
