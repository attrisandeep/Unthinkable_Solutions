import { motion } from "framer-motion";

const Footer = () => {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5, duration: 0.5 }}
      className="py-6 border-t border-border/50 mt-auto"
    >
      <div className="container mx-auto px-6 text-center text-sm text-muted-foreground">
        <p>Powered by Advanced RAG Technology & Large Language Models</p>
      </div>
    </motion.footer>
  );
};

export default Footer;
