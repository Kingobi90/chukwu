import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

export default function Login() {
  const [moodleToken, setMoodleToken] = useState('')
  const { login, isLoading, error } = useAuth()
  const navigate = useNavigate()
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  // Redirect if already authenticated
  if (isAuthenticated) {
    navigate('/')
    return null
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    login(moodleToken)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      <div className="w-full max-w-md p-8 space-y-6 glass rounded-2xl shadow-2xl animate-fade-in">
        <div className="text-center">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            StudyMaster
          </h1>
          <p className="mt-2 text-gray-400">AI-Enhanced Learning Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="token" className="block text-sm font-medium text-gray-300 mb-2">
              Moodle API Token
            </label>
            <input
              id="token"
              type="password"
              value={moodleToken}
              onChange={(e) => setMoodleToken(e.target.value)}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white placeholder-gray-500"
              placeholder="Enter your Moodle API token"
              required
            />
            <p className="mt-2 text-xs text-gray-500">
              Get your token from Moodle → Profile → Security Keys
            </p>
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-lg">
              <p className="text-sm text-red-400">
                {error instanceof Error ? error.message : 'Login failed. Please check your token.'}
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || !moodleToken}
            className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-semibold rounded-lg transition-all duration-200 transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="pt-4 border-t border-gray-700">
          <p className="text-xs text-center text-gray-500">
            By logging in, you agree to sync your Moodle data with StudyMaster
          </p>
        </div>
      </div>
    </div>
  )
}
