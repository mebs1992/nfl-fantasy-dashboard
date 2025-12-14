import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import './TeamProfiles.css'
import './EnterpriseTables.css'

const VIEW_OPTIONS = [
  { id: 'team-dna', label: '🧬 Team DNA' },
  { id: 'trophy-case', label: '🏆 Trophy Case' }
]

function TeamProfiles() {
  const [teamDNA, setTeamDNA] = useState([])
  const [trophyCase, setTrophyCase] = useState([])
  const [selectedView, setSelectedView] = useState('team-dna')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAllData()
  }, [])

  const fetchAllData = async () => {
    setLoading(true)
    try {
      await Promise.all([
        fetchTeamDNA(),
        fetchTrophyCase()
      ])
    } finally {
      setLoading(false)
    }
  }

  const fetchTeamDNA = async () => {
    try {
      const response = await axios.get(`${API_BASE}/team-dna`)
      if (response.data.success) {
        setTeamDNA(response.data.data || [])
      }
    } catch (error) {
      console.error('Error fetching team DNA:', error)
    }
  }

  const fetchTrophyCase = async () => {
    try {
      const response = await axios.get(`${API_BASE}/trophy-case`)
      if (response.data.success) {
        setTrophyCase(response.data.data || [])
      }
    } catch (error) {
      console.error('Error fetching trophy case:', error)
    }
  }

  const renderTeamDNA = () => {
    if (teamDNA.length === 0) {
      return <div className="no-data">No team DNA data available</div>
    }

    return (
      <div className="team-dna-container">
        <div className="dna-grid">
          {teamDNA.map((team, index) => (
            <div key={index} className="dna-card">
              <div className="dna-header">
                <img src={team.logo} alt={team.team} className="dna-logo" />
                <div className="dna-info">
                  <h3>{team.team}</h3>
                  <div className="dna-personality">{team.personality}</div>
                </div>
              </div>
              <div className="dna-traits">
                {team.traits.map((trait, i) => (
                  <span key={i} className="trait-badge">{trait}</span>
                ))}
              </div>
              <div className="dna-stats">
                <div className="dna-stat">
                  <span className="stat-label">Seasons:</span>
                  <span className="stat-value">{team.seasons}</span>
                </div>
                <div className="dna-stat">
                  <span className="stat-label">Championships:</span>
                  <span className="stat-value">{team.championships}</span>
                </div>
                <div className="dna-stat">
                  <span className="stat-label">Playoff Rate:</span>
                  <span className="stat-value">{team.playoff_rate}%</span>
                </div>
                {team.consistency && (
                  <div className="dna-stat">
                    <span className="stat-label">Consistency CV:</span>
                    <span className="stat-value">{team.consistency.coefficient_of_variation}%</span>
                  </div>
                )}
                {team.clutch && (
                  <div className="dna-stat">
                    <span className="stat-label">Clutch Factor:</span>
                    <span className="stat-value">{team.clutch.clutch_factor >= 0 ? '+' : ''}{team.clutch.clutch_factor}%</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const renderTrophyCase = () => {
    if (trophyCase.length === 0) {
      return <div className="no-data">No trophy case data available</div>
    }

    return (
      <div className="trophy-case-container">
        <div className="trophy-grid">
          {trophyCase.map((team, index) => (
            <div key={index} className="trophy-card">
              <div className="trophy-header">
                <img src={team.logo} alt={team.team} className="trophy-logo" />
                <h3>{team.team}</h3>
              </div>
              <div className="trophy-achievements">
                {team.championships && team.championships.length > 0 && (
                  <div className="achievement-section">
                    <div className="achievement-label">🏆 Championships ({team.championships.length})</div>
                    <div className="achievement-years">{team.championships.join(', ')}</div>
                  </div>
                )}
                {team.playoff_appearances && team.playoff_appearances.length > 0 && (
                  <div className="achievement-section">
                    <div className="achievement-label">🎯 Playoff Appearances ({team.playoff_appearances.length})</div>
                    <div className="achievement-years">{team.playoff_appearances.join(', ')}</div>
                  </div>
                )}
                {team.scoring_titles && team.scoring_titles.length > 0 && (
                  <div className="achievement-section">
                    <div className="achievement-label">🔥 Scoring Titles ({team.scoring_titles.length})</div>
                    <div className="achievement-years">{team.scoring_titles.join(', ')}</div>
                  </div>
                )}
                {team.highest_weekly_score && team.highest_weekly_score.score > 0 && (
                  <div className="achievement-section">
                    <div className="achievement-label">💥 Highest Weekly Score</div>
                    <div className="achievement-value">{team.highest_weekly_score.score.toFixed(1)} pts ({team.highest_weekly_score.year} W{team.highest_weekly_score.week})</div>
                  </div>
                )}
                {team.longest_win_streak > 0 && (
                  <div className="achievement-section">
                    <div className="achievement-label">🔥 Longest Win Streak</div>
                    <div className="achievement-value">{team.longest_win_streak} games</div>
                  </div>
                )}
                {team.perfect_seasons && team.perfect_seasons.length > 0 && (
                  <div className="achievement-section">
                    <div className="achievement-label">✨ Perfect Seasons</div>
                    <div className="achievement-years">{team.perfect_seasons.join(', ')}</div>
                  </div>
                )}
                {team.spoons && team.spoons.length > 0 && (
                  <div className="achievement-section">
                    <div className="achievement-label">🥄 Spoons ({team.spoons.length})</div>
                    <div className="achievement-years">{team.spoons.join(', ')}</div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (loading) {
    return <div className="team-profiles-loading">Loading team profiles...</div>
  }

  return (
    <div className="team-profiles-container">
      <div className="team-profiles-header">
        <h2>👤 Team Profiles</h2>
        <p>Team DNA, personality traits, and trophy case achievements</p>
      </div>

      <div className="team-profiles-content">
        <div className="team-profiles-sidebar">
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

        <div className="team-profiles-main">
          {selectedView === 'team-dna' && renderTeamDNA()}
          {selectedView === 'trophy-case' && renderTrophyCase()}
        </div>
      </div>
    </div>
  )
}

export default TeamProfiles

