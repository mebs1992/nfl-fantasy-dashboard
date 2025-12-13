import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { getTeamImageUrl, getTeamColors } from '../utils/teamImages'
import { API_BASE } from '../config'
import './PlayoffTracker.css'

function PlayoffTracker() {
  const [playoffScenarios, setPlayoffScenarios] = useState(null)
  const [standings, setStandings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchPlayoffScenarios()
    fetchStandings()
  }, [])

  const fetchStandings = async () => {
    try {
      const response = await axios.get(`${API_BASE}/standings`)
      if (response.data.success) {
        setStandings(response.data.data)
      }
    } catch (err) {
      console.error('Error fetching standings:', err)
    }
  }

  const fetchPlayoffScenarios = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/playoff-scenarios`)
      if (response.data.success) {
        setPlayoffScenarios(response.data.data)
      }
      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading playoff scenarios...</div>
  if (error) return <div className="error">Error: {error}</div>
  if (!playoffScenarios) return <div className="no-data">No playoff data available</div>

  return (
    <div className="playoff-tracker-page">
      <div className="playoff-tracker-header">
        <h1 className="animated-title">🎯 Playoff Tracker</h1>
        <p className="playoff-tracker-subtitle">
          Week {playoffScenarios.current_week} • {playoffScenarios.playoff_spots} teams make the playoffs • Tiebreaker: Points For
        </p>
      </div>

      {/* Locked Teams */}
      {playoffScenarios.locked && playoffScenarios.locked.length > 0 && (
        <div className="card playoff-section-card locked-section">
          <h2 className="playoff-section-title locked-title">
            ✅ Locked for Playoffs ({playoffScenarios.locked.length})
          </h2>
          <p className="section-description">
            These teams have secured their playoff spot
          </p>
          <div className="playoff-teams-grid">
            {playoffScenarios.locked.map((team) => {
              const teamColors = getTeamColors(team.team)
              const teamStanding = standings.find(s => s.name === team.team)
              return (
                <div key={team.team} className="playoff-team-card locked-card">
                  <img 
                    src={getTeamImageUrl(team.team, teamStanding?.logo)} 
                    alt={team.team}
                    className="playoff-team-logo"
                    onError={(e) => {
                      e.target.src = getTeamImageUrl(team.team)
                    }}
                  />
                  <div className="playoff-team-info">
                    <div className="playoff-team-name">{team.team}</div>
                    <div className="playoff-team-record">{team.record}</div>
                    <div className="playoff-team-points">PF: {team.points_for.toFixed(2)}</div>
                    <div className="playoff-status-badge locked-badge">🔒 Locked</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Teams in Contention */}
      {playoffScenarios.can_make_it && playoffScenarios.can_make_it.length > 0 && (
        <div className="card playoff-section-card contention-section">
          <h2 className="playoff-section-title contention-title">
            🎲 In Contention ({playoffScenarios.can_make_it.length})
          </h2>
          <p className="section-description">
            These teams are still fighting for a playoff spot
          </p>
          <div className="playoff-teams-grid">
            {playoffScenarios.can_make_it.map((team) => {
              const teamColors = getTeamColors(team.team)
              const teamStanding = standings.find(s => s.name === team.team)
              const needsList = Array.isArray(team.needs) ? team.needs : [team.needs]
              return (
                <div key={team.team} className="playoff-team-card contention-card">
                  <img 
                    src={getTeamImageUrl(team.team, teamStanding?.logo)} 
                    alt={team.team}
                    className="playoff-team-logo"
                    onError={(e) => {
                      e.target.src = getTeamImageUrl(team.team)
                    }}
                  />
                  <div className="playoff-team-info">
                    <div className="playoff-team-name">{team.team}</div>
                    <div className="playoff-team-record">{team.record}</div>
                    <div className="playoff-team-points">PF: {team.points_for.toFixed(2)}</div>
                    <div className="playoff-status-badge contention-badge">{team.status}</div>
                    {needsList && needsList.length > 0 && needsList[0] && (
                      <div className="playoff-needs">
                        <div className="playoff-needs-label">Needs:</div>
                        {needsList.map((need, idx) => (
                          <div key={idx} className="playoff-need-item">{need}</div>
                        ))}
                      </div>
                    )}
                    {team.opponent && (
                      <div className="playoff-matchup">
                        <span className="playoff-vs">vs</span>
                        <span className="playoff-opponent">{team.opponent}</span>
                        <span className="playoff-opponent-record">({team.opponent_record})</span>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Eliminated Teams */}
      {playoffScenarios.eliminated && playoffScenarios.eliminated.length > 0 && (
        <div className="card playoff-section-card eliminated-section">
          <h2 className="playoff-section-title eliminated-title">
            ❌ Eliminated ({playoffScenarios.eliminated.length})
          </h2>
          <p className="section-description">
            These teams have been eliminated from playoff contention
          </p>
          <div className="playoff-teams-grid">
            {playoffScenarios.eliminated.map((team) => {
              const teamColors = getTeamColors(team.team)
              const teamStanding = standings.find(s => s.name === team.team)
              return (
                <div key={team.team} className="playoff-team-card eliminated-card">
                  <img 
                    src={getTeamImageUrl(team.team, teamStanding?.logo)} 
                    alt={team.team}
                    className="playoff-team-logo"
                    onError={(e) => {
                      e.target.src = getTeamImageUrl(team.team)
                    }}
                  />
                  <div className="playoff-team-info">
                    <div className="playoff-team-name">{team.team}</div>
                    <div className="playoff-team-record">{team.record}</div>
                    <div className="playoff-team-points">PF: {team.points_for.toFixed(2)}</div>
                    <div className="playoff-status-badge eliminated-badge">❌ Eliminated</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Week 15 Matchups */}
      {playoffScenarios.week15_matchups && playoffScenarios.week15_matchups.length > 0 && (
        <div className="card playoff-section-card matchups-section">
          <h2 className="playoff-section-title">📅 Week {playoffScenarios.current_week} Matchups</h2>
          <p className="section-description">
            These games will decide playoff fates!
          </p>
          <div className="week-matchups">
            {playoffScenarios.week15_matchups.map((matchup, index) => {
              const team1Standing = standings.find(s => s.name === matchup.team1)
              const team2Standing = standings.find(s => s.name === matchup.team2)
              const team1Colors = getTeamColors(matchup.team1)
              const team2Colors = getTeamColors(matchup.team2)
              
              return (
                <div key={index} className="matchup-card">
                  <div className="matchup-team">
                    <img 
                      src={getTeamImageUrl(matchup.team1, team1Standing?.logo)} 
                      alt={matchup.team1}
                      className="matchup-logo"
                      onError={(e) => {
                        e.target.src = getTeamImageUrl(matchup.team1)
                      }}
                    />
                    <div className="matchup-team-details">
                      <div className="matchup-team-name">{matchup.team1}</div>
                      <div className="matchup-team-record">{matchup.team1_record}</div>
                    </div>
                  </div>
                  <div className="matchup-vs">VS</div>
                  <div className="matchup-team">
                    <img 
                      src={getTeamImageUrl(matchup.team2, team2Standing?.logo)} 
                      alt={matchup.team2}
                      className="matchup-logo"
                      onError={(e) => {
                        e.target.src = getTeamImageUrl(matchup.team2)
                      }}
                    />
                    <div className="matchup-team-details">
                      <div className="matchup-team-name">{matchup.team2}</div>
                      <div className="matchup-team-record">{matchup.team2_record}</div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default PlayoffTracker

