import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, File, X, CheckCircle } from "lucide-react";
import { Button } from "./ui/button";
import { useToast } from "@/hooks/use-toast";
import { uploadFiles as apiUploadFiles } from "@/lib/api";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  uploaded?: boolean;
  uploading?: boolean;
}

interface FileUploadProps {
  onFilesChange: (files: UploadedFile[]) => void;
}

const FileUpload = ({ onFilesChange }: FileUploadProps) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const { toast } = useToast();

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      addFiles(selectedFiles);
    }
  };

  const addFiles = async (newFiles: File[]) => {
    // Add files with uploading status
    const uploadedFiles: UploadedFile[] = newFiles.map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      uploading: true,
      uploaded: false,
    }));

    const tempFiles = [...files, ...uploadedFiles];
    setFiles(tempFiles);
    
    try {
      // Upload to backend
      const result = await apiUploadFiles(newFiles);
      
      // Mark files as uploaded
      const finalFiles = tempFiles.map(f => ({
        ...f,
        uploading: false,
        uploaded: true,
      }));
      
      setFiles(finalFiles);
      onFilesChange(finalFiles);
      
      toast({
        title: "Files uploaded successfully",
        description: `${newFiles.length} file(s) uploaded and processed`,
      });
    } catch (error) {
      console.error("Upload failed:", error);
      
      // Remove failed files
      setFiles(files);
      
      toast({
        variant: "destructive",
        title: "Upload failed",
        description: error instanceof Error ? error.message : "Failed to upload files to backend",
      });
    }
  };

  const removeFile = (id: string) => {
    const updatedFiles = files.filter((f) => f.id !== id);
    setFiles(updatedFiles);
    onFilesChange(updatedFiles);
  };

  return (
    <div className="space-y-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`
          relative glass-card rounded-2xl p-8 transition-all duration-300
          ${isDragging ? "scale-105 glow-effect" : ""}
        `}
      >
        <div className="flex flex-col items-center gap-4 text-center">
          <motion.div
            animate={isDragging ? { scale: 1.1 } : { scale: 1 }}
            className="relative"
          >
            <Upload className="w-12 h-12 text-primary" />
            {isDragging && (
              <motion.div
                animate={{ scale: [1, 1.5, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
                className="absolute inset-0 blur-xl bg-primary/30 rounded-full"
              />
            )}
          </motion.div>
          
          <div>
            <h3 className="text-lg font-semibold">Upload Documents</h3>
            <p className="text-sm text-muted-foreground">
              Drag & drop files here or click to browse
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Supports PDF, TXT, DOCX, and more
            </p>
          </div>

          <label htmlFor="file-upload">
            <Button
              type="button"
              className="relative overflow-hidden bg-gradient-to-r from-primary to-secondary hover:shadow-lg hover:shadow-primary/30 transition-all"
              onClick={() => document.getElementById("file-upload")?.click()}
            >
              <span className="relative z-10">Choose Files</span>
            </Button>
          </label>
          <input
            id="file-upload"
            type="file"
            multiple
            onChange={handleFileInput}
            className="hidden"
            accept=".pdf,.txt,.doc,.docx"
          />
        </div>
      </motion.div>

      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2"
          >
            <h4 className="text-sm font-medium text-foreground/80">
              Uploaded Files ({files.length})
            </h4>
            {files.map((file, index) => (
              <motion.div
                key={file.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
                className="glass-card rounded-xl p-4 flex items-center justify-between hover:shadow-lg transition-all"
              >
                <div className="flex items-center gap-3">
                  {file.uploading ? (
                    <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  ) : file.uploaded ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <File className="w-5 h-5 text-primary" />
                  )}
                  <div>
                    <p className="text-sm font-medium">{file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {(file.size / 1024).toFixed(2)} KB
                      {file.uploading && " - Uploading..."}
                      {file.uploaded && " - Uploaded"}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeFile(file.id)}
                  className="hover:bg-destructive/10 hover:text-destructive"
                  disabled={file.uploading}
                >
                  <X className="w-4 h-4" />
                </Button>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FileUpload;
