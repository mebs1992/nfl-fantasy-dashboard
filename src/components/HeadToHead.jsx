import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import { API_BASE } from '../config'
import './HeadToHead.css'

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe']

function HeadToHead() {
  const [teams, setTeams] = useState([])
  const [teamA, setTeamA] = useState('')
  const [teamB, setTeamB] = useState('')
  const [h2hData, setH2hData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchTeams()
  }, [])

  useEffect(() => {
    if (teamA && teamB && teamA !== teamB) {
      fetchHeadToHead()
    } else {
      setH2hData(null)
    }
  }, [teamA, teamB])

  const fetchTeams = async () => {
    try {
      // Try new teams endpoint first
      const response = await axios.get(`${API_BASE}/teams`)
      if (response.data.success) {
        setTeams(response.data.data.sort())
        return
      }
    } catch (err) {
      console.log('Teams endpoint not available, trying alternatives...')
    }
    
    try {
      // Fallback: get teams from matchups
      const matchupsResponse = await axios.get(`${API_BASE}/matchups`)
      if (matchupsResponse.data.success && matchupsResponse.data.data.length > 0) {
        const teamsSet = new Set()
        matchupsResponse.data.data.forEach(m => {
          if (m.team1_name) teamsSet.add(m.team1_name)
          if (m.team2_name) teamsSet.add(m.team2_name)
        })
        setTeams(Array.from(teamsSet).sort())
      }
    } catch (err) {
      console.error('Error fetching teams:', err)
      setError(err.message)
    }
  }

  const fetchHeadToHead = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get(`${API_BASE}/head-to-head`, {
        params: { team1: teamA, team2: teamB }
      })
      if (response.data.success) {
        setH2hData(response.data.data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (error) return <div className="error">Error: {error}</div>

  const pieData = h2hData && h2hData.total_games > 0 ? [
    { name: teamA, value: h2hData.team1_wins, color: COLORS[0] },
    { name: teamB, value: h2hData.team2_wins, color: COLORS[1] },
    ...(h2hData.ties > 0 ? [{ name: 'Ties', value: h2hData.ties, color: COLORS[2] }] : [])
  ].filter(item => item.value > 0) : []

  // Prepare data for yearly breakdown chart
  const yearlyData = h2hData?.games?.reduce((acc, game) => {
    const year = game.year || 'Unknown'
    if (!acc[year]) {
      acc[year] = { year, teamA_wins: 0, teamB_wins: 0, ties: 0 }
    }
    if (game.winner === teamA) {
      acc[year].teamA_wins++
    } else if (game.winner === teamB) {
      acc[year].teamB_wins++
    } else {
      acc[year].ties++
    }
    return acc
  }, {}) || {}

  const yearlyChartData = Object.values(yearlyData).sort((a, b) => a.year - b.year)

  return (
    <div>
      <div className="card">
        <h2>Head-to-Head Statistics</h2>
        
        <div className="h2h-selectors">
          <div className="selector-group">
            <label>Team A</label>
            <select 
              value={teamA} 
              onChange={(e) => setTeamA(e.target.value)}
              className="team-selector"
            >
              <option value="">Select Team A</option>
              {teams.map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
          </div>

          <div className="vs-divider">vs</div>

          <div className="selector-group">
            <label>Team B</label>
            <select 
              value={teamB} 
              onChange={(e) => setTeamB(e.target.value)}
              className="team-selector"
            >
              <option value="">Select Team B</option>
              {teams.map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
          </div>
        </div>

        {teamA && teamB && teamA === teamB && (
          <div className="error-message">
            Please select two different teams
          </div>
        )}

        {loading && (
          <div className="loading">Loading head-to-head data...</div>
        )}

        {h2hData && h2hData.total_games > 0 && (
          <div className="h2h-results">
            <div className="h2h-header">
              <h3>{teamA} vs {teamB}</h3>
              <div className="total-games">All-Time Record</div>
            </div>

            <div className="h2h-stats-grid">
              <div className="stat-card team-a">
                <div className="stat-team-name">{teamA}</div>
                <div className="stat-wins">{h2hData.team1_wins}</div>
                <div className="stat-label">Wins</div>
                <div className="stat-pct">{h2hData.team1_win_pct}%</div>
              </div>

              <div className="stat-card ties">
                <div className="stat-label">Ties</div>
                <div className="stat-ties">{h2hData.ties}</div>
              </div>

              <div className="stat-card team-b">
                <div className="stat-team-name">{teamB}</div>
                <div className="stat-wins">{h2hData.team2_wins}</div>
                <div className="stat-label">Wins</div>
                <div className="stat-pct">{h2hData.team2_win_pct}%</div>
              </div>
            </div>

            <div className="total-games-badge">
              {h2hData.total_games} Total Games
            </div>

            {pieData.length > 0 && (
              <div className="chart-container">
                <h4>Win Distribution</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}

            {yearlyChartData.length > 0 && (
              <div className="chart-container">
                <h4>Year-by-Year Breakdown</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={yearlyChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="teamA_wins" stackId="a" fill={COLORS[0]} name={`${teamA} Wins`} />
                    <Bar dataKey="teamB_wins" stackId="a" fill={COLORS[1]} name={`${teamB} Wins`} />
                    {h2hData.ties > 0 && (
                      <Bar dataKey="ties" stackId="a" fill={COLORS[2]} name="Ties" />
                    )}
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {h2hData.games && h2hData.games.length > 0 && (
              <div className="matchup-history">
                <h4>Matchup History</h4>
                <div className="history-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Year</th>
                        <th>Week</th>
                        <th>{teamA}</th>
                        <th>{teamB}</th>
                        <th>Winner</th>
                      </tr>
                    </thead>
                    <tbody>
                      {h2hData.games
                        .sort((a, b) => {
                          const yearDiff = (b.year || 0) - (a.year || 0)
                          if (yearDiff !== 0) return yearDiff
                          return (b.week || 0) - (a.week || 0)
                        })
                        .map((game, index) => (
                          <tr key={index}>
                            <td>{game.year || 'N/A'}</td>
                            <td>{game.week || 'N/A'}</td>
                            <td className={game.winner === teamA ? 'winner' : ''}>
                              {game.team1_name === teamA ? game.team1_score : game.team2_score}
                            </td>
                            <td className={game.winner === teamB ? 'winner' : ''}>
                              {game.team1_name === teamB ? game.team1_score : game.team2_score}
                            </td>
                            <td className="winner-name">{game.winner || 'Tie'}</td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {h2hData && h2hData.total_games === 0 && (
          <div className="no-data">
            No head-to-head history found between {teamA} and {teamB}
          </div>
        )}

        {!teamA || !teamB ? (
          <div className="select-teams-message">
            Select two teams above to view their head-to-head statistics
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default HeadToHead
