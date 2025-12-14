import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { getTeamImageUrl } from '../utils/teamImages'
import { API_BASE } from '../config'
import './LeagueStats.css'

function LeagueStats() {
  const [leagueStats, setLeagueStats] = useState(null)
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchLeagueStats()
  }, [])

  const fetchLeagueStats = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/league-stats`)
      if (response.data.success) {
        setLeagueStats(response.data.data)
      }
    } catch (err) {
      setError(err.message)
      console.error('Error fetching league stats:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading league statistics...</div>
  }

  if (error) {
    return <div className="error">Error: {error}</div>
  }

  if (!leagueStats) {
    return <div className="error">No data available</div>
  }

  const { league_averages, team_stats } = leagueStats
  const teams = Object.values(team_stats).sort((a, b) => a.name.localeCompare(b.name))
  const selectedTeamData = selectedTeam ? team_stats[selectedTeam] : null

  const StatCard = ({ title, value, unit = '', teamValue = null, isHigherBetter = true }) => {
    const showComparison = selectedTeamData && teamValue !== null && teamValue !== undefined
    
    const difference = showComparison ? teamValue - value : 0
    const isAboveAverage = showComparison ? (isHigherBetter ? difference > 0 : difference < 0) : false
    const percentDiff = showComparison && value !== 0 ? ((difference / value) * 100) : 0

    return (
      <div className={`stat-card ${showComparison ? 'has-comparison' : ''}`}>
        <div className="stat-label">{title}</div>
        <div className="stat-value">
          {value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          {unit && <span className="stat-unit">{unit}</span>}
        </div>
        {showComparison && (
          <div className="team-comparison">
            <div className="team-comparison-label">Selected Team</div>
            <div className="team-stat-value">
              {teamValue.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              {unit && <span className="stat-unit">{unit}</span>}
            </div>
            <div className={`comparison-badge ${isAboveAverage ? 'above' : 'below'}`}>
              <span>{isAboveAverage ? '↑' : '↓'}</span>
              <span>{Math.abs(percentDiff).toFixed(1)}% {isAboveAverage ? 'Above' : 'Below'} Average</span>
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="league-stats-page">
      <div className="league-stats-header">
        <h1 className="animated-title">League Statistics</h1>
        <p className="section-description">
          League-wide averages and team comparisons (Historical data: 2012-2024)
        </p>
      </div>

      {/* League Averages Section */}
      <div className="card">
        <h2>League Averages</h2>
        <div className="stats-grid">
          <StatCard 
            title="Average Winning Score" 
            value={league_averages.avg_winning_score}
            unit=" pts"
            teamValue={selectedTeamData ? selectedTeamData.avg_winning_score : null}
            isHigherBetter={true}
          />
          <StatCard 
            title="Average Wins for Playoffs" 
            value={league_averages.avg_wins_for_playoffs}
            unit=" wins"
            teamValue={selectedTeamData ? selectedTeamData.wins : null}
            isHigherBetter={true}
          />
          <StatCard 
            title="Average Points For" 
            value={league_averages.avg_points_for}
            unit=" pts"
            teamValue={selectedTeamData ? selectedTeamData.points_for : null}
            isHigherBetter={true}
          />
          <StatCard 
            title="Average Points Against" 
            value={league_averages.avg_points_against}
            unit=" pts"
            teamValue={selectedTeamData ? selectedTeamData.points_against : null}
            isHigherBetter={false}
          />
          <StatCard 
            title="Average Win %" 
            value={league_averages.avg_win_pct}
            unit="%"
            teamValue={selectedTeamData ? selectedTeamData.win_pct : null}
            isHigherBetter={true}
          />
          <StatCard 
            title="Average Points Per Game" 
            value={league_averages.avg_points_per_game}
            unit=" pts"
            teamValue={selectedTeamData ? selectedTeamData.points_per_game : null}
            isHigherBetter={true}
          />
          <StatCard 
            title="Average Point Differential" 
            value={league_averages.avg_point_differential}
            unit=" pts"
            teamValue={selectedTeamData ? selectedTeamData.point_differential : null}
            isHigherBetter={true}
          />
        </div>
      </div>

      {/* Team Selector */}
      <div className="card">
        <h2>Compare Team Stats</h2>
        <div className="team-selector-section">
          <label htmlFor="team-select" className="team-select-label">
            Select a Team:
          </label>
          <select
            id="team-select"
            className="team-select"
            value={selectedTeam || ''}
            onChange={(e) => setSelectedTeam(e.target.value || null)}
          >
            <option value="">-- Select a Team --</option>
            {teams.map(team => (
              <option key={team.name} value={team.name}>
                {team.name}
              </option>
            ))}
          </select>
        </div>

        {selectedTeamData && (
          <div className="selected-team-section">
            <div className="selected-team-header">
              <img 
                src={getTeamImageUrl(selectedTeamData.name, selectedTeamData.logo)} 
                alt={selectedTeamData.name}
                className="selected-team-logo"
                onError={(e) => {
                  e.target.src = getTeamImageUrl(selectedTeamData.name)
                }}
              />
              <h3>{selectedTeamData.name}</h3>
            </div>
            <div className="team-stats-grid">
              <div className="team-stat-item">
                <div className="team-stat-label">Record</div>
                <div className="team-stat-value-large">
                  {selectedTeamData.wins}-{selectedTeamData.losses}-{selectedTeamData.ties}
                </div>
              </div>
              <div className="team-stat-item">
                <div className="team-stat-label">Win %</div>
                <div className="team-stat-value-large">
                  {selectedTeamData.win_pct.toFixed(1)}%
                </div>
              </div>
              <div className="team-stat-item">
                <div className="team-stat-label">Points For</div>
                <div className="team-stat-value-large">
                  {selectedTeamData.points_for.toFixed(2)}
                </div>
              </div>
              <div className="team-stat-item">
                <div className="team-stat-label">Points Against</div>
                <div className="team-stat-value-large">
                  {selectedTeamData.points_against.toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default LeagueStats

