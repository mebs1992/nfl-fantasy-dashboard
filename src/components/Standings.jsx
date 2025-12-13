import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { getTeamImageUrl, getTeamColors, getTeamTagline } from '../utils/teamImages'
import { API_BASE } from '../config'
import './Standings.css'

function Standings() {
  const [standings, setStandings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [seasonYear, setSeasonYear] = useState(2025)

  useEffect(() => {
    fetchStandings()
  }, [])

  const fetchStandings = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/standings`)
      if (response.data.success) {
        setStandings(response.data.data)
        setSeasonYear(response.data.year || 2025)
      }
      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading {seasonYear} standings...</div>
  if (error) return <div className="error">Error: {error}</div>

  const chartData = standings.map((team) => ({
    name: team.name,
    'Points For': team.points_for || 0,
    'Points Against': team.points_against || 0,
    rank: team.place
  }))

  // Calculate fun stats
  const highestScorer = standings.length > 0 ? standings.reduce((max, team) => 
    team.points_for > max.points_for ? team : max, standings[0]) : null
  const bestRecord = standings.length > 0 ? standings.reduce((best, team) => {
    const teamPct = (team.wins + team.ties * 0.5) / (team.wins + team.losses + team.ties)
    const bestPct = (best.wins + best.ties * 0.5) / (best.wins + best.losses + best.ties)
    return teamPct > bestPct ? team : best
  }, standings[0]) : null

  return (
    <div className="standings-page">
      <div className="standings-header">
        <h1 className="animated-title">{seasonYear} Season Standings</h1>
        <p className="standings-subtitle">Current league standings and statistics</p>
      </div>

      {/* Fun Stats Cards */}
      <div className="fun-stats-grid">
        {highestScorer && (
          <div className="fun-stat-card highlight-card">
            <div className="fun-stat-icon">🔥</div>
            <div className="fun-stat-content">
              <div className="fun-stat-label">Highest Scorer</div>
              <div className="fun-stat-value">{highestScorer.name}</div>
              <div className="fun-stat-detail">{highestScorer.points_for.toFixed(2)} points</div>
            </div>
          </div>
        )}
        {bestRecord && (
          <div className="fun-stat-card highlight-card">
            <div className="fun-stat-icon">⭐</div>
            <div className="fun-stat-content">
              <div className="fun-stat-label">Best Record</div>
              <div className="fun-stat-value">{bestRecord.name}</div>
              <div className="fun-stat-detail">{bestRecord.wins}-{bestRecord.losses}-{bestRecord.ties}</div>
            </div>
          </div>
        )}
        {standings.length > 0 && (
          <div className="fun-stat-card">
            <div className="fun-stat-icon">📊</div>
            <div className="fun-stat-content">
              <div className="fun-stat-label">League Average</div>
              <div className="fun-stat-value">
                {(standings.reduce((sum, t) => sum + t.points_for, 0) / standings.length).toFixed(2)}
              </div>
              <div className="fun-stat-detail">points per team</div>
            </div>
          </div>
        )}
      </div>

      <div className="card standings-card">
        <h2>League Standings</h2>
        <div className="standings-table">
          <table>
            <thead>
              <tr>
                <th className="th-rank">Rank</th>
                <th className="th-team">Team</th>
                <th className="th-record">W-L-T</th>
                <th className="th-winpct">Win %</th>
                <th className="th-points">Points For</th>
                <th className="th-points">Points Against</th>
              </tr>
            </thead>
            <tbody>
              {standings.map((team, index) => {
                const totalGames = team.wins + team.losses + team.ties
                const winPct = totalGames > 0
                  ? ((team.wins + team.ties * 0.5) / totalGames * 100).toFixed(1)
                  : '0.0'
                
                // Determine playoff position class
                let playoffClass = ''
                let medalIcon = ''
                if (team.place === 1) {
                  playoffClass = 'playoff-gold'
                  medalIcon = '🥇'
                } else if (team.place === 2) {
                  playoffClass = 'playoff-silver'
                  medalIcon = '🥈'
                } else if (team.place === 3) {
                  playoffClass = 'playoff-bronze'
                  medalIcon = '🥉'
                } else if (team.place === 4) {
                  playoffClass = 'playoff-fourth'
                  medalIcon = '🎯'
                }
                
                const teamColors = getTeamColors(team.name)
                const teamTagline = getTeamTagline(team.name)
                
                return (
                  <tr 
                    key={team.id} 
                    className={`${playoffClass} team-row`}
                    style={{ '--team-color': teamColors.primary }}
                  >
                    <td className="rank">
                      <span className="rank-number">{team.place}</span>
                      {medalIcon && <span className="medal-icon">{medalIcon}</span>}
                    </td>
                    <td className="team-cell">
                      <div className="team-info">
                        <img 
                          src={getTeamImageUrl(team.name, team.logo)} 
                          alt={team.name}
                          className="team-avatar"
                          onError={(e) => {
                            e.target.src = getTeamImageUrl(team.name)
                          }}
                        />
                        <div className="team-details">
                          <div className="team-name">{team.name}</div>
                          <div className="team-tagline">{teamTagline}</div>
                        </div>
                      </div>
                    </td>
                    <td className="record-cell">
                      <span className="record-badge">{team.wins}-{team.losses}-{team.ties || 0}</span>
                    </td>
                    <td className="winpct-cell">
                      <div className="winpct-container">
                        <span className="winpct-value">{winPct}%</span>
                        <div className="winpct-bar">
                          <div 
                            className="winpct-fill" 
                            style={{ width: `${winPct}%`, background: teamColors.gradient }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="points points-for">{team.points_for?.toFixed(2) || '0.00'}</td>
                    <td className="points points-against">{team.points_against?.toFixed(2) || '0.00'}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Standings

