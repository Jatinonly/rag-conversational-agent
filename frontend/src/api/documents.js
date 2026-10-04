import { apiClient } from './client'

/**
 * Fetch list of all uploaded documents.
 * Backend route: GET /documents
 * Returns: { documents: [ { document_id: string, filename: string }, ... ] }
 */
export async function getDocuments() {
  const data = await apiClient('/documents', { method: 'GET' })
  return data?.documents || []
}

/**
 * Upload a PDF document.
 * Backend route: POST /documents/upload
 * Accepts multipart/form-data with file field
 * Returns: { filename: string, document_id: string, chunks: number, total_chunks: number }
 */
export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)

  return apiClient('/documents/upload', {
    method: 'POST',
    body: formData,
  })
}

/**
 * Delete a document by ID.
 * Backend route: DELETE /documents/{document_id}
 * Returns: { message: string, document_id: string }
 */
export async function deleteDocument(documentId) {
  return apiClient(`/documents/${documentId}`, {
    method: 'DELETE',
  })
}

