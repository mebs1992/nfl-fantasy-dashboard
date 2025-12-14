import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
import './Rivalries.css'

function Rivalries() {
  const [rivalries, setRivalries] = useState([])
  const [trashTalk, setTrashTalk] = useState([])
  const [selectedTeam1, setSelectedTeam1] = useState('')
  const [selectedTeam2, setSelectedTeam2] = useState('')
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRivalries()
    fetchTeams()
  }, [])

  const fetchRivalries = async () => {
    try {
      const response = await axios.get(`${API_BASE}/rivalries`)
      if (response.data.success) {
        setRivalries(response.data.data)
      }
      setLoading(false)
    } catch (error) {
      console.error('Error fetching rivalries:', error)
      setLoading(false)
    }
  }

  const fetchTeams = async () => {
    try {
      const response = await axios.get(`${API_BASE}/teams`)
      if (response.data.success) {
        setTeams(response.data.data)
      }
    } catch (error) {
      console.error('Error fetching teams:', error)
    }
  }

  const generateTrashTalk = async () => {
    if (!selectedTeam1 || !selectedTeam2) {
      alert('Please select both teams')
      return
    }
    
    try {
      const response = await axios.get(`${API_BASE}/trash-talk`, {
        params: { team1: selectedTeam1, team2: selectedTeam2 }
      })
      if (response.data.success) {
        setTrashTalk(response.data.data)
      }
    } catch (error) {
      console.error('Error generating trash talk:', error)
    }
  }

  if (loading) {
    return <div className="rivalries-loading">Loading rivalries...</div>
  }

  return (
    <div className="rivalries-container">
      <div className="rivalries-header">
        <h2>🔥 Rivalries</h2>
        <p>Top rivalries based on games played, competitiveness, and recency</p>
      </div>

      <div className="rivalries-content">
        <div className="rivalries-list">
          {rivalries.slice(0, 10).map((rivalry, index) => (
            <div key={index} className="rivalry-card">
              <div className="rivalry-rank">#{index + 1}</div>
              <div className="rivalry-teams">
                <div className="rivalry-team">
                  <img src={rivalry.team1_logo} alt={rivalry.team1} className="rivalry-logo" />
                  <span className="rivalry-team-name">{rivalry.team1}</span>
                  <span className="rivalry-wins">{rivalry.team1_wins}W</span>
                </div>
                <div className="rivalry-vs">vs</div>
                <div className="rivalry-team">
                  <img src={rivalry.team2_logo} alt={rivalry.team2} className="rivalry-logo" />
                  <span className="rivalry-team-name">{rivalry.team2}</span>
                  <span className="rivalry-wins">{rivalry.team2_wins}W</span>
                </div>
              </div>
              <div className="rivalry-stats">
                <span>{rivalry.games_played} games</span>
                <span>•</span>
                <span>Avg margin: {rivalry.avg_margin} pts</span>
                <span>•</span>
                <span>Rivalry Score: {rivalry.rivalry_score}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="trash-talk-section">
          <h3>💬 Trash Talk Generator</h3>
          <div className="trash-talk-selectors">
            <select 
              value={selectedTeam1} 
              onChange={(e) => setSelectedTeam1(e.target.value)}
              className="team-select"
            >
              <option value="">Select Team 1</option>
              {teams.map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
            <span className="vs-text">vs</span>
            <select 
              value={selectedTeam2} 
              onChange={(e) => setSelectedTeam2(e.target.value)}
              className="team-select"
            >
              <option value="">Select Team 2</option>
              {teams.map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
            <button onClick={generateTrashTalk} className="generate-btn">
              Generate Trash Talk
            </button>
          </div>
          {trashTalk.length > 0 && (
            <div className="trash-talk-results">
              {trashTalk.map((line, index) => (
                <p key={index} className="trash-talk-line">{line}</p>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Rivalries

