import React, { useRef, useState } from 'react'
import { Upload, FileUp, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'
import { Button } from '../ui/button'

export function UploadDocument({ onUpload, isUploading, uploadResult, error, onClearResult }) {
  const fileInputRef = useRef(null)
  const [selectedFileName, setSelectedFileName] = useState('')

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setSelectedFileName(file.name)
    await onUpload(file)

    // Reset input so re-uploading the same file works if needed
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-2">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pdf,application/pdf"
        className="hidden"
        id="pdf-upload-input"
        disabled={isUploading}
      />

      <Button
        variant="outline"
        size="sm"
        className="w-full justify-center gap-2 border-dashed border-slate-300 hover:border-slate-400 bg-slate-50/50 hover:bg-slate-100 text-slate-700 py-2.5 h-auto text-xs font-medium"
        onClick={() => fileInputRef.current?.click()}
        disabled={isUploading}
      >
        {isUploading ? (
          <>
            <Loader2 className="h-3.5 w-3.5 animate-spin text-slate-600" />
            <span>Processing PDF & Chunks...</span>
          </>
        ) : (
          <>
            <Upload className="h-3.5 w-3.5 text-slate-600" />
            <span>Upload PDF Document</span>
          </>
        )}
      </Button>

      {/* Success feedback */}
      {uploadResult && (
        <div className="flex items-start gap-2 p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 animate-in fade-in">
          <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-medium truncate">{uploadResult.filename}</p>
            <p className="text-[11px] text-emerald-700">
              Extracted {uploadResult.chunks} chunks (Total: {uploadResult.total_chunks})
            </p>
          </div>
          {onClearResult && (
            <button
              onClick={onClearResult}
              className="text-emerald-600 hover:text-emerald-800 text-xs font-semibold px-1"
            >
              ×
            </button>
          )}
        </div>
      )}

      {/* Error feedback */}
      {error && (
        <div className="flex items-start gap-2 p-2.5 rounded-lg bg-red-50 border border-red-200 text-xs text-red-800 animate-in fade-in">
          <AlertCircle className="h-4 w-4 text-red-600 shrink-0 mt-0.5" />
          <p className="flex-1 leading-snug">{error}</p>
        </div>
      )}
    </div>
  )
}

