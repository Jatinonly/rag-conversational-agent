const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Common request wrapper for API calls.
 * Centralizes URL management, headers, error handling and JSON parsing.
 */
export async function apiClient(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`

  const headers = {
    ...options.headers,
  }

  // Set Content-Type only if body is NOT FormData
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }

  let response
  try {
    response = await fetch(url, {
      ...options,
      headers,
    })
  } catch (err) {
    throw new Error('Unable to connect to the backend server. Please make sure it is running on port 8000.')
  }

  let data
  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    try {
      data = await response.json()
    } catch {
      data = null
    }
  } else {
    data = await response.text()
  }

  if (!response.ok) {
    const errorMsg = data?.detail || data?.error || data?.message || `Request failed with status ${response.status}`
    throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
  }

  // Backend sometimes returns 200 with { "error": "..." }
  if (data && typeof data === 'object' && data.error) {
    throw new Error(data.error)
  }

  return data
}

export default apiClient

