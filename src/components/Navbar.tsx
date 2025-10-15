import { Brain } from "lucide-react";
import { motion } from "framer-motion";

const Navbar = () => {
  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="sticky top-0 z-50 backdrop-blur-lg border-b border-border/50"
    >
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Brain className="w-8 h-8 text-primary animate-pulse-glow" />
              <div className="absolute inset-0 blur-xl bg-primary/30 animate-pulse-glow" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                Knowledge Explorer
              </h1>
              <p className="text-xs text-muted-foreground">RAG-Powered Search Engine</p>
            </div>
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
