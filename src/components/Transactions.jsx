import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './Transactions.css'

const API_BASE = 'http://localhost:5000/api'

function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchTransactions()
  }, [])

  const fetchTransactions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/transactions`, {
        params: { limit: 100 }
      })
      if (response.data.success) {
        setTransactions(response.data.data)
      }
      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading transactions...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div>
      <div className="card">
        <h2>Recent Transactions</h2>
        {transactions.length === 0 ? (
          <div className="no-data">No transaction data available. Data will appear as it's collected.</div>
        ) : (
          <div className="transactions-list">
            {transactions.map((transaction, index) => (
              <div key={index} className="transaction-item">
                <div className="transaction-header">
                  <span className="transaction-team">{transaction.team || 'Unknown Team'}</span>
                  <span className="transaction-date">
                    {transaction.date ? new Date(transaction.date).toLocaleDateString() : 'Unknown Date'}
                  </span>
                </div>
                <div className="transaction-details">
                  {transaction.type === 'add' && (
                    <span className="transaction-action add">+ Added: {transaction.player}</span>
                  )}
                  {transaction.type === 'drop' && (
                    <span className="transaction-action drop">- Dropped: {transaction.player}</span>
                  )}
                  {transaction.type === 'trade' && (
                    <span className="transaction-action trade">
                      ↔ Trade: {transaction.player1} for {transaction.player2}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Transactions

