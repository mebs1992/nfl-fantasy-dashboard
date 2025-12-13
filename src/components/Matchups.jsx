import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './Matchups.css'

const API_BASE = 'http://localhost:5000/api'

function Matchups() {
  const [matchups, setMatchups] = useState([])
  const [selectedWeek, setSelectedWeek] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchMatchups()
  }, [selectedWeek])

  const fetchMatchups = async () => {
    try {
      const params = selectedWeek ? { week: selectedWeek } : {}
      const response = await axios.get(`${API_BASE}/matchups`, { params })
      if (response.data.success) {
        setMatchups(response.data.data)
      }
      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading matchups...</div>
  if (error) return <div className="error">Error: {error}</div>

  // Group matchups by week
  const matchupsByWeek = {}
  matchups.forEach(matchup => {
    const week = matchup.week || 'Unknown'
    if (!matchupsByWeek[week]) {
      matchupsByWeek[week] = []
    }
    matchupsByWeek[week].push(matchup)
  })

  const weeks = Object.keys(matchupsByWeek).sort((a, b) => {
    if (a === 'Unknown') return 1
    if (b === 'Unknown') return -1
    return parseInt(a) - parseInt(b)
  })

  return (
    <div>
      <div className="card">
        <h2>Weekly Matchups</h2>
        <div className="week-selector">
          <label>Filter by Week:</label>
          <select value={selectedWeek || ''} onChange={(e) => setSelectedWeek(e.target.value || null)}>
            <option value="">All Weeks</option>
            {weeks.map(week => (
              <option key={week} value={week}>Week {week}</option>
            ))}
          </select>
        </div>

        {weeks.length === 0 ? (
          <div className="no-data">No matchup data available. Data will appear as it's collected.</div>
        ) : (
          weeks.map(week => (
            <div key={week} className="week-section">
              <h3>Week {week}</h3>
              <div className="matchups-grid">
                {matchupsByWeek[week].map((matchup, index) => {
                  const team1 = matchup.team1_name || matchup.team1 || 'Team 1'
                  const team2 = matchup.team2_name || matchup.team2 || 'Team 2'
                  const score1 = matchup.team1_score || matchup.score1 || 0
                  const score2 = matchup.team2_score || matchup.score2 || 0
                  const winner = matchup.winner

                  return (
                    <div key={index} className="matchup-card">
                      <div className={`matchup-team ${winner === team1 ? 'winner' : ''}`}>
                        <div className="team-name">{team1}</div>
                        <div className="team-score">{score1.toFixed(2)}</div>
                      </div>
                      <div className="matchup-vs">vs</div>
                      <div className={`matchup-team ${winner === team2 ? 'winner' : ''}`}>
                        <div className="team-name">{team2}</div>
                        <div className="team-score">{score2.toFixed(2)}</div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default Matchups

