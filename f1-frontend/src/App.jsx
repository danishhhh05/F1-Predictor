import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import './App.css'

const API = 'http://localhost:8000'

const TEAMS = [
  'mercedes','red_bull','ferrari','mclaren','aston_martin',
  'alpine','williams','haas','sauber','racing_point','renault',
  'toro_rosso','force_india','lotus_f1','manor','marussia'
]

const CIRCUITS = [
  {id:'1', name:'Bahrain'}, {id:'2', name:'Saudi Arabia'},
  {id:'3', name:'Australia'}, {id:'4', name:'Japan'},
  {id:'6', name:'China'}, {id:'69', name:'Miami'},
  {id:'71', name:'Emilia Romagna'}, {id:'10', name:'Monaco'},
  {id:'11', name:'Canada'}, {id:'12', name:'Spain'},
  {id:'13', name:'Austria'}, {id:'9', name:'Britain'},
  {id:'14', name:'Hungary'}, {id:'15', name:'Belgium'},
  {id:'16', name:'Netherlands'}, {id:'17', name:'Italy'},
  {id:'73', name:'Azerbaijan'}, {id:'18', name:'Singapore'},
  {id:'70', name:'Las Vegas'}, {id:'32', name:'Abu Dhabi'},
]

const emptyDriver = () => ({
  driver: '', constructor: '', grid: 1, quali_position: 1,
  driver_champ_points: 0, driver_champ_pos: 10,
  constructor_champ_points: 0, constructor_champ_pos: 5,
})

const posClass = (i) => i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : 'other'
const posLabel = (i) => i === 0 ? '1ST' : i === 1 ? '2ND' : i === 2 ? '3RD' : `${i+1}TH`

export default function App() {
  const [drivers, setDrivers] = useState([emptyDriver(), emptyDriver(), emptyDriver()])
  const [raceInfo, setRaceInfo] = useState({ circuit_id: '1', round: 1, year: 2025 })
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const updateDriver = (i, field, val) => {
    setDrivers(d => d.map((dr, idx) => idx === i ? {...dr, [field]: val} : dr))
  }
  const addDriver = () => setDrivers(d => [...d, emptyDriver()])
  const removeDriver = (i) => setDrivers(d => d.filter((_, idx) => idx !== i))

  const predict = async () => {
    setLoading(true); setError(null); setResults(null)
    try {
      const payload = {
        drivers: drivers.map(d => ({
          ...d,
          circuit_id: raceInfo.circuit_id,
          round: Number(raceInfo.round),
          year: Number(raceInfo.year),
          grid: Number(d.grid),
          quali_position: Number(d.quali_position),
          driver_champ_points: Number(d.driver_champ_points),
          driver_champ_pos: Number(d.driver_champ_pos),
          constructor_champ_points: Number(d.constructor_champ_points),
          constructor_champ_pos: Number(d.constructor_champ_pos),
        }))
      }
      const res = await axios.post(`${API}/predict`, payload)
      setResults(res.data.predictions)
    } catch(e) {
      setError(e.response?.data?.detail || 'Could not connect to API. Is it running?')
    }
    setLoading(false)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-badge">ML PREDICTOR</div>
        <h1>F1 <span>RACE</span> PREDICTOR</h1>
        <p>Machine learning predictions for race winners & podium finishers</p>
      </header>

      {/* Race Info */}
      <div className="race-info">
        <div className="form-group">
          <label>Circuit</label>
          <select value={raceInfo.circuit_id}
            onChange={e => setRaceInfo(r => ({...r, circuit_id: e.target.value}))}>
            {CIRCUITS.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Round</label>
          <input type="number" min="1" max="24" value={raceInfo.round}
            onChange={e => setRaceInfo(r => ({...r, round: e.target.value}))} />
        </div>
        <div className="form-group">
          <label>Season Year</label>
          <input type="number" min="2010" max="2026" value={raceInfo.year}
            onChange={e => setRaceInfo(r => ({...r, year: e.target.value}))} />
        </div>
      </div>

      {/* Driver Entries */}
      {drivers.map((d, i) => (
        <div className="driver-entry" key={i}>
          <div className="driver-entry-header">
            <span className="driver-num">DRIVER {i + 1}</span>
            {drivers.length > 2 &&
              <button className="remove-btn" onClick={() => removeDriver(i)}>Remove</button>}
          </div>
          <div className="form-grid">
            <div className="form-group">
              <label>Driver ID</label>
              <input placeholder="e.g. verstappen" value={d.driver}
                onChange={e => updateDriver(i, 'driver', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Constructor</label>
              <select value={d.constructor}
                onChange={e => updateDriver(i, 'constructor', e.target.value)}>
                <option value="">Select team</option>
                {TEAMS.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Grid Position</label>
              <input type="number" min="1" max="20" value={d.grid}
                onChange={e => updateDriver(i, 'grid', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Qualifying Position</label>
              <input type="number" min="1" max="20" value={d.quali_position}
                onChange={e => updateDriver(i, 'quali_position', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Driver Champ Points</label>
              <input type="number" min="0" value={d.driver_champ_points}
                onChange={e => updateDriver(i, 'driver_champ_points', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Driver Champ Position</label>
              <input type="number" min="1" max="20" value={d.driver_champ_pos}
                onChange={e => updateDriver(i, 'driver_champ_pos', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Constructor Points</label>
              <input type="number" min="0" value={d.constructor_champ_points}
                onChange={e => updateDriver(i, 'constructor_champ_points', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Constructor Position</label>
              <input type="number" min="1" max="10" value={d.constructor_champ_pos}
                onChange={e => updateDriver(i, 'constructor_champ_pos', e.target.value)} />
            </div>
          </div>
        </div>
      ))}

      <div className="btn-row">
        <button className="btn btn-secondary" onClick={addDriver}>+ Add Driver</button>
        <button className="btn btn-primary" onClick={predict}
          disabled={loading || drivers.some(d => !d.driver || !d.constructor)}>
          {loading ? 'PREDICTING...' : 'PREDICT RACE'}
        </button>
      </div>

      {/* Results */}
      {loading && (
        <div className="loading">
          <div className="spinner" />
          RUNNING PREDICTION MODEL...
        </div>
      )}

      {error && <div className="error">⚠️ {error}</div>}

      <AnimatePresence>
        {results && (
          <motion.div className="results-section"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}>
            <div className="results-title">🏁 Predicted Race Results</div>
            {results.map((r, i) => (
              <motion.div key={r.driver}
                className={`result-card ${posClass(i)}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.07 }}>
                <div className={`pos-badge ${posClass(i)}`}>{posLabel(i)}</div>
                <div className="driver-info">
                  <div className="name">{r.driver}</div>
                  <div className="team">{r.constructor}</div>
                  <div className="bar-bg" style={{marginTop:'0.5rem'}}>
                    <div className="bar-fill" style={{width: `${r.win_probability}%`}} />
                  </div>
                </div>
                <div className="prob-bars">
                  <div className="prob-item">
                    <div className="prob-label">Win</div>
                    <div className={`prob-value win`}>{r.win_probability}%</div>
                  </div>
                  <div className="prob-item">
                    <div className="prob-label">Podium</div>
                    <div className={`prob-value pod`}>{r.podium_probability}%</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}