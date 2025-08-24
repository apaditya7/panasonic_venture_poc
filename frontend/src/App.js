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
  const [showPerformanceReport, setShowPerformanceReport] = useState(false);
  const [performanceReport, setPerformanceReport] = useState(null);
  const [criticalAlert, setCriticalAlert] = useState(null);
  const [showCriticalAlert, setShowCriticalAlert] = useState(false);

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
        
        if (machine.anomaly_score > 0.7 && machine.status === 'critical') {
          checkCriticalAlert(machine.machine_id);
        }
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

  const generatePerformanceReport = async () => {
    try {
      const response = await axios.post('http://localhost:8000/api/performance-report');
      setPerformanceReport(response.data);
      setShowPerformanceReport(true);
    } catch (error) {
      setPerformanceReport({
        report: 'Unable to generate performance report at this time.',
        error: true
      });
      setShowPerformanceReport(true);
    }
  };

  const closePerformanceReport = () => {
    setShowPerformanceReport(false);
    setPerformanceReport(null);
  };

  const checkCriticalAlert = async (machineId) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/machines/${machineId}/analyze`);
      const machine = machines.find(m => m.id === machineId);
      if (response.data.anomaly_score > 0.7) {
        setCriticalAlert({
          machineName: machine?.name,
          analysis: response.data.ai_analysis,
          anomalyScore: response.data.anomaly_score,
          severity: 'critical'
        });
        setShowCriticalAlert(true);
      }
    } catch (error) {
      console.error('Error checking critical alert:', error);
    }
  };

  const closeCriticalAlert = () => {
    setShowCriticalAlert(false);
    setCriticalAlert(null);
  };

  const renderStructuredContent = (content, className = '') => {
    if (!content) return null;

    // Check if content is structured (from backend formatting)
    if (content.formatted && content.type === 'structured' && content.sections) {
      return (
        <div className={`structured-content ${className}`}>
          {Object.entries(content.sections).map(([key, value]) => (
            <div key={key} className="content-section">
              <h4 className="section-header">{key.replace(/_/g, ' ').toUpperCase()}</h4>
              <div className="section-content">{value}</div>
            </div>
          ))}
        </div>
      );
    }

    // Fallback to formatted text display
    const textContent = content.content || content.raw_content || content;
    return (
      <div className={`formatted-text ${className}`} dangerouslySetInnerHTML={{
        __html: formatTextForDisplay(textContent)
      }} />
    );
  };

  const formatTextForDisplay = (text) => {
    if (!text) return '';
    
    return text
      // Handle markdown headers
      .replace(/^## (.+)$/gm, '<h3 class="report-section-header">$1</h3>')
      .replace(/^### (.+)$/gm, '<h4 class="report-subsection-header">$1</h4>')
      
      // Handle bold and italic formatting
      .replace(/\*\*(.+?)\*\*/g, '<strong class="report-emphasis">$1</strong>')
      .replace(/\*(.+?)\*/g, '<em class="report-italic">$1</em>')
      
      // Handle structured fields (Issue, Cause, Risk, Action)
      .replace(/^\*\*([A-Za-z]+)\*\*:\s*(.+)$/gm, '<div class="analysis-field"><span class="field-label">$1:</span> <span class="field-content">$2</span></div>')
      
      // Handle bullet points and lists
      .replace(/^-\s+(.+)$/gm, '<div class="bullet-point">• $1</div>')
      .replace(/^\d+\.\s+(.+)$/gm, '<div class="numbered-item">$1</div>')
      
      // Handle line breaks and paragraphs
      .replace(/\n\s*\n/g, '</div><div class="paragraph">')
      .replace(/\n/g, '<br>')
      
      // Wrap in paragraph div
      .replace(/^(.+)/, '<div class="paragraph">$1')
      .replace(/(.+)$/, '$1</div>')
      
      .trim();
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
        <div className="header-content">
          <div>
            <h1>Panasonic Venture POC</h1>
            <p>Industrial Machine Monitoring System</p>
          </div>
          <button className="performance-report-btn" onClick={generatePerformanceReport}>
            📊 AI Performance Report
          </button>
        </div>
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
                  
                  {machineData[machine.id].anomaly_score > 0.3 && machineData[machine.id].anomaly_score <= 0.7 && (
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
                {analysisData.error ? (
                  <div className="error-message">{analysisData.analysis}</div>
                ) : (
                  renderStructuredContent(
                    analysisData.formatted_analysis || analysisData.ai_analysis || analysisData.analysis,
                    'analysis-content-text'
                  )
                )}
                
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

      {showPerformanceReport && performanceReport && (
        <div className="modal-overlay" onClick={closePerformanceReport}>
          <div className="modal-content performance-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📊 AI Performance Report</h2>
              <button className="modal-close" onClick={closePerformanceReport}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="performance-report-content">
                {performanceReport.error ? (
                  <div className="error-message">{performanceReport.report}</div>
                ) : (
                  renderStructuredContent(
                    performanceReport.formatted_data || performanceReport.report,
                    'performance-content'
                  )
                )}
              </div>
            </div>
            
            <div className="modal-footer">
              <button className="modal-btn-close" onClick={closePerformanceReport}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {showCriticalAlert && criticalAlert && (
        <div className="modal-overlay critical-overlay">
          <div className="modal-content critical-alert" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header critical-header">
              <h2>🚨 CRITICAL ALERT</h2>
              <button className="modal-close" onClick={closeCriticalAlert}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="critical-machine-info">
                <h3>{criticalAlert.machineName}</h3>
                <div className="critical-score">
                  <span>Anomaly Score: </span>
                  <span className="critical-score-value">
                    {(criticalAlert.anomalyScore * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              
              <div className="analysis-content">
                <h4>IMMEDIATE ACTION REQUIRED:</h4>
                {renderStructuredContent(
                  criticalAlert.analysis,
                  'critical-analysis-content'
                )}
              </div>
            </div>
            
            <div className="modal-footer">
              <button className="modal-btn-close critical-btn" onClick={closeCriticalAlert}>
                Acknowledge Alert
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
