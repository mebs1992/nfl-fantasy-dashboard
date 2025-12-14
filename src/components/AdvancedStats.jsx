import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { API_BASE } from '../config'
import { getTeamImageUrl } from '../utils/teamImages'
import './AdvancedStats.css'
import './EnterpriseTables.css'

const VIEW_OPTIONS = [
  { id: 'rivalries', label: '🔥 Rivalries' },
  { id: 'current-streaks', label: '📊 Current Streaks' },
  { id: 'all-time-streaks', label: '🏆 All-Time Streaks' },
  { id: 'points-trends', label: '📈 Points Trends' },
  { id: 'consistency', label: '🎯 Consistency Score' },
  { id: 'blowouts', label: '💥 Blowouts' },
  { id: 'bad-beats', label: '😱 Bad Beats' },
  { id: 'weekly-awards', label: '🏆 Weekly Awards' },
  { id: 'lowest-scoring-weeks', label: '📉 Lowest Scoring Weeks' },
  { id: 'clutch', label: '⚡ Clutch Performance' },
  { id: 'team-dna', label: '🧬 Team DNA' },
  { id: 'trophy-case', label: '🏅 Trophy Case' },
  { id: 'what-if', label: '🔮 What-If' },
  { id: 'weekly-recap', label: '📰 Weekly Recap' }
]

const TEAM_LINE_COLORS = [
  '#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe',
  '#FFD700', '#C0C0C0', '#CD7F32', '#10b981', '#ef4444'
]

function AdvancedStats() {
  const [selectedView, setSelectedView] = useState('rivalries')
  const [loading, setLoading] = useState(true)
  
  // Data states
  const [rivalries, setRivalries] = useState([])
  const [currentStreaks, setCurrentStreaks] = useState([])
  const [allTimeStreaks, setAllTimeStreaks] = useState([])
  const [pointsTrends, setPointsTrends] = useState([])
  const [consistency, setConsistency] = useState([])
  const [blowouts, setBlowouts] = useState([])
  const [badBeats, setBadBeats] = useState({ high_score_losses: [], low_score_wins: [] })
  const [weeklyAwards, setWeeklyAwards] = useState({ highest_scores: [], lowest_winning_scores: [], biggest_margins: [] })
  const [clutch, setClutch] = useState([])
  const [teamDNA, setTeamDNA] = useState([])
  const [trophyCase, setTrophyCase] = useState([])
  const [lowestScoringWeeks, setLowestScoringWeeks] = useState([])
  const [teams, setTeams] = useState([])
  const [trashTalk, setTrashTalk] = useState([])
  const [selectedTeam1, setSelectedTeam1] = useState('')
  const [selectedTeam2, setSelectedTeam2] = useState('')
  const [whatIfScenario, setWhatIfScenario] = useState({ year: 2025, week: 15, team1: '', team2: '', newWinner: '' })
  const [whatIfResult, setWhatIfResult] = useState(null)
  const [recapYear, setRecapYear] = useState(2025)
  const [recapWeek, setRecapWeek] = useState(15)
  const [recap, setRecap] = useState(null)

  useEffect(() => {
    fetchAllData()
    fetchTeams()
  }, [])

  const fetchAllData = async () => {
    setLoading(true)
    try {
      await Promise.all([
        fetchRivalries(),
        fetchStreaks(),
        fetchPointsTrends(),
        fetchConsistency(),
        fetchBlowouts(),
        fetchBadBeats(),
        fetchWeeklyAwards(),
        fetchLowestScoringWeeks(),
        fetchClutch(),
        fetchTeamDNA(),
        fetchTrophyCase()
      ])
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
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

  const fetchRivalries = async () => {
    try {
      const response = await axios.get(`${API_BASE}/rivalries`)
      if (response.data.success) {
        setRivalries(response.data.data || [])
      } else {
        console.error('Rivalries API returned success=false:', response.data.error)
      }
    } catch (error) {
      console.error('Error fetching rivalries:', error)
      setRivalries([])
    }
  }

  const fetchStreaks = async () => {
    try {
      const response = await axios.get(`${API_BASE}/streaks`)
      if (response.data.success) {
        setCurrentStreaks(response.data.data?.current || [])
        setAllTimeStreaks(response.data.data?.all_time || [])
      } else {
        console.error('Streaks API returned success=false:', response.data.error)
      }
    } catch (error) {
      console.error('Error fetching streaks:', error)
      setCurrentStreaks([])
      setAllTimeStreaks([])
    }
  }

  const fetchPointsTrends = async () => {
    try {
      const response = await axios.get(`${API_BASE}/points-trends`)
      if (response.data.success) {
        setPointsTrends(response.data.data || [])
      } else {
        console.error('Points trends API returned success=false:', response.data.error)
      }
    } catch (error) {
      console.error('Error fetching points trends:', error)
      setPointsTrends([])
    }
  }

  const fetchConsistency = async () => {
    try {
      const response = await axios.get(`${API_BASE}/consistency`)
      if (response.data.success) {
        setConsistency(response.data.data || [])
      } else {
        console.error('Consistency API returned success=false:', response.data.error)
      }
    } catch (error) {
      console.error('Error fetching consistency:', error)
      setConsistency([])
    }
  }

  const fetchBlowouts = async () => {
    try {
      const response = await axios.get(`${API_BASE}/blowouts`)
      if (response.data.success) {
        setBlowouts(response.data.data || [])
      } else {
        console.error('Blowouts API returned success=false:', response.data.error)
      }
    } catch (error) {
      console.error('Error fetching blowouts:', error)
      setBlowouts([])
    }
  }

  const fetchBadBeats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/bad-beats`)
      if (response.data.success) {
        setBadBeats(response.data.data || { high_score_losses: [], low_score_wins: [] })
      } else {
        console.error('Bad beats API returned success=false:', response.data.error)
      }
    } catch (error) {
      console.error('Error fetching bad beats:', error)
      setBadBeats({ high_score_losses: [], low_score_wins: [] })
    }
  }

  const fetchWeeklyAwards = async () => {
    try {
      const response = await axios.get(`${API_BASE}/weekly-awards`)
      if (response.data.success) {
        setWeeklyAwards(response.data.data || { highest_scores: [], lowest_winning_scores: [], biggest_margins: [] })
      } else {
        console.error('Weekly awards API returned success=false:', response.data.error)
      }
    } catch (error) {
      console.error('Error fetching weekly awards:', error)
      setWeeklyAwards({ highest_scores: [], lowest_winning_scores: [], biggest_margins: [] })
    }
  }

  const fetchClutch = async () => {
    try {
      const response = await axios.get(`${API_BASE}/clutch`)
      if (response.data.success) {
        setClutch(response.data.data || [])
      } else {
        console.error('Clutch API returned success=false:', response.data.error)
      }
    } catch (error) {
      console.error('Error fetching clutch:', error)
      setClutch([])
    }
  }

  const fetchTeamDNA = async () => {
    try {
      const response = await axios.get(`${API_BASE}/team-dna`)
      if (response.data.success) {
        setTeamDNA(response.data.data || [])
      } else {
        console.error('Team DNA API returned success=false:', response.data.error)
      }
    } catch (error) {
      console.error('Error fetching team DNA:', error)
      setTeamDNA([])
    }
  }

  const fetchTrophyCase = async () => {
    try {
      const response = await axios.get(`${API_BASE}/trophy-case`)
      if (response.data.success) {
        setTrophyCase(response.data.data || [])
      } else {
        console.error('Trophy case API returned success=false:', response.data.error)
      }
    } catch (error) {
      console.error('Error fetching trophy case:', error)
      setTrophyCase([])
    }
  }

  const fetchLowestScoringWeeks = async () => {
    try {
      const response = await axios.get(`${API_BASE}/lowest-scoring-weeks`)
      if (response.data.success) {
        setLowestScoringWeeks(response.data.data || [])
      } else {
        console.error('Lowest scoring weeks API returned success=false:', response.data.error)
      }
    } catch (error) {
      console.error('Error fetching lowest scoring weeks:', error)
      setLowestScoringWeeks([])
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

  const calculateWhatIf = async () => {
    try {
      const response = await axios.post(`${API_BASE}/what-if`, { scenario: whatIfScenario })
      if (response.data.success) {
        setWhatIfResult(response.data.data)
      }
    } catch (error) {
      console.error('Error calculating what-if:', error)
    }
  }

  const fetchRecap = async () => {
    try {
      const response = await axios.get(`${API_BASE}/weekly-recap`, {
        params: { year: recapYear, week: recapWeek }
      })
      if (response.data.success) {
        setRecap(response.data.data)
      }
    } catch (error) {
      console.error('Error fetching recap:', error)
    }
  }

  // Render functions for each view
  const renderRivalries = () => (
    <div className="view-content">
      <div className="rivalries-list">
        {rivalries.length > 0 ? rivalries.slice(0, 15).map((rivalry, index) => (
          <div key={index} className="rivalry-card">
            <div className="rivalry-rank">#{index + 1}</div>
            <div className="rivalry-teams">
              <div className="rivalry-team">
                  {rivalry.team1_logo && <img src={getTeamImageUrl(rivalry.team1, rivalry.team1_logo)} alt={rivalry.team1} className="rivalry-logo" onError={(e) => e.target.style.display = 'none'} />}
                  <span>{rivalry.team1}</span>
                  <span className="rivalry-wins">{rivalry.team1_wins}W</span>
                </div>
                <div className="rivalry-vs">vs</div>
                <div className="rivalry-team">
                  {rivalry.team2_logo && <img src={getTeamImageUrl(rivalry.team2, rivalry.team2_logo)} alt={rivalry.team2} className="rivalry-logo" onError={(e) => e.target.style.display = 'none'} />}
                <span>{rivalry.team2}</span>
                <span className="rivalry-wins">{rivalry.team2_wins}W</span>
              </div>
            </div>
            <div className="rivalry-stats">
              {rivalry.games_played} games • Avg margin: {rivalry.avg_margin} pts
            </div>
          </div>
        )) : <div className="no-data">No rivalries data available</div>}
      </div>
      <div className="trash-talk-section">
        <h3>💬 Trash Talk Generator</h3>
        <div className="trash-talk-selectors">
          <select value={selectedTeam1} onChange={(e) => setSelectedTeam1(e.target.value)} className="team-select">
            <option value="">Select Team 1</option>
            {teams.map(team => <option key={team} value={team}>{team}</option>)}
          </select>
          <span className="vs-text">vs</span>
          <select value={selectedTeam2} onChange={(e) => setSelectedTeam2(e.target.value)} className="team-select">
            <option value="">Select Team 2</option>
            {teams.map(team => <option key={team} value={team}>{team}</option>)}
          </select>
          <button onClick={generateTrashTalk} className="generate-btn">Generate</button>
        </div>
        {trashTalk.length > 0 && (
          <div className="trash-talk-results">
            {trashTalk.map((line, i) => <p key={i}>{line}</p>)}
          </div>
        )}
      </div>
    </div>
  )

  const renderStreaks = (streaks, isCurrent = false) => {
    if (!streaks || streaks.length === 0) {
      return <div className="no-data">No {isCurrent ? 'current' : 'all-time'} streaks data available</div>
    }
    return (
      <div className="table-container">
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
            {streaks.map((streak, index) => (
              <tr key={index}>
                <td className="rank-data">{index + 1}</td>
                <td className="team-data">
                  {streak.logo && <img src={getTeamImageUrl(streak.team, streak.logo)} alt={streak.team} className="team-logo-small" onError={(e) => e.target.style.display = 'none'} />}
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
    if (!pointsTrends || pointsTrends.length === 0) {
      return <div className="no-data">No points trends data available</div>
    }
    const chartData = {}
    pointsTrends.forEach(team => {
      team.yearly_averages?.forEach(yearData => {
        if (!chartData[yearData.year]) chartData[yearData.year] = {}
        chartData[yearData.year][team.team] = yearData.avg_score
      })
    })
    const years = Object.keys(chartData).sort().map(Number)
    const chartDataArray = years.map(year => {
      const data = { year }
      pointsTrends.forEach(team => {
        const yearData = team.yearly_averages?.find(y => y.year === year)
        if (yearData) data[team.team] = yearData.avg_score
      })
      return data
    })
    const topTeams = [...pointsTrends].sort((a, b) => b.overall_avg - a.overall_avg).slice(0, 8)
    return (
      <div className="trends-container">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartDataArray}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="year" stroke="#333" />
            <YAxis stroke="#333" />
            <Tooltip />
            <Legend />
            {topTeams.map((team, i) => (
              <Line key={team.team} type="monotone" dataKey={team.team} 
                stroke={TEAM_LINE_COLORS[i % TEAM_LINE_COLORS.length]} strokeWidth={2} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    )
  }

  const renderConsistency = () => {
    if (!consistency || consistency.length === 0) {
      return <div className="no-data">No consistency data available</div>
    }
    return (
      <div className="table-container">
        <table className="data-table">
          <colgroup>
            <col className="col-rank" />
            <col className="col-team" />
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
            </tr>
          </thead>
          <tbody>
            {consistency.map((team, index) => (
              <tr key={index}>
                <td className="rank-data">{index + 1}</td>
                <td className="team-data">
                  {team.logo && <img src={getTeamImageUrl(team.team, team.logo)} alt={team.team} className="team-logo-small" onError={(e) => e.target.style.display = 'none'} />}
                  {team.team}
                </td>
                <td className="num-data">{team.avg_score}</td>
                <td className="num-data">{team.std_dev}</td>
                <td className="num-data">{team.coefficient_of_variation}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  const renderBlowouts = () => {
    if (!blowouts || blowouts.length === 0) {
      return <div className="no-data">No blowouts data available</div>
    }
    return (
      <div className="table-container">
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
                  {blowout.winner_logo && <img src={getTeamImageUrl(blowout.winner, blowout.winner_logo)} alt={blowout.winner} className="team-logo-small" onError={(e) => e.target.style.display = 'none'} />}
                  {blowout.winner}
                </td>
                <td className="team-data">
                  {blowout.loser_logo && <img src={getTeamImageUrl(blowout.loser, blowout.loser_logo)} alt={blowout.loser} className="team-logo-small" onError={(e) => e.target.style.display = 'none'} />}
                  {blowout.loser}
                </td>
                <td className="num-data num-green">{blowout.winner_score?.toFixed(1)}</td>
                <td className="num-data num-red">{blowout.loser_score?.toFixed(1)}</td>
                <td className="num-data num-bold">{blowout.margin?.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  const renderBadBeats = () => (
    <div className="view-content">
      <div className="bad-beats-section">
        <h3>😱 High Score Losses (130+ and Lost)</h3>
        <div className="table-container">
          <table className="data-table">
            <colgroup>
              <col className="col-rank" />
              <col className="col-team" />
              <col className="col-team" />
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
              </tr>
            </thead>
            <tbody>
              {badBeats.high_score_losses?.slice(0, 20).map((beat, index) => (
                <tr key={index}>
                  <td className="rank-data">{index + 1}</td>
                  <td className="team-data">
                    {beat.team_logo && <img src={getTeamImageUrl(beat.team, beat.team_logo)} alt={beat.team} className="team-logo-small" onError={(e) => e.target.style.display = 'none'} />}
                    {beat.team}
                  </td>
                  <td className="team-data">
                    {beat.opponent_logo && <img src={getTeamImageUrl(beat.opponent, beat.opponent_logo)} alt={beat.opponent} className="team-logo-small" onError={(e) => e.target.style.display = 'none'} />}
                    {beat.opponent}
                  </td>
                  <td className="num-data num-green">{beat.team_score?.toFixed(1)}</td>
                  <td className="num-data num-red">{beat.opponent_score?.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <div className="bad-beats-section">
        <h3>😏 Low Score Wins (&lt;90 and Won)</h3>
        <div className="table-container">
          <table className="data-table">
            <colgroup>
              <col className="col-rank" />
              <col className="col-team" />
              <col className="col-team" />
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
              </tr>
            </thead>
            <tbody>
              {badBeats.low_score_wins?.slice(0, 20).map((beat, index) => (
                <tr key={index}>
                  <td className="rank-data">{index + 1}</td>
                  <td className="team-data">
                    {beat.team_logo && <img src={getTeamImageUrl(beat.team, beat.team_logo)} alt={beat.team} className="team-logo-small" onError={(e) => e.target.style.display = 'none'} />}
                    {beat.team}
                  </td>
                  <td className="team-data">
                    {beat.opponent_logo && <img src={getTeamImageUrl(beat.opponent, beat.opponent_logo)} alt={beat.opponent} className="team-logo-small" onError={(e) => e.target.style.display = 'none'} />}
                    {beat.opponent}
                  </td>
                  <td className="num-data num-orange">{beat.team_score?.toFixed(1)}</td>
                  <td className="num-data num-red">{beat.opponent_score?.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  const renderWeeklyAwards = () => (
    <div className="view-content">
      <div className="awards-section">
        <h3>🔥 Highest Scores</h3>
        <div className="table-container">
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
                <th className="num-header">Score</th>
                <th className="num-header">Year/Week</th>
              </tr>
            </thead>
            <tbody>
              {weeklyAwards.highest_scores?.slice(0, 20).map((award, index) => (
                <tr key={index}>
                  <td className="rank-data">{index + 1}</td>
                  <td className="team-data">
                    {award.team_logo && <img src={getTeamImageUrl(award.team, award.team_logo)} alt={award.team} className="team-logo-small" onError={(e) => e.target.style.display = 'none'} />}
                    {award.team}
                  </td>
                  <td className="num-data num-green num-bold">{award.score?.toFixed(1)}</td>
                  <td className="num-data">{award.year} W{award.week}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  const renderLowestScoringWeeks = () => {
    if (!lowestScoringWeeks || lowestScoringWeeks.length === 0) {
      return <div className="no-data">No lowest scoring weeks data available</div>
    }
    return (
      <div className="table-container">
        <table className="data-table">
          <colgroup>
            <col className="col-rank" />
            <col className="col-team" />
            <col className="col-num" />
            <col className="col-team" />
            <col className="col-num" />
            <col className="col-num" />
          </colgroup>
          <thead>
            <tr>
              <th className="rank-header">Rank</th>
              <th className="team-header">Team</th>
              <th className="num-header">Score</th>
              <th className="team-header">Opponent</th>
              <th className="num-header">Opponent Score</th>
              <th className="num-header">Year/Week</th>
            </tr>
          </thead>
          <tbody>
            {lowestScoringWeeks.map((week, index) => (
              <tr key={index}>
                <td className="rank-data">{index + 1}</td>
                <td className="team-data">
                  {week.team_logo && <img src={getTeamImageUrl(week.team, week.team_logo)} alt={week.team} className="team-logo-small" onError={(e) => e.target.style.display = 'none'} />}
                  {week.team}
                </td>
                <td className="num-data num-red num-bold">{week.score?.toFixed(1)}</td>
                <td className="team-data">
                  {week.opponent_logo && <img src={getTeamImageUrl(week.opponent, week.opponent_logo)} alt={week.opponent} className="team-logo-small" onError={(e) => e.target.style.display = 'none'} />}
                  {week.opponent}
                </td>
                <td className="num-data">{week.opponent_score?.toFixed(1)}</td>
                <td className="num-data">{week.year} W{week.week}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  const renderClutch = () => {
    if (!clutch || clutch.length === 0) {
      return <div className="no-data">No clutch data available</div>
    }
    return (
      <div className="table-container">
        <table className="data-table">
          <colgroup>
            <col className="col-rank" />
            <col className="col-team" />
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
              <th className="num-header">Clutch Factor</th>
            </tr>
          </thead>
          <tbody>
            {clutch.map((team, index) => (
              <tr key={index}>
                <td className="rank-data">{index + 1}</td>
                <td className="team-data">
                  {team.logo && <img src={getTeamImageUrl(team.team, team.logo)} alt={team.team} className="team-logo-small" onError={(e) => e.target.style.display = 'none'} />}
                  {team.team}
                </td>
                <td className="num-data">{team.close_games}</td>
                <td className="num-data">{team.close_win_pct}%</td>
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
    )
  }

  const renderTeamDNA = () => {
    if (!teamDNA || teamDNA.length === 0) {
      return <div className="no-data">No team DNA data available</div>
    }
    return (
      <div className="dna-grid">
        {teamDNA.map((team, index) => (
          <div key={index} className="dna-card">
            <div className="dna-header">
                  {team.logo && <img src={getTeamImageUrl(team.team, team.logo)} alt={team.team} className="dna-logo" onError={(e) => e.target.style.display = 'none'} />}
                  <div>
                    <h3>{team.team}</h3>
                    <div className="dna-personality">{team.personality}</div>
                  </div>
                </div>
                <div className="dna-traits">
                  {team.traits?.map((trait, i) => (
                    <span key={i} className="trait-badge">{trait}</span>
                  ))}
                </div>
                <div className="dna-stats">
                  <div>Seasons: {team.seasons}</div>
                  <div>Championships: {team.championships}</div>
                  <div>Playoff Rate: {team.playoff_rate}%</div>
                </div>
              </div>
            ))}
          </div>
        )
      }

      const renderTrophyCase = () => {
        if (!trophyCase || trophyCase.length === 0) {
          return <div className="no-data">No trophy case data available</div>
        }
        return (
          <div className="trophy-grid">
            {trophyCase.map((team, index) => (
              <div key={index} className="trophy-card">
                <div className="trophy-header">
                  {team.logo && <img src={getTeamImageUrl(team.team, team.logo)} alt={team.team} className="trophy-logo" onError={(e) => e.target.style.display = 'none'} />}
              <h3>{team.team}</h3>
            </div>
            <div className="trophy-achievements">
              {team.championships?.length > 0 && (
                <div>🏆 Championships: {team.championships.join(', ')}</div>
              )}
              {team.scoring_titles?.length > 0 && (
                <div>🔥 Scoring Titles: {team.scoring_titles.join(', ')}</div>
              )}
              {team.highest_weekly_score?.score > 0 && (
                <div>💥 Highest Score: {team.highest_weekly_score.score.toFixed(1)} ({team.highest_weekly_score.year} W{team.highest_weekly_score.week})</div>
              )}
              {team.longest_win_streak > 0 && (
                <div>🔥 Longest Win Streak: {team.longest_win_streak}</div>
              )}
            </div>
          </div>
        ))}
      </div>
    )
  }

  const renderWhatIf = () => (
    <div className="what-if-form">
      <div className="form-group">
        <label>Year</label>
        <input type="number" value={whatIfScenario.year} onChange={(e) => setWhatIfScenario({...whatIfScenario, year: parseInt(e.target.value)})} />
      </div>
      <div className="form-group">
        <label>Week</label>
        <input type="number" value={whatIfScenario.week} onChange={(e) => setWhatIfScenario({...whatIfScenario, week: parseInt(e.target.value)})} />
      </div>
      <div className="form-group">
        <label>Team 1</label>
        <input type="text" value={whatIfScenario.team1} onChange={(e) => setWhatIfScenario({...whatIfScenario, team1: e.target.value})} />
      </div>
      <div className="form-group">
        <label>Team 2</label>
        <input type="text" value={whatIfScenario.team2} onChange={(e) => setWhatIfScenario({...whatIfScenario, team2: e.target.value})} />
      </div>
      <div className="form-group">
        <label>New Winner</label>
        <input type="text" value={whatIfScenario.newWinner} onChange={(e) => setWhatIfScenario({...whatIfScenario, newWinner: e.target.value})} />
      </div>
      <button onClick={calculateWhatIf} className="calculate-btn">Calculate</button>
      {whatIfResult && <div className="result-message">{whatIfResult.message}</div>}
    </div>
  )

  const renderWeeklyRecap = () => (
    <div className="recap-controls">
      <div className="control-group">
        <label>Year</label>
        <input type="number" value={recapYear} onChange={(e) => setRecapYear(parseInt(e.target.value))} />
      </div>
      <div className="control-group">
        <label>Week</label>
        <input type="number" value={recapWeek} onChange={(e) => setRecapWeek(parseInt(e.target.value))} />
      </div>
      <button onClick={fetchRecap} className="generate-btn">Generate Recap</button>
      {recap && (
        <div className="recap-content">
          <h3>{recap.year} Week {recap.week}</h3>
          <p>{recap.summary}</p>
          {recap.highest_score && (
            <div>🔥 Highest: {recap.highest_score.team} ({recap.highest_score.score.toFixed(1)})</div>
          )}
        </div>
      )}
    </div>
  )

  if (loading) {
    return <div className="advanced-stats-loading">Loading advanced stats...</div>
  }

  return (
    <div className="advanced-stats-container">
      <div className="advanced-stats-header">
        <h2>📊 Advanced Stats</h2>
        <p>Rivalries, streaks, trends, fun stats, and more</p>
      </div>

      <div className="advanced-stats-content">
        <div className="advanced-stats-sidebar">
          <select value={selectedView} onChange={(e) => setSelectedView(e.target.value)} className="view-selector">
            {VIEW_OPTIONS.map(option => (
              <option key={option.id} value={option.id}>{option.label}</option>
            ))}
          </select>
        </div>

        <div className="advanced-stats-main">
          {selectedView === 'rivalries' && renderRivalries()}
          {selectedView === 'current-streaks' && renderStreaks(currentStreaks, true)}
          {selectedView === 'all-time-streaks' && renderStreaks(allTimeStreaks, false)}
          {selectedView === 'points-trends' && renderPointsTrends()}
          {selectedView === 'consistency' && renderConsistency()}
          {selectedView === 'blowouts' && renderBlowouts()}
          {selectedView === 'bad-beats' && renderBadBeats()}
          {selectedView === 'weekly-awards' && renderWeeklyAwards()}
          {selectedView === 'lowest-scoring-weeks' && renderLowestScoringWeeks()}
          {selectedView === 'clutch' && renderClutch()}
          {selectedView === 'team-dna' && renderTeamDNA()}
          {selectedView === 'trophy-case' && renderTrophyCase()}
          {selectedView === 'what-if' && renderWhatIf()}
          {selectedView === 'weekly-recap' && renderWeeklyRecap()}
        </div>
      </div>
    </div>
  )
}

export default AdvancedStats

