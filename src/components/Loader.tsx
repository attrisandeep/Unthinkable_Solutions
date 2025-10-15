import { motion } from "framer-motion";
import { Brain } from "lucide-react";

const Loader = () => {
  return (
    <div className="flex flex-col items-center gap-4 py-8">
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="relative"
      >
        <Brain className="w-12 h-12 text-primary" />
        <motion.div
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.5, 0.8, 0.5],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute inset-0 blur-2xl bg-primary/40 rounded-full"
        />
      </motion.div>
      
      <div className="flex gap-2">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            animate={{
              y: [0, -10, 0],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: i * 0.2,
              ease: "easeInOut",
            }}
            className="w-2 h-2 rounded-full bg-primary"
          />
        ))}
      </div>
      
      <p className="text-sm text-muted-foreground animate-pulse">
        AI is thinking...
      </p>
    </div>
  );
};

export default Loader;
