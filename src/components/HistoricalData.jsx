import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import './HistoricalData.css'

const API_BASE = 'http://localhost:5000/api'

const COLORS = ['#FFD700', '#C0C0C0', '#CD7F32', '#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']

function HistoricalData() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchHistoricalStats()
  }, [])

  const fetchHistoricalStats = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/historical-stats`)
      if (response.data.success) {
        setStats(response.data.data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading historical data...</div>
  if (error) return <div className="error">Error: {error}</div>
  if (!stats) return <div className="no-data">No historical data available</div>

  // Prepare data for charts
  const superBowlData = Object.entries(stats.super_bowls || {})
    .map(([team, data]) => ({ 
      team, 
      count: typeof data === 'number' ? data : data.count,
      years: typeof data === 'number' ? [] : (data.years || [])
    }))
    .sort((a, b) => b.count - a.count)

  const playoffData = Object.entries(stats.playoffs || {})
    .map(([team, data]) => ({ 
      team, 
      count: typeof data === 'number' ? data : data.count,
      years: typeof data === 'number' ? [] : (data.years || [])
    }))
    .sort((a, b) => b.count - a.count)

  const spoonData = Object.entries(stats.spoons || {})
    .map(([team, data]) => ({ 
      team, 
      count: typeof data === 'number' ? data : data.count,
      years: typeof data === 'number' ? [] : (data.years || [])
    }))
    .sort((a, b) => b.count - a.count)

  return (
    <div>
      <div className="card">
        <h2>🏆 Super Bowl Wins</h2>
        <p className="section-description">Teams that finished in 1st place (League Champions)</p>
        
        {superBowlData.length > 0 ? (
          <>
            <div className="stats-list">
              {superBowlData.map((item, index) => (
                <div key={item.team} className="stat-item superbowl">
                  <div className="stat-rank">#{index + 1}</div>
                  <div className="stat-team-info">
                    <div className="stat-team">{item.team}</div>
                    {item.years && item.years.length > 0 && (
                      <div className="stat-years">{item.years.join(', ')}</div>
                    )}
                  </div>
                  <div className="stat-count">{item.count}</div>
                  <div className="stat-label">{item.count === 1 ? 'Win' : 'Wins'}</div>
                </div>
              ))}
            </div>
            
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={superBowlData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="team" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#FFD700" name="Super Bowl Wins">
                    {superBowlData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : (
          <div className="no-data">No Super Bowl data available</div>
        )}
      </div>

      <div className="card">
        <h2>🎯 Playoff Appearances</h2>
        <p className="section-description">Teams that finished in 1st-4th place (Playoff Teams)</p>
        
        {playoffData.length > 0 ? (
          <>
            <div className="stats-list">
              {playoffData.map((item, index) => (
                <div key={item.team} className="stat-item playoff">
                  <div className="stat-rank">#{index + 1}</div>
                  <div className="stat-team-info">
                    <div className="stat-team">{item.team}</div>
                    {item.years && item.years.length > 0 && (
                      <div className="stat-years">{item.years.join(', ')}</div>
                    )}
                  </div>
                  <div className="stat-count">{item.count}</div>
                  <div className="stat-label">{item.count === 1 ? 'Appearance' : 'Appearances'}</div>
                </div>
              ))}
            </div>
            
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={playoffData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="team" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#667eea" name="Playoff Appearances">
                    {playoffData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : (
          <div className="no-data">No playoff data available</div>
        )}
      </div>

      <div className="card">
        <h2>🥄 Spoons (Last Place)</h2>
        <p className="section-description">Teams that finished in 12th place (The Spoon)</p>
        
        {spoonData.length > 0 ? (
          <>
            <div className="stats-list">
              {spoonData.map((item, index) => (
                <div key={item.team} className="stat-item spoon">
                  <div className="stat-rank">#{index + 1}</div>
                  <div className="stat-team-info">
                    <div className="stat-team">{item.team}</div>
                    {item.years && item.years.length > 0 && (
                      <div className="stat-years">{item.years.join(', ')}</div>
                    )}
                  </div>
                  <div className="stat-count">{item.count}</div>
                  <div className="stat-label">{item.count === 1 ? 'Spoon' : 'Spoons'}</div>
                </div>
              ))}
            </div>
            
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={spoonData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="team" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#CD7F32" name="Spoons">
                    {spoonData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[(index + 4) % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : (
          <div className="no-data">No spoon data available</div>
        )}
      </div>
    </div>
  )
}

export default HistoricalData

