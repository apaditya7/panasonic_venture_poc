import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import './App.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

function App() {
  const [machines, setMachines] = useState([]);
  const [machineData, setMachineData] = useState({});
  const [loading, setLoading] = useState(true);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);

  const fetchMachineConfig = async () => {
    try {
      const response = await axios.get('/config/machine_configs.json');
      setMachines(response.data.machines);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching machine config:', error);
      setLoading(false);
    }
  };

  const fetchMachineData = useCallback(async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/machines/data/current');
      const machineDataMap = {};
      response.data.forEach(machine => {
        machineDataMap[machine.machine_id] = {
          ...machine.data,
          status: machine.status,
          anomaly_score: machine.anomaly_score,
          last_updated: machine.last_updated
        };
      });
      setMachineData(machineDataMap);
    } catch (error) {
      const simulatedData = {};
      machines.forEach(machine => {
        simulatedData[machine.id] = generateSimulatedData(machine);
      });
      setMachineData(simulatedData);
    }
  }, [machines]);

  useEffect(() => {
    fetchMachineConfig();
  }, []);

  useEffect(() => {
    if (machines.length > 0) {
      const interval = setInterval(fetchMachineData, 5000);
      fetchMachineData();
      return () => clearInterval(interval);
    }
  }, [machines, fetchMachineData]);

  const generateSimulatedData = (machine) => {
    const ranges = machine.normal_ranges;
    return {
      temperature: Math.random() * (ranges.temperature.max - ranges.temperature.min) + ranges.temperature.min,
      pressure: Math.random() * (ranges.pressure.max - ranges.pressure.min) + ranges.pressure.min,
      vibration: Math.random() * (ranges.vibration.max - ranges.vibration.min) + ranges.vibration.min,
      rpm: Math.random() * (ranges.rpm.max - ranges.rpm.min) + ranges.rpm.min,
      power_consumption: Math.random() * (ranges.power_consumption.max - ranges.power_consumption.min) + ranges.power_consumption.min,
    };
  };

  const getStatusColor = (value, min, max, status) => {
    if (status === 'critical') return '#ff4444';
    if (status === 'warning') return '#ffaa00';
    if (status === 'normal') return '#44ff44';
    if (value < min || value > max) return '#ff4444';
    if (value < min * 1.1 || value > max * 0.9) return '#ffaa00';
    return '#44ff44';
  };

  const getAnomalyColor = (score) => {
    if (!score) return '#e0e0e0';
    if (score >= 0.8) return '#ff4444';
    if (score >= 0.6) return '#ffaa00';
    if (score >= 0.4) return '#ffd700';
    return '#44ff44';
  };

  const analyzeAnomaly = async (machineId) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/machines/${machineId}/analyze`);
      const machine = machines.find(m => m.id === machineId);
      setAnalysisData({
        machineName: machine?.name,
        machineType: machine?.type,
        anomalyScore: response.data.anomaly_score,
        analysis: response.data.ai_analysis || 'No anomalies detected',
        alert: response.data.alert
      });
      setShowAnalysis(true);
    } catch (error) {
      setAnalysisData({
        machineName: machines.find(m => m.id === machineId)?.name,
        analysis: 'Error analyzing anomaly. Please try again.',
        error: true
      });
      setShowAnalysis(true);
    }
  };

  const closeAnalysis = () => {
    setShowAnalysis(false);
    setAnalysisData(null);
  };

  if (loading) {
    return (
      <div className="App">
        <header className="App-header">
          <h1>Panasonic Venture POC</h1>
          <p>Industrial Machine Monitoring System</p>
        </header>
        <main>
          <p>Loading dashboard...</p>
        </main>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Panasonic Venture POC</h1>
        <p>Industrial Machine Monitoring System</p>
      </header>
      <main className="dashboard">
        <div className="machine-grid">
          {machines.map(machine => (
            <div key={machine.id} className="machine-card">
              <h3>{machine.name}</h3>
              <p className="machine-type">{machine.type.replace('_', ' ').toUpperCase()}</p>
              
              {machineData[machine.id] && (
                <>
                  <div className="machine-status">
                    <span className="status-label">Status:</span>
                    <span 
                      className="status-value"
                      style={{ color: getStatusColor(0, 0, 1, machineData[machine.id].status) }}
                    >
                      {machineData[machine.id].status?.toUpperCase() || 'UNKNOWN'}
                    </span>
                    {machineData[machine.id].anomaly_score !== undefined && (
                      <div className="anomaly-score">
                        <span className="anomaly-label">Anomaly Score:</span>
                        <span 
                          className="anomaly-value"
                          style={{ color: getAnomalyColor(machineData[machine.id].anomaly_score) }}
                        >
                          {(machineData[machine.id].anomaly_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="metrics">
                    <div className="metric">
                      <span className="metric-label">Temperature</span>
                      <span 
                        className="metric-value"
                        style={{ 
                          color: getStatusColor(
                            machineData[machine.id].temperature, 
                            machine.normal_ranges.temperature.min, 
                            machine.normal_ranges.temperature.max,
                            machineData[machine.id].status
                          )
                        }}
                      >
                        {machineData[machine.id].temperature.toFixed(1)}°C
                      </span>
                    </div>
                    
                    <div className="metric">
                      <span className="metric-label">Pressure</span>
                      <span 
                        className="metric-value"
                        style={{ 
                          color: getStatusColor(
                            machineData[machine.id].pressure, 
                            machine.normal_ranges.pressure.min, 
                            machine.normal_ranges.pressure.max,
                            machineData[machine.id].status
                          )
                        }}
                      >
                        {machineData[machine.id].pressure.toFixed(0)} PSI
                      </span>
                    </div>
                    
                    <div className="metric">
                      <span className="metric-label">Vibration</span>
                      <span 
                        className="metric-value"
                        style={{ 
                          color: getStatusColor(
                            machineData[machine.id].vibration, 
                            machine.normal_ranges.vibration.min, 
                            machine.normal_ranges.vibration.max,
                            machineData[machine.id].status
                          )
                        }}
                      >
                        {machineData[machine.id].vibration.toFixed(2)} mm/s
                      </span>
                    </div>
                    
                    <div className="metric">
                      <span className="metric-label">RPM</span>
                      <span 
                        className="metric-value"
                        style={{ 
                          color: getStatusColor(
                            machineData[machine.id].rpm, 
                            machine.normal_ranges.rpm.min, 
                            machine.normal_ranges.rpm.max,
                            machineData[machine.id].status
                          )
                        }}
                      >
                        {machineData[machine.id].rpm.toFixed(0)}
                      </span>
                    </div>
                    
                    <div className="metric">
                      <span className="metric-label">Power</span>
                      <span 
                        className="metric-value"
                        style={{ 
                          color: getStatusColor(
                            machineData[machine.id].power_consumption, 
                            machine.normal_ranges.power_consumption.min, 
                            machine.normal_ranges.power_consumption.max,
                            machineData[machine.id].status
                          )
                        }}
                      >
                        {machineData[machine.id].power_consumption.toFixed(1)} kW
                      </span>
                    </div>
                  </div>
                  
                  {machineData[machine.id].anomaly_score > 0.3 && (
                    <button 
                      className="analyze-btn"
                      onClick={() => analyzeAnomaly(machine.id)}
                    >
                      🤖 AI Analysis
                    </button>
                  )}
                </>
              )}
            </div>
          ))}
        </div>
      </main>
      
      {showAnalysis && analysisData && (
        <div className="modal-overlay" onClick={closeAnalysis}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🤖 AI Analysis</h2>
              <button className="modal-close" onClick={closeAnalysis}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="analysis-machine-info">
                <h3>{analysisData.machineName}</h3>
                <p className="machine-type-modal">
                  {analysisData.machineType?.replace('_', ' ').toUpperCase()}
                </p>
                {analysisData.anomalyScore && (
                  <div className="anomaly-score-modal">
                    <span>Anomaly Score: </span>
                    <span 
                      className="score-value"
                      style={{ color: getAnomalyColor(analysisData.anomalyScore) }}
                    >
                      {(analysisData.anomalyScore * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
              </div>
              
              <div className="analysis-content">
                <h4>Analysis:</h4>
                <div className={`analysis-text ${analysisData.error ? 'error' : ''}`}>
                  {analysisData.analysis.split(/\d+\./).map((section, index) => {
                    if (index === 0) return null; // Skip empty first element
                    return (
                      <div key={index} className="analysis-section">
                        <strong>{index}.</strong> {section.trim()}
                      </div>
                    );
                  })}
                </div>
                
                {analysisData.alert && (
                  <div className="alert-info">
                    <h4>Alert Details:</h4>
                    <div className="alert-severity">
                      Severity: <span className={`severity-${analysisData.alert.severity}`}>
                        {analysisData.alert.severity.toUpperCase()}
                      </span>
                    </div>
                    <p className="alert-message">{analysisData.alert.message}</p>
                  </div>
                )}
              </div>
            </div>
            
            <div className="modal-footer">
              <button className="modal-btn-close" onClick={closeAnalysis}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
