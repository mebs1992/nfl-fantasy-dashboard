import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { API_BASE } from '../config'
import './FunStats.css'
import './EnterpriseTables.css'

const VIEW_OPTIONS = [
  { id: 'blowouts', label: '💥 Blowouts' },
  { id: 'bad-beats', label: '😱 Bad Beats' },
  { id: 'weekly-awards', label: '🏆 Weekly Awards' },
  { id: 'clutch', label: '🎯 Clutch Performance' }
]

function FunStats() {
  const [blowouts, setBlowouts] = useState([])
  const [badBeats, setBadBeats] = useState({ high_score_losses: [], low_score_wins: [] })
  const [weeklyAwards, setWeeklyAwards] = useState({ highest_scores: [], lowest_winning_scores: [], biggest_margins: [] })
  const [clutch, setClutch] = useState([])
  const [selectedView, setSelectedView] = useState('blowouts')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAllData()
  }, [])

  const fetchAllData = async () => {
    setLoading(true)
    try {
      await Promise.all([
        fetchBlowouts(),
        fetchBadBeats(),
        fetchWeeklyAwards(),
        fetchClutch()
      ])
    } finally {
      setLoading(false)
    }
  }

  const fetchBlowouts = async () => {
    try {
      const response = await axios.get(`${API_BASE}/blowouts`)
      if (response.data.success) {
        setBlowouts(response.data.data || [])
      }
    } catch (error) {
      console.error('Error fetching blowouts:', error)
    }
  }

  const fetchBadBeats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/bad-beats`)
      if (response.data.success) {
        setBadBeats(response.data.data || { high_score_losses: [], low_score_wins: [] })
      }
    } catch (error) {
      console.error('Error fetching bad beats:', error)
    }
  }

  const fetchWeeklyAwards = async () => {
    try {
      const response = await axios.get(`${API_BASE}/weekly-awards`)
      if (response.data.success) {
        setWeeklyAwards(response.data.data || { highest_scores: [], lowest_winning_scores: [], biggest_margins: [] })
      }
    } catch (error) {
      console.error('Error fetching weekly awards:', error)
    }
  }

  const fetchClutch = async () => {
    try {
      const response = await axios.get(`${API_BASE}/clutch`)
      if (response.data.success) {
        setClutch(response.data.data || [])
      }
    } catch (error) {
      console.error('Error fetching clutch:', error)
    }
  }

  const renderBlowouts = () => {
    if (blowouts.length === 0) {
      return <div className="no-data">No blowouts data available</div>
    }

    return (
      <div className="blowouts-container">
        <div className="blowouts-table-container">
          <table className="data-table">
            <colgroup>
              <col className="col-rank" />
              <col className="col-team" />
              <col className="col-team" />
              <col className="col-num" />
              <col className="col-num" />
              <col className="col-num" />
            </colgroup>
            <thead>
              <tr>
                <th className="rank-header">Rank</th>
                <th className="team-header">Winner</th>
                <th className="team-header">Loser</th>
                <th className="num-header">Winner Score</th>
                <th className="num-header">Loser Score</th>
                <th className="num-header">Margin</th>
              </tr>
            </thead>
            <tbody>
              {blowouts.slice(0, 30).map((blowout, index) => (
                <tr key={index}>
                  <td className="rank-data">{index + 1}</td>
                  <td className="team-data">
                    <img src={blowout.winner_logo} alt={blowout.winner} className="team-logo-small" />
                    {blowout.winner}
                  </td>
                  <td className="team-data">
                    <img src={blowout.loser_logo} alt={blowout.loser} className="team-logo-small" />
                    {blowout.loser}
                  </td>
                  <td className="num-data num-green">{blowout.winner_score.toFixed(1)}</td>
                  <td className="num-data num-red">{blowout.loser_score.toFixed(1)}</td>
                  <td className="num-data num-bold">{blowout.margin.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  const renderBadBeats = () => {
    return (
      <div className="bad-beats-container">
        <div className="bad-beats-section">
          <h3>😱 High Score Losses (Scored 130+ and Lost)</h3>
          <div className="bad-beats-table-container">
            <table className="data-table">
              <colgroup>
                <col className="col-rank" />
                <col className="col-team" />
                <col className="col-team" />
                <col className="col-num" />
                <col className="col-num" />
                <col className="col-num" />
              </colgroup>
              <thead>
                <tr>
                  <th className="rank-header">Rank</th>
                  <th className="team-header">Team</th>
                  <th className="team-header">Opponent</th>
                  <th className="num-header">Team Score</th>
                  <th className="num-header">Opponent Score</th>
                  <th className="num-header">Year/Week</th>
                </tr>
              </thead>
              <tbody>
                {badBeats.high_score_losses?.slice(0, 20).map((beat, index) => (
                  <tr key={index}>
                    <td className="rank-data">{index + 1}</td>
                    <td className="team-data">
                      <img src={beat.team_logo} alt={beat.team} className="team-logo-small" />
                      {beat.team}
                    </td>
                    <td className="team-data">
                      <img src={beat.opponent_logo} alt={beat.opponent} className="team-logo-small" />
                      {beat.opponent}
                    </td>
                    <td className="num-data num-green">{beat.team_score.toFixed(1)}</td>
                    <td className="num-data num-red">{beat.opponent_score.toFixed(1)}</td>
                    <td className="num-data">{beat.year} W{beat.week}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bad-beats-section">
          <h3>😏 Low Score Wins (Scored &lt;90 and Won)</h3>
          <div className="bad-beats-table-container">
            <table className="data-table">
              <colgroup>
                <col className="col-rank" />
                <col className="col-team" />
                <col className="col-team" />
                <col className="col-num" />
                <col className="col-num" />
                <col className="col-num" />
              </colgroup>
              <thead>
                <tr>
                  <th className="rank-header">Rank</th>
                  <th className="team-header">Team</th>
                  <th className="team-header">Opponent</th>
                  <th className="num-header">Team Score</th>
                  <th className="num-header">Opponent Score</th>
                  <th className="num-header">Year/Week</th>
                </tr>
              </thead>
              <tbody>
                {badBeats.low_score_wins?.slice(0, 20).map((beat, index) => (
                  <tr key={index}>
                    <td className="rank-data">{index + 1}</td>
                    <td className="team-data">
                      <img src={beat.team_logo} alt={beat.team} className="team-logo-small" />
                      {beat.team}
                    </td>
                    <td className="team-data">
                      <img src={beat.opponent_logo} alt={beat.opponent} className="team-logo-small" />
                      {beat.opponent}
                    </td>
                    <td className="num-data num-orange">{beat.team_score.toFixed(1)}</td>
                    <td className="num-data num-red">{beat.opponent_score.toFixed(1)}</td>
                    <td className="num-data">{beat.year} W{beat.week}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    )
  }

  const renderWeeklyAwards = () => {
    return (
      <div className="weekly-awards-container">
        <div className="awards-section">
          <h3>🔥 Highest Scores of the Week</h3>
          <div className="awards-table-container">
            <table className="data-table">
              <colgroup>
                <col className="col-rank" />
                <col className="col-team" />
                <col className="col-team" />
                <col className="col-num" />
                <col className="col-num" />
                <col className="col-num" />
              </colgroup>
              <thead>
                <tr>
                  <th className="rank-header">Rank</th>
                  <th className="team-header">Team</th>
                  <th className="team-header">Opponent</th>
                  <th className="num-header">Score</th>
                  <th className="num-header">Opponent Score</th>
                  <th className="num-header">Year/Week</th>
                </tr>
              </thead>
              <tbody>
                {weeklyAwards.highest_scores?.slice(0, 20).map((award, index) => (
                  <tr key={index}>
                    <td className="rank-data">{index + 1}</td>
                    <td className="team-data">
                      <img src={award.team_logo} alt={award.team} className="team-logo-small" />
                      {award.team}
                    </td>
                    <td className="team-data">
                      <img src={award.opponent_logo} alt={award.opponent} className="team-logo-small" />
                      {award.opponent}
                    </td>
                    <td className="num-data num-green num-bold">{award.score.toFixed(1)}</td>
                    <td className="num-data">{award.opponent_score.toFixed(1)}</td>
                    <td className="num-data">{award.year} W{award.week}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="awards-section">
          <h3>😅 Lowest Winning Scores</h3>
          <div className="awards-table-container">
            <table className="data-table">
              <colgroup>
                <col className="col-rank" />
                <col className="col-team" />
                <col className="col-team" />
                <col className="col-num" />
                <col className="col-num" />
                <col className="col-num" />
              </colgroup>
              <thead>
                <tr>
                  <th className="rank-header">Rank</th>
                  <th className="team-header">Team</th>
                  <th className="team-header">Opponent</th>
                  <th className="num-header">Score</th>
                  <th className="num-header">Opponent Score</th>
                  <th className="num-header">Year/Week</th>
                </tr>
              </thead>
              <tbody>
                {weeklyAwards.lowest_winning_scores?.slice(0, 20).map((award, index) => (
                  <tr key={index}>
                    <td className="rank-data">{index + 1}</td>
                    <td className="team-data">
                      <img src={award.team_logo} alt={award.team} className="team-logo-small" />
                      {award.team}
                    </td>
                    <td className="team-data">
                      <img src={award.opponent_logo} alt={award.opponent} className="team-logo-small" />
                      {award.opponent}
                    </td>
                    <td className="num-data num-orange">{award.score.toFixed(1)}</td>
                    <td className="num-data num-red">{award.opponent_score.toFixed(1)}</td>
                    <td className="num-data">{award.year} W{award.week}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="awards-section">
          <h3>💥 Biggest Margins of Victory</h3>
          <div className="awards-table-container">
            <table className="data-table">
              <colgroup>
                <col className="col-rank" />
                <col className="col-team" />
                <col className="col-team" />
                <col className="col-num" />
                <col className="col-num" />
                <col className="col-num" />
              </colgroup>
              <thead>
                <tr>
                  <th className="rank-header">Rank</th>
                  <th className="team-header">Winner</th>
                  <th className="team-header">Loser</th>
                  <th className="num-header">Winner Score</th>
                  <th className="num-header">Loser Score</th>
                  <th className="num-header">Margin</th>
                </tr>
              </thead>
              <tbody>
                {weeklyAwards.biggest_margins?.slice(0, 20).map((award, index) => (
                  <tr key={index}>
                    <td className="rank-data">{index + 1}</td>
                    <td className="team-data">
                      <img src={award.winner_logo} alt={award.winner} className="team-logo-small" />
                      {award.winner}
                    </td>
                    <td className="team-data">
                      <img src={award.loser_logo} alt={award.loser} className="team-logo-small" />
                      {award.loser}
                    </td>
                    <td className="num-data num-green">{award.winner_score.toFixed(1)}</td>
                    <td className="num-data num-red">{award.loser_score.toFixed(1)}</td>
                    <td className="num-data num-bold">{award.margin.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    )
  }

  const renderClutch = () => {
    if (clutch.length === 0) {
      return <div className="no-data">No clutch performance data available</div>
    }

    return (
      <div className="clutch-container">
        <div className="clutch-table-container">
          <table className="data-table">
            <colgroup>
              <col className="col-rank" />
              <col className="col-team" />
              <col className="col-num" />
              <col className="col-num" />
              <col className="col-num" />
              <col className="col-num" />
              <col className="col-num" />
            </colgroup>
            <thead>
              <tr>
                <th className="rank-header">Rank</th>
                <th className="team-header">Team</th>
                <th className="num-header">Close Games</th>
                <th className="num-header">Close Win %</th>
                <th className="num-header">All Win %</th>
                <th className="num-header">Clutch Factor</th>
              </tr>
            </thead>
            <tbody>
              {clutch.map((team, index) => (
                <tr key={index}>
                  <td className="rank-data">{index + 1}</td>
                  <td className="team-data">
                    <img src={team.logo} alt={team.team} className="team-logo-small" />
                    {team.team}
                  </td>
                  <td className="num-data">{team.close_games}</td>
                  <td className="num-data">{team.close_win_pct}%</td>
                  <td className="num-data">{team.all_win_pct}%</td>
                  <td className="num-data">
                    <span className={`clutch-factor ${team.clutch_factor >= 0 ? 'positive' : 'negative'}`}>
                      {team.clutch_factor >= 0 ? '+' : ''}{team.clutch_factor}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="clutch-explanation">
          <p><strong>Clutch Factor:</strong> Difference between close game win % and overall win %</p>
          <p>Positive = Better in close games | Negative = Worse in close games</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return <div className="fun-stats-loading">Loading fun stats...</div>
  }

  return (
    <div className="fun-stats-container">
      <div className="fun-stats-header">
        <h2>🎮 Fun Stats</h2>
        <p>Blowouts, bad beats, weekly awards, and clutch performances</p>
      </div>

      <div className="fun-stats-content">
        <div className="fun-stats-sidebar">
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

        <div className="fun-stats-main">
          {selectedView === 'blowouts' && renderBlowouts()}
          {selectedView === 'bad-beats' && renderBadBeats()}
          {selectedView === 'weekly-awards' && renderWeeklyAwards()}
          {selectedView === 'clutch' && renderClutch()}
        </div>
      </div>
    </div>
  )
}

export default FunStats

