import { useState, useEffect, useCallback } from 'react'
import { getDocuments, uploadDocument, deleteDocument } from '../api/documents'

export function useDocuments() {
  const [documents, setDocuments] = useState([])
  const [selectedDocId, setSelectedDocId] = useState(null)
  const [isLoadingDocs, setIsLoadingDocs] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [error, setError] = useState(null)

  const loadDocuments = useCallback(async () => {
    setIsLoadingDocs(true)
    setError(null)
    try {
      const docs = await getDocuments()
      setDocuments(docs)
    } catch (err) {
      setError(err.message || 'Failed to fetch documents')
    } finally {
      setIsLoadingDocs(false)
    }
  }, [])

  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  const upload = async (file) => {
    if (!file) {
      setError('Please select a file to upload')
      return null
    }

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF documents are supported.')
      return null
    }

    setIsUploading(true)
    setError(null)
    setUploadResult(null)

    try {
      const res = await uploadDocument(file)
      // Refresh documents list
      await loadDocuments()
      setUploadResult(res)
      return res
    } catch (err) {
      setError(err.message || 'Failed to upload document')
      return null
    } finally {
      setIsUploading(false)
    }
  }

  const removeDoc = async (documentId) => {
    setError(null)
    try {
      await deleteDocument(documentId)
      setDocuments((prev) => prev.filter((d) => d.document_id !== documentId))
      if (selectedDocId === documentId) {
        setSelectedDocId(null)
      }
      return true
    } catch (err) {
      setError(err.message || 'Failed to delete document')
      return false
    }
  }

  const toggleSelectDocument = (docId) => {
    setSelectedDocId((prev) => (prev === docId ? null : docId))
  }

  return {
    documents,
    selectedDocId,
    setSelectedDocId,
    toggleSelectDocument,
    isLoadingDocs,
    isUploading,
    uploadResult,
    error,
    clearError: () => setError(null),
    clearUploadResult: () => setUploadResult(null),
    loadDocuments,
    upload,
    removeDoc,
  }
}

