import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'

export function useAuth() {
  const navigate = useNavigate()
  const { setAuth, clearAuth } = useAuthStore()

  const loginMutation = useMutation({
    mutationFn: (moodleToken: string) => authAPI.login(moodleToken),
    onSuccess: async (response) => {
      const { access_token, refresh_token } = response.data
      
      // Save tokens to localStorage FIRST so the interceptor can use them
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      
      // Get user info (now the token will be included)
      const userResponse = await authAPI.getCurrentUser()
      setAuth(userResponse.data, access_token, refresh_token)
      
      navigate('/')
    },
  })

  const logoutMutation = useMutation({
    mutationFn: () => authAPI.logout(),
    onSuccess: () => {
      clearAuth()
      navigate('/login')
    },
  })

  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const response = await authAPI.getCurrentUser()
      return response.data
    },
    enabled: useAuthStore.getState().isAuthenticated,
  })

  return {
    login: loginMutation.mutate,
    logout: logoutMutation.mutate,
    user,
    isLoading: loginMutation.isPending,
    error: loginMutation.error,
  }
}
