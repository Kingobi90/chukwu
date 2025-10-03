import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { focusAPI } from '@/lib/api'
import { ArrowLeft, Play, Pause, RotateCcw } from 'lucide-react'

const PRESETS = [
  { label: '25 min', minutes: 25 },
  { label: '50 min', minutes: 50 },
  { label: '15 min', minutes: 15 },
  { label: '5 min', minutes: 5 },
]

const SOUNDS = [
  { value: 'silence', label: 'Silence' },
  { value: 'white_noise', label: 'White Noise' },
  { value: 'rain', label: 'Rain' },
  { value: 'lofi', label: 'Lo-Fi' },
]

export default function FocusMode() {
  const [duration, setDuration] = useState(25)
  const [sound, setSound] = useState('silence')
  const [timeLeft, setTimeLeft] = useState(duration * 60)
  const [isRunning, setIsRunning] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data: stats } = useQuery({
    queryKey: ['focusStats'],
    queryFn: async () => {
      const response = await focusAPI.getStats()
      return response.data
    },
  })

  const startMutation = useMutation({
    mutationFn: () => focusAPI.startSession({ duration_minutes: duration, ambient_sound: sound }),
    onSuccess: (response) => {
      setSessionId(response.data.id)
      setIsRunning(true)
      setTimeLeft(duration * 60)
    },
  })

  const completeMutation = useMutation({
    mutationFn: ({ id, interrupted }: { id: string; interrupted: boolean }) =>
      focusAPI.completeSession(id, interrupted),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['focusStats'] })
      setIsRunning(false)
      setSessionId(null)
    },
  })

  useEffect(() => {
    let interval: NodeJS.Timeout

    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            // Session complete
            if (sessionId) {
              completeMutation.mutate({ id: sessionId, interrupted: false })
            }
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }

    return () => clearInterval(interval)
  }, [isRunning, timeLeft, sessionId])

  const handleStart = () => {
    startMutation.mutate()
  }

  const handleStop = () => {
    if (sessionId) {
      completeMutation.mutate({ id: sessionId, interrupted: true })
    }
    setIsRunning(false)
    setTimeLeft(duration * 60)
  }

  const handleReset = () => {
    setTimeLeft(duration * 60)
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const progress = ((duration * 60 - timeLeft) / (duration * 60)) * 100

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-orange-900 to-gray-900">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <Link to="/" className="inline-flex items-center text-orange-400 hover:text-orange-300 mb-8">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Timer */}
          <div className="lg:col-span-2">
            <div className="glass p-12 rounded-2xl">
              <h2 className="text-3xl font-bold text-white mb-8 text-center">Focus Mode</h2>

              {/* Circular Progress */}
              <div className="relative w-80 h-80 mx-auto mb-8">
                <svg className="transform -rotate-90 w-full h-full">
                  <circle
                    cx="160"
                    cy="160"
                    r="140"
                    stroke="currentColor"
                    strokeWidth="12"
                    fill="none"
                    className="text-gray-700"
                  />
                  <circle
                    cx="160"
                    cy="160"
                    r="140"
                    stroke="currentColor"
                    strokeWidth="12"
                    fill="none"
                    strokeDasharray={`${2 * Math.PI * 140}`}
                    strokeDashoffset={`${2 * Math.PI * 140 * (1 - progress / 100)}`}
                    className="text-orange-500 transition-all duration-1000"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-6xl font-bold text-white mb-2">
                      {formatTime(timeLeft)}
                    </div>
                    <div className="text-gray-400">{isRunning ? 'Focus Time' : 'Ready'}</div>
                  </div>
                </div>
              </div>

              {/* Controls */}
              <div className="flex items-center justify-center gap-4">
                {!isRunning ? (
                  <button
                    onClick={handleStart}
                    className="px-8 py-4 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white font-semibold rounded-lg transition-all flex items-center gap-2"
                  >
                    <Play className="w-5 h-5" />
                    Start Session
                  </button>
                ) : (
                  <>
                    <button
                      onClick={handleStop}
                      className="px-8 py-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-all flex items-center gap-2"
                    >
                      <Pause className="w-5 h-5" />
                      Stop
                    </button>
                    <button
                      onClick={handleReset}
                      className="px-6 py-4 glass hover:bg-gray-700 text-white rounded-lg transition-all"
                    >
                      <RotateCcw className="w-5 h-5" />
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Settings & Stats */}
          <div className="space-y-6">
            {/* Settings */}
            <div className="glass p-6 rounded-xl">
              <h3 className="text-xl font-semibold text-white mb-4">Settings</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Duration</label>
                  <div className="grid grid-cols-2 gap-2">
                    {PRESETS.map((preset) => (
                      <button
                        key={preset.minutes}
                        onClick={() => {
                          setDuration(preset.minutes)
                          setTimeLeft(preset.minutes * 60)
                        }}
                        disabled={isRunning}
                        className={`py-2 rounded-lg transition-colors ${
                          duration === preset.minutes
                            ? 'bg-orange-600 text-white'
                            : 'glass text-gray-300 hover:bg-gray-700'
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        {preset.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-2">Ambient Sound</label>
                  <select
                    value={sound}
                    onChange={(e) => setSound(e.target.value)}
                    disabled={isRunning}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  >
                    {SOUNDS.map((s) => (
                      <option key={s.value} value={s.value}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="glass p-6 rounded-xl">
              <h3 className="text-xl font-semibold text-white mb-4">Statistics</h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Today</span>
                  <span className="text-white font-semibold">
                    {stats?.sessions_today || 0} sessions
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Minutes</span>
                  <span className="text-white font-semibold">
                    {stats?.minutes_today || 0}m
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Sessions</span>
                  <span className="text-white font-semibold">
                    {stats?.total_sessions || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Time</span>
                  <span className="text-white font-semibold">
                    {Math.floor((stats?.total_minutes || 0) / 60)}h {(stats?.total_minutes || 0) % 60}m
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
