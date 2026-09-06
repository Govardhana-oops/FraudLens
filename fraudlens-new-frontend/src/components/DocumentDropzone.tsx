import React, { useRef, useState } from "react";
import { Upload, Camera, FileCheck, X, Image as ImageIcon } from "lucide-react";
import clsx from "clsx";

interface DocumentDropzoneProps {
  onFileSelected?: (file: File | null) => void;
  onFileSelect?: (file: File | null) => void;
  selectedFile: File | null;
  label?: string;
  accept?: string;
}

export function DocumentDropzone({
  onFileSelected,
  onFileSelect,
  selectedFile,
  label = "Drag and drop document image here, or click to browse",
  accept = "image/jpeg,image/png,image/webp,image/tiff",
}: DocumentDropzoneProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleNotify = (file: File | null) => {
    if (onFileSelected) onFileSelected(file);
    if (onFileSelect) onFileSelect(file);
  };

  const handleFileChange = (file: File | null) => {
    if (file) {
      handleNotify(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      handleNotify(null);
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const onDragLeave = () => {
    setIsDragOver(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="w-full">
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => {
          if (e.target.files && e.target.files.length > 0) {
            handleFileChange(e.target.files[0]);
          }
        }}
      />

      {selectedFile ? (
        <div className="panel-3d p-4 flex items-center justify-between border-brand-teal/50 bg-canvas-850">
          <div className="flex items-center gap-3 overflow-hidden">
            {previewUrl ? (
              <img
                src={previewUrl}
                alt="Document Preview"
                className="h-12 w-12 rounded-lg object-cover border border-canvas-600 shrink-0"
              />
            ) : (
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-brand-teal/20 text-brand-teal border border-brand-teal/40 shrink-0">
                <FileCheck size={24} />
              </div>
            )}
            <div className="truncate">
              <p className="text-xs font-bold text-slateText-50 truncate">{selectedFile.name}</p>
              <p className="text-[11px] font-mono text-slateText-300">
                {(selectedFile.size / 1024).toFixed(1)} KB • {selectedFile.type || "image/jpeg"}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => handleFileChange(null)}
            className="p-1.5 rounded-lg bg-canvas-750 text-slateText-300 hover:text-accent-rose hover:bg-canvas-700 transition-colors"
            title="Remove file"
          >
            <X size={16} />
          </button>
        </div>
      ) : (
        <div
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
          className={clsx(
            "panel-dropzone group flex flex-col items-center justify-center gap-3 p-8 cursor-pointer text-center",
            isDragOver && "border-brand-teal bg-brand-teal/10 shadow-glow-teal"
          )}
        >
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-canvas-850 border border-canvas-600 group-hover:border-brand-teal/60 group-hover:bg-brand-teal/15 transition-all duration-150">
            <Upload className="h-7 w-7 text-brand-teal group-hover:scale-110 transition-transform" />
          </div>
          <div>
            <p className="text-xs font-bold text-slateText-100 group-hover:text-brand-teal transition-colors">
              {label}
            </p>
            <p className="text-[11px] font-medium text-slateText-400 mt-1">
              Supports JPEG, PNG, WebP, TIFF (Max 25MB)
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
