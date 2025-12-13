import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import './TeamStats.css'

const API_BASE = 'http://localhost:5000/api'

function TeamStats() {
  const [teams, setTeams] = useState([])
  const [selectedTeam, setSelectedTeam] = useState('')
  const [teamStats, setTeamStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchTeams()
  }, [])

  useEffect(() => {
    if (selectedTeam) {
      fetchTeamStats()
    }
  }, [selectedTeam])

  const fetchTeams = async () => {
    try {
      const response = await axios.get(`${API_BASE}/standings`)
      if (response.data.success) {
        setTeams(response.data.data)
        if (response.data.data.length > 0) {
          setSelectedTeam(response.data.data[0].name)
        }
      }
      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const fetchTeamStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/team-stats`, {
        params: { team_name: selectedTeam }
      })
      if (response.data.success) {
        setTeamStats(response.data.data)
      }
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <div className="loading">Loading team stats...</div>
  if (error) return <div className="error">Error: {error}</div>

  const opponentChartData = teamStats?.opponent_records?.map(opp => ({
    opponent: opp.opponent,
    'Win %': opp.win_pct,
    wins: opp.wins,
    losses: opp.losses
  })) || []

  return (
    <div>
      <div className="card">
        <h2>Team Statistics</h2>
        <div className="team-selector">
          <label>Select Team:</label>
          <select value={selectedTeam} onChange={(e) => setSelectedTeam(e.target.value)}>
            {teams.map(team => (
              <option key={team.id || team.name} value={team.name}>{team.name}</option>
            ))}
          </select>
        </div>

        {teamStats && (
          <div className="team-stats-content">
            {teamStats.current && (
              <div className="current-stats">
                <h3>Current Season</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <div className="stat-label">Record</div>
                    <div className="stat-value">
                      {teamStats.current.wins}-{teamStats.current.losses}-{teamStats.current.ties || 0}
                    </div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-label">Points For</div>
                    <div className="stat-value">{teamStats.current.points_for?.toFixed(2) || '0.00'}</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-label">Win %</div>
                    <div className="stat-value">
                      {teamStats.current.wins + teamStats.current.losses + (teamStats.current.ties || 0) > 0
                        ? (((teamStats.current.wins + (teamStats.current.ties || 0) * 0.5) / 
                            (teamStats.current.wins + teamStats.current.losses + (teamStats.current.ties || 0))) * 100).toFixed(1)
                        : '0.0'}%
                    </div>
                  </div>
                </div>
              </div>
            )}

            {teamStats.historical && (
              <div className="historical-stats">
                <h3>All-Time Stats</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <div className="stat-label">Total Wins</div>
                    <div className="stat-value">{teamStats.historical.total_wins || 0}</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-label">Total Losses</div>
                    <div className="stat-value">{teamStats.historical.total_losses || 0}</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-label">Total Ties</div>
                    <div className="stat-value">{teamStats.historical.total_ties || 0}</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-label">Total Points</div>
                    <div className="stat-value">{teamStats.historical.total_points?.toFixed(2) || '0.00'}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {teamStats?.opponent_records && teamStats.opponent_records.length > 0 && (
        <div className="card">
          <h2>Win Percentage vs Opponents</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={opponentChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="opponent" angle={-45} textAnchor="end" height={100} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="Win %" fill="#667eea" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {teamStats?.opponent_records && teamStats.opponent_records.length > 0 && (
        <div className="card">
          <h2>Opponent Records</h2>
          <div className="opponent-table">
            <table>
              <thead>
                <tr>
                  <th>Opponent</th>
                  <th>Wins</th>
                  <th>Losses</th>
                  <th>Ties</th>
                  <th>Win %</th>
                </tr>
              </thead>
              <tbody>
                {teamStats.opponent_records.map((opp, index) => (
                  <tr key={index}>
                    <td className="team-name">{opp.opponent}</td>
                    <td>{opp.wins}</td>
                    <td>{opp.losses}</td>
                    <td>{opp.ties}</td>
                    <td className="win-pct">{opp.win_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default TeamStats

