import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import './WeeklyRecap.css'

function WeeklyRecap() {
  const [year, setYear] = useState(2025)
  const [week, setWeek] = useState(15)
  const [recap, setRecap] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchRecap = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/weekly-recap`, {
        params: { year, week }
      })
      if (response.data.success) {
        setRecap(response.data.data)
      }
    } catch (error) {
      console.error('Error fetching weekly recap:', error)
      setRecap({ error: 'Failed to load recap' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRecap()
  }, [])

  const handleGenerate = () => {
    fetchRecap()
  }

  if (recap?.error) {
    return (
      <div className="weekly-recap-container">
        <div className="recap-error">
          <p>{recap.error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="weekly-recap-container">
      <div className="recap-header">
        <h2>📰 Weekly Recap</h2>
        <p>Automated summaries of the week's biggest moments</p>
      </div>

      <div className="recap-controls">
        <div className="control-group">
          <label>Year</label>
          <input
            type="number"
            value={year}
            onChange={(e) => setYear(parseInt(e.target.value))}
            min="2012"
            max="2025"
          />
        </div>
        <div className="control-group">
          <label>Week</label>
          <input
            type="number"
            value={week}
            onChange={(e) => setWeek(parseInt(e.target.value))}
            min="1"
            max="17"
          />
        </div>
        <button onClick={handleGenerate} className="generate-btn" disabled={loading}>
          {loading ? 'Loading...' : 'Generate Recap'}
        </button>
      </div>

      {recap && !recap.error && (
        <div className="recap-content">
          <div className="recap-summary">
            <h3>{recap.year} Week {recap.week} Recap</h3>
            <p className="recap-text">{recap.summary}</p>
          </div>

          {recap.highest_score && (
            <div className="recap-highlight">
              <div className="highlight-icon">🔥</div>
              <div className="highlight-content">
                <div className="highlight-title">Highest Score</div>
                <div className="highlight-details">
                  <strong>{recap.highest_score.team}</strong> scored {recap.highest_score.score.toFixed(1)} points
                  {recap.highest_score.opponent && (
                    <> against <strong>{recap.highest_score.opponent}</strong> ({recap.highest_score.opponent_score.toFixed(1)} pts)</>
                  )}
                </div>
              </div>
            </div>
          )}

          {recap.biggest_blowout && (
            <div className="recap-highlight">
              <div className="highlight-icon">💥</div>
              <div className="highlight-content">
                <div className="highlight-title">Biggest Blowout</div>
                <div className="highlight-details">
                  <strong>{recap.biggest_blowout.winner}</strong> defeated <strong>{recap.biggest_blowout.loser}</strong> by {recap.biggest_blowout.margin.toFixed(1)} points
                  ({recap.biggest_blowout.winner_score.toFixed(1)} - {recap.biggest_blowout.loser_score.toFixed(1)})
                </div>
              </div>
            </div>
          )}

          {recap.closest_game && (
            <div className="recap-highlight">
              <div className="highlight-icon">⚡</div>
              <div className="highlight-content">
                <div className="highlight-title">Closest Game</div>
                <div className="highlight-details">
                  <strong>{recap.closest_game.team1}</strong> ({recap.closest_game.score1.toFixed(1)}) vs <strong>{recap.closest_game.team2}</strong> ({recap.closest_game.score2.toFixed(1)})
                  <br />
                  Winner: <strong>{recap.closest_game.winner}</strong> by {recap.closest_game.margin.toFixed(1)} points
                </div>
              </div>
            </div>
          )}

          <div className="recap-stats">
            <div className="stat-card">
              <div className="stat-value">{recap.total_games}</div>
              <div className="stat-label">Total Games</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default WeeklyRecap

