import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { API_BASE } from '../config'
import './StreaksTrends.css'
import './EnterpriseTables.css'

const VIEW_OPTIONS = [
  { id: 'current-streaks', label: '🔥 Current Streaks' },
  { id: 'all-time-streaks', label: '📊 All-Time Streaks' },
  { id: 'points-trends', label: '📈 Points Trends' },
  { id: 'consistency', label: '🎯 Consistency Score' },
  { id: 'playoff-probability', label: '🏆 Playoff Probability' }
]

function StreaksTrends() {
  const [currentStreaks, setCurrentStreaks] = useState([])
  const [allTimeStreaks, setAllTimeStreaks] = useState([])
  const [pointsTrends, setPointsTrends] = useState([])
  const [consistency, setConsistency] = useState([])
  const [selectedView, setSelectedView] = useState('current-streaks')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAllData()
  }, [])

  const fetchAllData = async () => {
    setLoading(true)
    try {
      await Promise.all([
        fetchStreaks(),
        fetchPointsTrends(),
        fetchConsistency()
      ])
    } finally {
      setLoading(false)
    }
  }

  const fetchStreaks = async () => {
    try {
      const response = await axios.get(`${API_BASE}/streaks`)
      if (response.data.success) {
        setCurrentStreaks(response.data.data.current || [])
        setAllTimeStreaks(response.data.data.all_time || [])
      }
    } catch (error) {
      console.error('Error fetching streaks:', error)
    }
  }

  const fetchPointsTrends = async () => {
    try {
      const response = await axios.get(`${API_BASE}/points-trends`)
      if (response.data.success) {
        setPointsTrends(response.data.data || [])
      }
    } catch (error) {
      console.error('Error fetching points trends:', error)
    }
  }

  const fetchConsistency = async () => {
    try {
      const response = await axios.get(`${API_BASE}/consistency`)
      if (response.data.success) {
        setConsistency(response.data.data || [])
      }
    } catch (error) {
      console.error('Error fetching consistency:', error)
    }
  }

  const renderCurrentStreaks = () => {
    if (currentStreaks.length === 0) {
      return <div className="no-data">No current streaks data available</div>
    }

    return (
      <div className="streaks-table-container">
        <table className="data-table">
          <colgroup>
            <col className="col-rank" />
            <col className="col-team" />
            <col className="col-num" />
            <col className="col-num" />
          </colgroup>
          <thead>
            <tr>
              <th className="rank-header">Rank</th>
              <th className="team-header">Team</th>
              <th className="num-header">Streak</th>
              <th className="num-header">Type</th>
            </tr>
          </thead>
          <tbody>
            {currentStreaks.map((streak, index) => (
              <tr key={index}>
                <td className="rank-data">{index + 1}</td>
                <td className="team-data">
                  <img src={streak.logo} alt={streak.team} className="team-logo-small" />
                  {streak.team}
                </td>
                <td className="num-data num-bold">{streak.streak}</td>
                <td className="num-data">
                  <span className={`streak-type ${streak.type}`}>
                    {streak.type === 'win' ? '🔥 Win' : '❄️ Loss'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  const renderAllTimeStreaks = () => {
    if (allTimeStreaks.length === 0) {
      return <div className="no-data">No all-time streaks data available</div>
    }

    return (
      <div className="streaks-table-container">
        <table className="data-table">
          <colgroup>
            <col className="col-rank" />
            <col className="col-team" />
            <col className="col-num" />
            <col className="col-num" />
          </colgroup>
          <thead>
            <tr>
              <th className="rank-header">Rank</th>
              <th className="team-header">Team</th>
              <th className="num-header">Streak</th>
              <th className="num-header">Type</th>
            </tr>
          </thead>
          <tbody>
            {allTimeStreaks.map((streak, index) => (
              <tr key={index}>
                <td className="rank-data">{index + 1}</td>
                <td className="team-data">
                  <img src={streak.logo} alt={streak.team} className="team-logo-small" />
                  {streak.team}
                </td>
                <td className="num-data num-bold">{streak.streak}</td>
                <td className="num-data">
                  <span className={`streak-type ${streak.type}`}>
                    {streak.type === 'win' ? '🔥 Win' : '❄️ Loss'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  const renderPointsTrends = () => {
    if (pointsTrends.length === 0) {
      return <div className="no-data">No points trends data available</div>
    }

    // Prepare data for chart
    const chartData = {}
    pointsTrends.forEach(team => {
      team.yearly_averages?.forEach(yearData => {
        if (!chartData[yearData.year]) {
          chartData[yearData.year] = {}
        }
        chartData[yearData.year][team.team] = yearData.avg_score
      })
    })

    const years = Object.keys(chartData).sort().map(Number)
    const chartDataArray = years.map(year => {
      const data = { year }
      pointsTrends.forEach(team => {
        const yearData = team.yearly_averages?.find(y => y.year === year)
        if (yearData) {
          data[team.team] = yearData.avg_score
        }
      })
      return data
    })

    // Limit to top 8 teams by overall average for readability
    const topTeams = [...pointsTrends]
      .sort((a, b) => b.overall_avg - a.overall_avg)
      .slice(0, 8)

    return (
      <div className="trends-container">
        <div className="trends-chart">
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartDataArray}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="year" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip />
              <Legend />
              {topTeams.map((team, index) => (
                <Line
                  key={team.team}
                  type="monotone"
                  dataKey={team.team}
                  stroke={TEAM_LINE_COLORS[index % TEAM_LINE_COLORS.length]}
                  strokeWidth={2}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="trends-summary">
          {pointsTrends.map(team => (
            <div key={team.team} className="trend-card">
              <img src={team.logo} alt={team.team} className="trend-logo" />
              <div className="trend-info">
                <div className="trend-team">{team.team}</div>
                <div className="trend-stats">
                  <span>Current: {team.current_avg} pts</span>
                  <span>Overall: {team.overall_avg} pts</span>
                  <span className={`trend-direction ${team.trend}`}>
                    {team.trend === 'improving' ? '📈' : team.trend === 'declining' ? '📉' : '➡️'} {team.trend}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const renderConsistency = () => {
    if (consistency.length === 0) {
      return <div className="no-data">No consistency data available</div>
    }

    return (
      <div className="consistency-container">
        <div className="consistency-table-container">
          <table className="data-table">
            <colgroup>
              <col className="col-rank" />
              <col className="col-team" />
              <col className="col-num" />
              <col className="col-num" />
              <col className="col-num" />
              <col className="col-num" />
            </colgroup>
            <thead>
              <tr>
                <th className="rank-header">Rank</th>
                <th className="team-header">Team</th>
                <th className="num-header">Avg Score</th>
                <th className="num-header">Std Dev</th>
                <th className="num-header">CV %</th>
                <th className="num-header">Range</th>
              </tr>
            </thead>
            <tbody>
              {consistency.map((team, index) => (
                <tr key={index}>
                  <td className="rank-data">{index + 1}</td>
                  <td className="team-data">
                    <img src={team.logo} alt={team.team} className="team-logo-small" />
                    {team.team}
                  </td>
                  <td className="num-data">{team.avg_score}</td>
                  <td className="num-data">{team.std_dev}</td>
                  <td className="num-data">{team.coefficient_of_variation}%</td>
                  <td className="num-data">{team.range.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="consistency-explanation">
          <p><strong>Consistency Score:</strong> Lower Coefficient of Variation (CV) = More Consistent</p>
          <p>Teams with lower CV are "Steady Eddie" - reliable week-to-week. Teams with higher CV are "Boom or Bust" - unpredictable.</p>
        </div>
      </div>
    )
  }

  const renderPlayoffProbability = () => {
    return (
      <div className="playoff-prob-container">
        <p>Week-by-week playoff probability tracking requires additional data collection.</p>
        <p>This feature will show how each team's playoff chances changed throughout the season.</p>
      </div>
    )
  }

  const TEAM_LINE_COLORS = [
    '#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe',
    '#FFD700', '#C0C0C0', '#CD7F32', '#10b981', '#ef4444'
  ]

  if (loading) {
    return <div className="streaks-loading">Loading streaks and trends...</div>
  }

  return (
    <div className="streaks-trends-container">
      <div className="streaks-header">
        <h2>📊 Streaks & Trends</h2>
        <p>Track winning streaks, points trends, and consistency metrics</p>
      </div>

      <div className="streaks-content">
        <div className="streaks-sidebar">
          <select
            value={selectedView}
            onChange={(e) => setSelectedView(e.target.value)}
            className="view-selector"
          >
            {VIEW_OPTIONS.map(option => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="streaks-main">
          {selectedView === 'current-streaks' && renderCurrentStreaks()}
          {selectedView === 'all-time-streaks' && renderAllTimeStreaks()}
          {selectedView === 'points-trends' && renderPointsTrends()}
          {selectedView === 'consistency' && renderConsistency()}
          {selectedView === 'playoff-probability' && renderPlayoffProbability()}
        </div>
      </div>
    </div>
  )
}

export default StreaksTrends

