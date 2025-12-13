import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import './HallOfShame.css'

function HallOfShame() {
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchHallOfShame()
  }, [])

  const fetchHallOfShame = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/hall-of-shame`)
      if (response.data.success) {
        setTeams(response.data.data)
      }
    } catch (err) {
      setError(err.message)
      console.error('Error fetching Hall of Shame:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="shame-loading">
        <div className="spinner"></div>
        <p>Loading Hall of Shame...</p>
      </div>
    )
  }

  if (error) {
    return <div className="shame-error">Error: {error}</div>
  }

  return (
    <div className="hall-of-shame">
      <div className="shame-header">
        <h1 className="shame-title">💀 Hall of Shame 💀</h1>
        <p className="shame-subtitle">The Perpetually Trophy-Less</p>
        <div className="shame-divider"></div>
        <p className="shame-description">
          These teams have been in the league for 3+ years and have yet to hoist the championship trophy.
          They've tried. They've come close. They've... well, they've been here.
        </p>
      </div>

      <div className="shame-teams">
        {teams.length === 0 ? (
          <div className="shame-empty">
            <p>🎉 Congratulations! No teams qualify for the Hall of Shame!</p>
            <p>Everyone has won at least one championship. What a league!</p>
          </div>
        ) : (
          teams.map((team, index) => (
            <div key={team.team} className="shame-card">
              <div className="shame-card-content">
                <div className="shame-card-header">
                  {team.logo && (
                    <img 
                      src={team.logo} 
                      alt={team.team}
                      className="shame-logo"
                    />
                  )}
                  <div className="shame-team-info">
                    <h2 className="shame-team-name">{team.team}</h2>
                    <div className="shame-stats">
                      <span className="shame-stat">
                        <span className="shame-stat-label">Years Active:</span>
                        <span className="shame-stat-value">{team.years_active}</span>
                      </span>
                      <span className="shame-stat">
                        <span className="shame-stat-label">Years:</span>
                        <span className="shame-stat-value">{team.years_range}</span>
                      </span>
                    </div>
                  </div>
                  <div className="shame-badge">
                    <span className="shame-badge-text">0</span>
                    <span className="shame-badge-label">Rings</span>
                  </div>
                </div>
                <div className="shame-blurb">
                  <p>{team.blurb}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="shame-footer">
        <p className="shame-footer-text">
          "The road to glory is paved with... well, these teams are still paving."
        </p>
      </div>
    </div>
  )
}

export default HallOfShame

