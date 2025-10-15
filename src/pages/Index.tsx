import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import FileUpload from "@/components/FileUpload";
import QueryInput from "@/components/QueryInput";
import ChatOutput from "@/components/ChatOutput";
import DocumentList from "@/components/DocumentList";
import Loader from "@/components/Loader";
import { Sparkles, Paperclip } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { query as apiQuery } from "@/lib/api";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
}

interface ChatMessage {
  id: string;
  query: string;
  response: string;
  sources?: string[];
}

const Index = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleQuery = async (queryText: string) => {
    setIsLoading(true);

    try {
      // Call the actual backend API
      const result = await apiQuery(queryText, 5);

      const newMessage: ChatMessage = {
        id: Math.random().toString(36).substr(2, 9),
        query: queryText,
        response: result.answer,
        sources: result.sources?.map(s => s.filename) || [],
      };

      setMessages([...messages, newMessage]);
    } catch (error) {
      console.error("Query failed:", error);
      
      // Show error message to user
      const errorMessage: ChatMessage = {
        id: Math.random().toString(36).substr(2, 9),
        query: queryText,
        response: `Sorry, I encountered an error processing your question. Please make sure:\n\n1. You have uploaded documents first\n2. The backend server is running (http://localhost:8000)\n3. Your API keys are configured correctly\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}`,
        sources: [],
      };
      
      setMessages([...messages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const [showFileUpload, setShowFileUpload] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-background via-background to-primary/5">
      <Navbar />
      
      <main className="flex-1 flex flex-col max-w-5xl mx-auto w-full px-4 py-6">
        {/* Welcome Header - Only show when no messages */}
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="text-center mb-8 mt-12"
            >
              <motion.div
                animate={{ 
                  scale: [1, 1.05, 1],
                  rotate: [0, 5, -5, 0] 
                }}
                transition={{ 
                  duration: 4, 
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                className="inline-block mb-6"
              >
                <Sparkles className="w-20 h-20 text-primary animate-pulse-glow" />
              </motion.div>
              
              <h1 className="text-5xl md:text-7xl font-bold mb-4">
                <span className="bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
                  Knowledge Explorer
                </span>
              </h1>
              
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
                Ask anything. Attach documents when needed.
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Chat Messages Area */}
        <div className="flex-1 overflow-y-auto mb-6 space-y-4">
          {isLoading && messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <Loader />
            </motion.div>
          )}
          
          {messages.length > 0 && (
            <>
              <ChatOutput messages={messages} />
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Loader />
                </motion.div>
              )}
            </>
          )}
        </div>

        {/* Fixed Bottom Input Area */}
        <div className="sticky bottom-0 pb-4">
          {/* Attached Files Indicator */}
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-3 flex items-center gap-2 flex-wrap"
            >
              {files.map((file) => (
                <motion.div
                  key={file.id}
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="glass-card px-3 py-1.5 rounded-full flex items-center gap-2 text-sm"
                >
                  <Paperclip className="w-3 h-3 text-primary" />
                  <span className="text-foreground/80">{file.name}</span>
                </motion.div>
              ))}
            </motion.div>
          )}

          {/* Input with Attach Button */}
          <div className="glass-card rounded-2xl p-4">
            <QueryInput 
              onSubmit={handleQuery} 
              disabled={isLoading}
              onAttachClick={() => setShowFileUpload(true)}
              hasFiles={files.length > 0}
            />
          </div>
        </div>
      </main>

      <Footer />

      {/* File Upload Sheet */}
      <Sheet open={showFileUpload} onOpenChange={setShowFileUpload}>
        <SheetContent side="bottom" className="h-[80vh] overflow-y-auto">
          <SheetHeader>
            <SheetTitle className="flex items-center gap-2">
              <Paperclip className="w-5 h-5 text-primary" />
              Attach Documents
            </SheetTitle>
          </SheetHeader>
          <div className="mt-6">
            <FileUpload onFilesChange={(newFiles) => {
              setFiles(newFiles);
              if (newFiles.length > files.length) {
                setTimeout(() => setShowFileUpload(false), 800);
              }
            }} />
            {files.length > 0 && (
              <div className="mt-6">
                <DocumentList documents={files} />
              </div>
            )}
          </div>
        </SheetContent>
      </Sheet>

      {/* Background decoration */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-48 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-1/4 -right-48 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-float" style={{ animationDelay: "1s" }} />
      </div>
    </div>
  );
};

export default Index;
