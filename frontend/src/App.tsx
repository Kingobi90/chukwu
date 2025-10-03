import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import SmartStudy from './pages/SmartStudy'
import FocusMode from './pages/FocusMode'
import CampusUnderground from './pages/CampusUnderground'
import LiveSync from './pages/LiveSync'
import Accountability from './pages/Accountability'
import BrainDump from './pages/BrainDump'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/smart-study"
          element={
            <PrivateRoute>
              <SmartStudy />
            </PrivateRoute>
          }
        />
        <Route
          path="/focus-mode"
          element={
            <PrivateRoute>
              <FocusMode />
            </PrivateRoute>
          }
        />
        <Route
          path="/campus-underground"
          element={
            <PrivateRoute>
              <CampusUnderground />
            </PrivateRoute>
          }
        />
        <Route
          path="/live-sync"
          element={
            <PrivateRoute>
              <LiveSync />
            </PrivateRoute>
          }
        />
        <Route
          path="/accountability"
          element={
            <PrivateRoute>
              <Accountability />
            </PrivateRoute>
          }
        />
        <Route
          path="/brain-dump"
          element={
            <PrivateRoute>
              <BrainDump />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
