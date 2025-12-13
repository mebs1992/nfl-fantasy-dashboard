import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import './HallOfFame.css'

function HallOfFame() {
  const [inductees, setInductees] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchHallOfFame()
  }, [])

  const fetchHallOfFame = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/hall-of-fame`)
      if (response.data.success) {
        setInductees(response.data.data)
      }
    } catch (err) {
      setError(err.message)
      console.error('Error fetching Hall of Fame:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="hall-loading">
        <div className="spinner"></div>
        <p>Loading Hall of Fame...</p>
      </div>
    )
  }

  if (error) {
    return <div className="hall-error">Error: {error}</div>
  }

  return (
    <div className="hall-of-fame">
      <div className="hall-header">
        <h1 className="hall-title">🏆 Hall of Fame 🏆</h1>
        <p className="hall-subtitle">The Immortals of The Greatest League</p>
        <div className="hall-divider"></div>
      </div>

      <div className="hall-inductees">
        {inductees.map((inductee, index) => (
          <div key={inductee.team} className="hall-card">
            <div className="hall-card-glow"></div>
            <div className="hall-card-content">
              <div className="hall-card-header">
                <div className="hall-badge">
                  <span className="hall-badge-number">{index + 1}</span>
                </div>
                {inductee.logo && (
                  <img 
                    src={inductee.logo} 
                    alt={inductee.team}
                    className="hall-logo"
                  />
                )}
                <h2 className="hall-team-name">{inductee.team}</h2>
              </div>
              <div className="hall-blurb">
                <p>{inductee.blurb}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="hall-footer">
        <p className="hall-footer-text">
          "Excellence is not a destination, it's a journey. These legends have made the journey look effortless."
        </p>
      </div>
    </div>
  )
}

export default HallOfFame

