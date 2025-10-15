import { motion } from "framer-motion";
import { FileText, ChevronRight } from "lucide-react";

interface Document {
  id: string;
  name: string;
  size: number;
}

interface DocumentListProps {
  documents: Document[];
}

const DocumentList = ({ documents }: DocumentListProps) => {
  if (documents.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-card rounded-2xl p-6 space-y-4"
    >
      <div className="flex items-center gap-2 pb-3 border-b border-border/50">
        <FileText className="w-5 h-5 text-primary" />
        <h3 className="font-semibold">Document Library</h3>
        <span className="ml-auto text-xs text-muted-foreground">
          {documents.length} {documents.length === 1 ? "file" : "files"}
        </span>
      </div>

      <div className="space-y-2 max-h-[400px] overflow-y-auto custom-scrollbar">
        {documents.map((doc, index) => (
          <motion.div
            key={doc.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="group p-3 rounded-xl bg-background/50 hover:bg-primary/5 border border-transparent hover:border-primary/20 transition-all cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate group-hover:text-primary transition-colors">
                  {doc.name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {(doc.size / 1024).toFixed(2)} KB
                </p>
              </div>
              <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default DocumentList;
