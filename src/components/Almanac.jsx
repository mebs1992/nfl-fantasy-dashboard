import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { getTeamImageUrl, getTeamColors } from '../utils/teamImages'
import { API_BASE } from '../config'
import './Almanac.css'

// Enterprise-grade color scheme
const CHART_COLORS = {
  pointsFor: '#667eea',
  winPct: '#10b981',
  pointsAgainst: '#ef4444'
}

// Team colors for line chart
const TEAM_LINE_COLORS = [
  '#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe',
  '#FFD700', '#C0C0C0', '#CD7F32', '#10b981', '#ef4444',
  '#f59e0b', '#8b5cf6'
]

const VIEW_OPTIONS = [
  { id: 'championships', label: '🏆 Championships' },
  { id: 'scoring-titles', label: '🔥 Scoring Titles' },
  { id: 'spoons', label: '🥄 Spoons' },
  { id: 'playoffs', label: '🎯 Playoff Appearances' },
  { id: 'points-for', label: '📊 All-Time Points For' },
  { id: 'points-against', label: '📉 All-Time Points Against' },
  { id: 'win-pct', label: '📈 Win % Trend' }
]

function Almanac() {
  const [allTimeStats, setAllTimeStats] = useState(null)
  const [historicalStats, setHistoricalStats] = useState(null)
  const [scoringTitles, setScoringTitles] = useState(null)
  const [winPctByYear, setWinPctByYear] = useState(null)
  const [selectedView, setSelectedView] = useState('championships')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAllTimeStats()
    fetchHistoricalStats()
    fetchScoringTitles()
    fetchWinPctByYear()
  }, [])

  const fetchAllTimeStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/team-stats-all-time`)
      if (response.data.success) {
        setAllTimeStats(response.data.data)
      }
    } catch (err) {
      console.error('Error fetching all-time stats:', err)
    }
  }

  const fetchHistoricalStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/historical-stats`)
      if (response.data.success) {
        setHistoricalStats(response.data.data)
      }
    } catch (err) {
      console.error('Error fetching historical stats:', err)
    }
  }

  const fetchScoringTitles = async () => {
    try {
      const response = await axios.get(`${API_BASE}/scoring-titles`)
      if (response.data.success) {
        setScoringTitles(response.data.data)
      }
    } catch (err) {
      console.error('Error fetching scoring titles:', err)
    }
  }

  const fetchWinPctByYear = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/win-pct-by-year`)
      if (response.data.success) {
        setWinPctByYear(response.data.data)
      }
    } catch (err) {
      console.error('Error fetching win pct by year:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading all-time statistics...</div>
  if (error) return <div className="error">Error: {error}</div>

  // Prepare historical achievement data
  const superBowlData = historicalStats ? Object.entries(historicalStats.super_bowls || {})
    .map(([team, data]) => ({ 
      team, 
      count: typeof data === 'number' ? data : data.count,
      years: typeof data === 'number' ? [] : (data.years || []),
      logo: typeof data === 'object' ? (data.logo || '') : ''
    }))
    .sort((a, b) => b.count - a.count) : []

  const playoffData = historicalStats ? Object.entries(historicalStats.playoffs || {})
    .map(([team, data]) => ({ 
      team, 
      count: typeof data === 'number' ? data : data.count,
      years: typeof data === 'number' ? [] : (data.years || []),
      logo: typeof data === 'object' ? (data.logo || '') : ''
    }))
    .sort((a, b) => b.count - a.count) : []

  const spoonData = historicalStats ? Object.entries(historicalStats.spoons || {})
    .map(([team, data]) => ({ 
      team, 
      count: typeof data === 'number' ? data : data.count,
      years: typeof data === 'number' ? [] : (data.years || []),
      logo: typeof data === 'object' ? (data.logo || '') : ''
    }))
    .sort((a, b) => b.count - a.count) : []

  const renderContent = () => {
    switch (selectedView) {
      case 'championships':
        return (
          <>
            <div className="card championships-card">
              <h2>🏆 Super Bowl Champions</h2>
              <p className="section-description">League champions by year (2017-2024)</p>
              <div className="championships-grid">
                {superBowlData.map((item, index) => (
                  <div key={item.team} className="championship-item">
                    <div className="championship-rank">#{index + 1}</div>
                    <img 
                      src={getTeamImageUrl(item.team, item.logo)} 
                      alt={item.team}
                      className="championship-avatar"
                      onError={(e) => {
                        e.target.src = getTeamImageUrl(item.team)
                      }}
                    />
                    <div className="championship-content">
                      <div className="championship-team">{item.team}</div>
                      <div className="championship-count">{item.count} {item.count === 1 ? 'Championship' : 'Championships'}</div>
                      {item.years && item.years.length > 0 && (
                        <div className="championship-years">{item.years.join(', ')}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {superBowlData.length > 0 && (
              <div className="card">
                <h2>Super Bowl Wins Chart</h2>
                <p className="section-description">Visual breakdown of championships by team</p>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={superBowlData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis 
                        dataKey="team" 
                        angle={-45} 
                        textAnchor="end" 
                        height={120}
                        tick={{ fill: '#6b7280', fontSize: 11, fontWeight: 500 }}
                        axisLine={{ stroke: '#e5e7eb' }}
                      />
                      <YAxis 
                        tick={{ fill: '#6b7280', fontSize: 11, fontWeight: 500 }}
                        axisLine={{ stroke: '#e5e7eb' }}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#fff', 
                          border: '1px solid #e5e7eb', 
                          borderRadius: '8px',
                          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                          padding: '12px'
                        }}
                        labelStyle={{ color: '#374151', fontWeight: 600, marginBottom: '4px' }}
                      />
                      <Legend />
                      <Bar dataKey="count" name="Super Bowl Wins" radius={[8, 8, 0, 0]}>
                        {superBowlData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={TEAM_LINE_COLORS[index % TEAM_LINE_COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </>
        )

      case 'scoring-titles':
        return (
          <div className="card championships-card">
            <h2>🔥 Scoring Titles</h2>
            <p className="section-description">Teams with the highest points scored in each season (2017-2024)</p>
            <div className="championships-grid">
              {scoringTitles && scoringTitles.map((item, index) => (
                <div key={item.team} className="championship-item scoring-title-item">
                  <div className="championship-rank">#{index + 1}</div>
                  <img 
                    src={getTeamImageUrl(item.team, item.logo)} 
                    alt={item.team}
                    className="championship-avatar"
                    onError={(e) => {
                      e.target.src = getTeamImageUrl(item.team)
                    }}
                  />
                  <div className="championship-content">
                    <div className="championship-team">{item.team}</div>
                    <div className="championship-count">{item.count} {item.count === 1 ? 'Title' : 'Titles'}</div>
                    {item.years && item.years.length > 0 && (
                      <div className="championship-years">
                        {item.years.map((y, idx) => (
                          <span key={y.year}>
                            {y.year} ({y.points.toLocaleString(undefined, { maximumFractionDigits: 2 })} pts)
                            {idx < item.years.length - 1 && ', '}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )

      case 'spoons':
        return (
          <>
            <div className="card championships-card">
              <h2>🥄 Spoons (Last Place)</h2>
              <p className="section-description">Teams that finished in 12th place (2017-2024)</p>
              <div className="championships-grid">
                {spoonData.map((item, index) => (
                  <div key={item.team} className="championship-item spoon-item">
                    <div className="championship-rank">#{index + 1}</div>
                    <img 
                      src={getTeamImageUrl(item.team, item.logo)} 
                      alt={item.team}
                      className="championship-avatar"
                      onError={(e) => {
                        e.target.src = getTeamImageUrl(item.team)
                      }}
                    />
                    <div className="championship-content">
                      <div className="championship-team">{item.team}</div>
                      <div className="championship-count">{item.count} {item.count === 1 ? 'Spoon' : 'Spoons'}</div>
                      {item.years && item.years.length > 0 && (
                        <div className="championship-years">{item.years.join(', ')}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {spoonData.length > 0 && (
              <div className="card">
                <h2>Spoons Chart</h2>
                <p className="section-description">Visual breakdown of last place finishes by team</p>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={spoonData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis 
                        dataKey="team" 
                        angle={-45} 
                        textAnchor="end" 
                        height={120}
                        tick={{ fill: '#6b7280', fontSize: 11, fontWeight: 500 }}
                        axisLine={{ stroke: '#e5e7eb' }}
                      />
                      <YAxis 
                        tick={{ fill: '#6b7280', fontSize: 11, fontWeight: 500 }}
                        axisLine={{ stroke: '#e5e7eb' }}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#fff', 
                          border: '1px solid #e5e7eb', 
                          borderRadius: '8px',
                          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                          padding: '12px'
                        }}
                        labelStyle={{ color: '#374151', fontWeight: 600, marginBottom: '4px' }}
                      />
                      <Legend />
                      <Bar dataKey="count" name="Spoons" radius={[8, 8, 0, 0]}>
                        {spoonData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={TEAM_LINE_COLORS[index % TEAM_LINE_COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </>
        )

      case 'playoffs':
        return (
          <div className="card">
            <h2>🎯 Playoff Appearances</h2>
            <p className="section-description">Teams that finished in the top 4 (2017-2024)</p>
            <div className="achievements-grid">
              <div className="achievement-section">
                <div className="achievement-list">
                  {playoffData.map((item, index) => {
                    const teamColors = getTeamColors(item.team)
                    return (
                      <div key={item.team} className="achievement-item playoff" style={{ '--team-color': teamColors.primary }}>
                        <div className="achievement-rank">#{index + 1}</div>
                        <img src={getTeamImageUrl(item.team, item.logo)} alt={item.team} className="achievement-avatar" />
                        <div className="achievement-content">
                          <div className="achievement-team">{item.team}</div>
                          <div className="achievement-count">{item.count} {item.count === 1 ? 'Appearance' : 'Appearances'}</div>
                          {item.years && item.years.length > 0 && (
                            <div className="achievement-years">{item.years.join(', ')}</div>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          </div>
        )

      case 'points-for':
        return (
          <div className="card points-table-card">
            <h2>📊 All-Time Points For</h2>
            <p className="section-description">Total points scored across all completed seasons</p>
            <div className="almanac-table-wrapper">
              <table className="almanac-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Team</th>
                    <th>Total Points</th>
                    <th>Seasons</th>
                  </tr>
                </thead>
                <tbody>
                  {allTimeStats && allTimeStats.most_points_scored.map((item, index) => {
                    const teamColors = getTeamColors(item.team)
                    return (
                      <tr 
                        key={item.team}
                        className="almanac-table-row"
                        style={{ '--team-color': teamColors.primary }}
                      >
                        <td className="rank-cell">#{index + 1}</td>
                        <td className="team-cell">
                          <div className="team-info">
                            <img 
                              src={getTeamImageUrl(item.team, item.logo)} 
                              alt={item.team}
                              className="team-avatar-small"
                              onError={(e) => {
                                e.target.src = getTeamImageUrl(item.team)
                              }}
                            />
                            <span className="team-name">{item.team}</span>
                          </div>
                        </td>
                        <td className="points-cell points-for">{item.points.toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>
                        <td className="seasons-cell">{item.seasons}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )

      case 'points-against':
        return (
          <div className="card points-table-card">
            <h2>📉 All-Time Points Against</h2>
            <p className="section-description">Total points allowed across all completed seasons</p>
            <div className="almanac-table-wrapper">
              <table className="almanac-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Team</th>
                    <th>Total Points</th>
                    <th>Seasons</th>
                  </tr>
                </thead>
                <tbody>
                  {allTimeStats && allTimeStats.most_points_against.map((item, index) => {
                    const teamColors = getTeamColors(item.team)
                    return (
                      <tr 
                        key={item.team}
                        className="almanac-table-row"
                        style={{ '--team-color': teamColors.primary }}
                      >
                        <td className="rank-cell">#{index + 1}</td>
                        <td className="team-cell">
                          <div className="team-info">
                            <img 
                              src={getTeamImageUrl(item.team, item.logo)} 
                              alt={item.team}
                              className="team-avatar-small"
                              onError={(e) => {
                                e.target.src = getTeamImageUrl(item.team)
                              }}
                            />
                            <span className="team-name">{item.team}</span>
                          </div>
                        </td>
                        <td className="points-cell points-against">{item.points.toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>
                        <td className="seasons-cell">{item.seasons}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )

      case 'win-pct':
        return (
          <div className="card">
            <h2>📈 All-Time Win Percentage Trend</h2>
            <p className="section-description">Win percentage for top teams across seasons (2017-2024)</p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={500}>
                <LineChart 
                  data={winPctByYear}
                  margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="year"
                    tick={{ fill: '#6b7280', fontSize: 12, fontWeight: 500 }}
                    axisLine={{ stroke: '#e5e7eb' }}
                  />
                  <YAxis 
                    tick={{ fill: '#6b7280', fontSize: 12, fontWeight: 500 }}
                    tickFormatter={(value) => `${value.toFixed(0)}%`}
                    axisLine={{ stroke: '#e5e7eb' }}
                    label={{ value: 'Win %', angle: -90, position: 'insideLeft', fill: '#6b7280' }}
                  />
                  <Tooltip 
                    formatter={(value) => `${value.toFixed(2)}%`}
                    contentStyle={{ 
                      backgroundColor: '#fff', 
                      border: '1px solid #e5e7eb', 
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                      padding: '12px'
                    }}
                    labelStyle={{ color: '#374151', fontWeight: 600, marginBottom: '4px' }}
                  />
                  <Legend 
                    wrapperStyle={{ paddingTop: '20px' }}
                    iconType="line"
                  />
                  {allTimeStats && allTimeStats.highest_win_pct.slice(0, 8).map((team, index) => (
                    <Line
                      key={team.team}
                      type="monotone"
                      dataKey={team.team}
                      stroke={TEAM_LINE_COLORS[index % TEAM_LINE_COLORS.length]}
                      strokeWidth={2.5}
                      dot={{ r: 5 }}
                      activeDot={{ r: 7 }}
                      name={team.team}
                      connectNulls={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="almanac">
      <div className="almanac-header">
        <h1 className="almanac-title">The Almanac</h1>
        <p className="almanac-subtitle">All-Time League Statistics (2017-2024)</p>
      </div>

      <div className="almanac-layout">
        <div className="almanac-sidebar">
          <div className="sidebar-header">Select View</div>
          <div className="sidebar-menu">
            {VIEW_OPTIONS.map((option) => (
              <button
                key={option.id}
                className={`sidebar-menu-item ${selectedView === option.id ? 'active' : ''}`}
                onClick={() => setSelectedView(option.id)}
              >
                <span className="menu-label">{option.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="almanac-content">
          {renderContent()}
        </div>
      </div>
    </div>
  )
}

export default Almanac
