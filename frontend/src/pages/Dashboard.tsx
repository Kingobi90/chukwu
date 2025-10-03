import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { coursesAPI, flashcardsAPI, focusAPI } from '@/lib/api'
import { useAuth } from '@/hooks/useAuth'
import { 
  BookOpen, 
  Brain, 
  Timer, 
  Users, 
  Zap, 
  StickyNote,
  LogOut,
  TrendingUp
} from 'lucide-react'

export default function Dashboard() {
  const { user, logout } = useAuth()

  const { data: courses } = useQuery({
    queryKey: ['courses'],
    queryFn: async () => {
      const response = await coursesAPI.getCourses()
      return response.data
    },
  })

  const { data: dueFlashcards } = useQuery({
    queryKey: ['dueFlashcards'],
    queryFn: async () => {
      const response = await flashcardsAPI.getDueFlashcards()
      return response.data
    },
  })

  const { data: focusStats } = useQuery({
    queryKey: ['focusStats'],
    queryFn: async () => {
      const response = await focusAPI.getStats()
      return response.data
    },
  })

  const features = [
    {
      name: 'Smart Study',
      description: 'AI-powered flashcards & spaced repetition',
      icon: Brain,
      color: 'from-teal-500 to-cyan-500',
      link: '/smart-study',
      stat: `${dueFlashcards?.length || 0} cards due`,
    },
    {
      name: 'Focus Mode',
      description: 'Pomodoro timer with ambient sounds',
      icon: Timer,
      color: 'from-orange-500 to-red-500',
      link: '/focus-mode',
      stat: `${focusStats?.sessions_today || 0} sessions today`,
    },
    {
      name: 'Campus Underground',
      description: 'Study groups & peer collaboration',
      icon: Users,
      color: 'from-green-500 to-emerald-500',
      link: '/campus-underground',
      stat: 'Connect with peers',
    },
    {
      name: 'Live Class Sync',
      description: 'Real-time Moodle integration',
      icon: BookOpen,
      color: 'from-blue-500 to-indigo-500',
      link: '/live-sync',
      stat: `${courses?.length || 0} courses`,
    },
    {
      name: 'Accountability',
      description: 'Leaderboards & achievements',
      icon: TrendingUp,
      color: 'from-red-500 to-pink-500',
      link: '/accountability',
      stat: `${user?.points || 0} points`,
    },
    {
      name: 'Brain Dump',
      description: 'Quick notes & voice memos',
      icon: StickyNote,
      color: 'from-purple-500 to-violet-500',
      link: '/brain-dump',
      stat: 'Capture ideas',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      {/* Header */}
      <header className="glass border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                StudyMaster
              </h1>
              <p className="text-sm text-gray-400 mt-1">Welcome back, {user?.username}!</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-gray-400">Current Streak</p>
                <p className="text-xl font-bold text-orange-400">
                  {user?.streak_days || 0} days 🔥
                </p>
              </div>
              <button
                onClick={() => logout()}
                className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
                title="Logout"
              >
                <LogOut className="w-5 h-5 text-gray-400" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="glass p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Total Points</p>
                <p className="text-3xl font-bold text-purple-400">{user?.points || 0}</p>
              </div>
              <Zap className="w-12 h-12 text-purple-400 opacity-50" />
            </div>
          </div>
          
          <div className="glass p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Focus Time Today</p>
                <p className="text-3xl font-bold text-orange-400">
                  {focusStats?.minutes_today || 0}m
                </p>
              </div>
              <Timer className="w-12 h-12 text-orange-400 opacity-50" />
            </div>
          </div>
          
          <div className="glass p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Cards Due</p>
                <p className="text-3xl font-bold text-teal-400">
                  {dueFlashcards?.length || 0}
                </p>
              </div>
              <Brain className="w-12 h-12 text-teal-400 opacity-50" />
            </div>
          </div>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => {
            const Icon = feature.icon
            return (
              <Link
                key={feature.name}
                to={feature.link}
                className="glass p-6 rounded-xl hover:scale-105 transition-transform duration-200 group"
              >
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-purple-400 transition-colors">
                  {feature.name}
                </h3>
                <p className="text-sm text-gray-400 mb-3">{feature.description}</p>
                <p className="text-xs text-purple-400 font-medium">{feature.stat}</p>
              </Link>
            )
          })}
        </div>
      </main>
    </div>
  )
}
