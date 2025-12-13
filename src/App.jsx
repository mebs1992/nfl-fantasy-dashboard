import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Standings from './components/Standings'
import PlayoffTracker from './components/PlayoffTracker'
import HeadToHead from './components/HeadToHead'
import Almanac from './components/Almanac'
import HallOfFame from './components/HallOfFame'
import HallOfShame from './components/HallOfShame'
import { API_BASE } from './config'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('standings')
  const [leagueInfo, setLeagueInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState(null)

  useEffect(() => {
    fetchLeagueInfo()
    // Refresh data every 5 minutes
    const interval = setInterval(fetchLeagueInfo, 300000)
    return () => clearInterval(interval)
  }, [])

  const fetchLeagueInfo = async () => {
    try {
      const response = await axios.get(`${API_BASE}/league-info`)
      setLeagueInfo(response.data.data)
      setLastUpdate(response.data.data.last_updated)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching league info:', error)
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setLoading(true)
    try {
      await axios.post(`${API_BASE}/refresh`)
      await fetchLeagueInfo()
    } catch (error) {
      console.error('Error refreshing data:', error)
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'standings', label: 'Standings' },
    { id: 'playoff-tracker', label: 'Playoff Tracker' },
    { id: 'almanac', label: 'The Almanac' },
    { id: 'head-to-head', label: 'Head-to-Head' },
    { id: 'hall-of-fame', label: 'Hall of Fame' },
    { id: 'hall-of-shame', label: 'Hall of Shame' }
  ]

  if (loading && !leagueInfo) {
    return (
      <div className="app-loading">
        <div className="spinner"></div>
        <p>Loading league data...</p>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🏈 The Greatest League</h1>
          <div className="header-actions">
            {lastUpdate && (
              <span className="last-update">
                Updated: {new Date(lastUpdate).toLocaleString()}
              </span>
            )}
            <button onClick={handleRefresh} className="refresh-btn" disabled={loading}>
              {loading ? 'Refreshing...' : '🔄 Refresh Data'}
            </button>
          </div>
        </div>
      </header>

      <nav className="app-nav">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main className="app-main">
        {activeTab === 'standings' && <Standings />}
        {activeTab === 'playoff-tracker' && <PlayoffTracker />}
        {activeTab === 'almanac' && <Almanac />}
        {activeTab === 'head-to-head' && <HeadToHead />}
        {activeTab === 'hall-of-fame' && <HallOfFame />}
        {activeTab === 'hall-of-shame' && <HallOfShame />}
      </main>
    </div>
  )
}

export default App

