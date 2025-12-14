import React, { useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import './WhatIf.css'

function WhatIf() {
  const [scenario, setScenario] = useState({
    year: 2025,
    week: 15,
    team1: '',
    team2: '',
    newWinner: ''
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await axios.post(`${API_BASE}/what-if`, { scenario })
      if (response.data.success) {
        setResult(response.data.data)
      }
    } catch (error) {
      console.error('Error calculating what-if:', error)
      setResult({ error: 'Failed to calculate scenario' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="what-if-container">
      <div className="what-if-header">
        <h2>🔮 What-If Machine</h2>
        <p>Calculate how different outcomes would affect playoff scenarios</p>
      </div>

      <div className="what-if-content">
        <div className="what-if-form-card">
          <h3>Create Scenario</h3>
          <form onSubmit={handleSubmit} className="what-if-form">
            <div className="form-group">
              <label>Year</label>
              <input
                type="number"
                value={scenario.year}
                onChange={(e) => setScenario({ ...scenario, year: parseInt(e.target.value) })}
                min="2012"
                max="2025"
              />
            </div>
            <div className="form-group">
              <label>Week</label>
              <input
                type="number"
                value={scenario.week}
                onChange={(e) => setScenario({ ...scenario, week: parseInt(e.target.value) })}
                min="1"
                max="17"
              />
            </div>
            <div className="form-group">
              <label>Team 1</label>
              <input
                type="text"
                value={scenario.team1}
                onChange={(e) => setScenario({ ...scenario, team1: e.target.value })}
                placeholder="Enter team name"
              />
            </div>
            <div className="form-group">
              <label>Team 2</label>
              <input
                type="text"
                value={scenario.team2}
                onChange={(e) => setScenario({ ...scenario, team2: e.target.value })}
                placeholder="Enter team name"
              />
            </div>
            <div className="form-group">
              <label>New Winner</label>
              <input
                type="text"
                value={scenario.newWinner}
                onChange={(e) => setScenario({ ...scenario, newWinner: e.target.value })}
                placeholder="Enter winning team name"
              />
            </div>
            <button type="submit" className="calculate-btn" disabled={loading}>
              {loading ? 'Calculating...' : 'Calculate Scenario'}
            </button>
          </form>
        </div>

        {result && (
          <div className="what-if-result">
            <h3>Result</h3>
            {result.message ? (
              <div className="result-message">
                <p>{result.message}</p>
                {result.scenario && (
                  <div className="scenario-summary">
                    <p><strong>Scenario:</strong> {result.scenario.year} Week {result.scenario.week}</p>
                    <p>{result.scenario.team1} vs {result.scenario.team2}</p>
                    <p>New Winner: {result.scenario.newWinner}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="result-error">
                <p>{result.error || 'Unable to calculate scenario'}</p>
              </div>
            )}
          </div>
        )}

        <div className="what-if-info">
          <h3>How It Works</h3>
          <p>This feature allows you to simulate different game outcomes and see how they would affect playoff scenarios.</p>
          <p><strong>Coming Soon:</strong> Full playoff probability calculations and detailed impact analysis.</p>
        </div>
      </div>
    </div>
  )
}

export default WhatIf

