import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

export default function Accountability() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-red-900 to-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Link to="/" className="inline-flex items-center text-red-400 hover:text-red-300 mb-8">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Link>

        <h1 className="text-4xl font-bold text-white mb-8">Accountability Circle</h1>
        
        <div className="glass p-8 rounded-xl text-center">
          <p className="text-gray-400 text-lg">
            Leaderboards and achievements coming soon...
          </p>
        </div>
      </div>
    </div>
  )
}
