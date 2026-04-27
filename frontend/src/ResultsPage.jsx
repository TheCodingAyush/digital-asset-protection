import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
import { useNavigate, Link } from 'react-router-dom';
import { auth } from './firebase';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import PropagationGraph from './PropagationGraph';
import './upload.css';
import './results.css';

const ResultsPage = () => {
  const [user, setUser] = useState(null);
  const [matches, setMatches] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (!currentUser) {
        navigate('/login');
      } else {
        setUser(currentUser);
      }
    });
    return () => unsubscribe();
  }, [navigate]);

  useEffect(() => {
    try {
      const storedResults = localStorage.getItem('framelens_results');
      if (!storedResults) {
        navigate('/dashboard');
        return;
      }
      const parsedResults = JSON.parse(storedResults);
      if (!Array.isArray(parsedResults) || parsedResults.length === 0) {
        navigate('/dashboard');
        return;
      }
      
      // Check if they are already analyzed
      const alreadyAnalyzed = parsedResults.some(m => m.risk_level && m.modification_type);
      if (alreadyAnalyzed) setAnalysisComplete(true);
      
      setMatches(parsedResults);
    } catch (e) {
      console.error("Failed to parse results", e);
      navigate('/dashboard');
    }
  }, [navigate]);

  const handleLogout = async () => {
    try {
      await signOut(auth);
      navigate('/');
    } catch (err) {
      console.error(err);
    }
  };

  const handleGeminiAnalysis = async () => {
    setIsAnalyzing(true);
    const originalTitle = localStorage.getItem('framelens_filename') || "Scanned Content";
    
    try {
      const res = await fetch(`${API_BASE}/results/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          original_title: originalTitle,
          matches: matches // includes source, id, similarity, etc.
        })
      });
      
      if (!res.ok) throw new Error("Analysis request failed");
      const data = await res.json();
      
      if (data.analyzed_matches) {
        setMatches(data.analyzed_matches);
        localStorage.setItem('framelens_results', JSON.stringify(data.analyzed_matches));
      }
      setAnalysisComplete(true);
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleScanAnother = () => {
    localStorage.removeItem('framelens_results');
    localStorage.removeItem('framelens_filename');
    navigate('/dashboard');
  };

  const getRiskColorClass = (level) => {
    if (!level) return 'risk-unknown';
    const l = level.toLowerCase();
    if (l === 'high') return 'risk-high';
    if (l === 'medium') return 'risk-medium';
    if (l === 'low') return 'risk-low';
    return 'risk-unknown';
  };

  const getConfidenceInfo = (similarity) => {
    if (similarity >= 0.85) return { label: 'HIGH CONFIDENCE', class: 'conf-high' };
    if (similarity >= 0.5) return { label: 'POSSIBLE MATCH', class: 'conf-possible' };
    return { label: 'LOW SIMILARITY', class: 'conf-low' };
  };

  if (!user || matches.length === 0) return null;

  return (
    <>
      <nav className="dashboard-navbar">
        <div className="container dashboard-nav-container">
          <div className="navbar-logo">FrameLens</div>
          
          <div className="nav-links">
            <Link to="/dashboard" className="nav-link">SCAN</Link>
            <Link to="/dataset" className="nav-link">PROTECT</Link>
          </div>

          <div className="dashboard-nav-right">
            <div className="user-avatar" title={user.email}>
              {user.email ? user.email.charAt(0).toUpperCase() : '?'}
            </div>
            <button onClick={handleLogout} className="logout-btn">LOGOUT</button>
          </div>
        </div>
      </nav>

      <main className="results-main">
        <div className="container">
          <div className="results-header-container">
            <div className="results-header-left">
              <span className="section-label" style={{ marginBottom: '1.5rem' }}>SCAN RESULTS</span>
              <h1 className="results-heading">
                {matches.some(m => m.source === 'Dataset') && matches.some(m => m.source === 'YouTube')
                  ? "Multi-Source Infringement Detected."
                  : matches.some(m => m.source === 'YouTube')
                    ? "Content Found Across Platforms."
                    : "Infringement Detected."}
              </h1>
              <p className="results-subtext">We found {matches.length} match(es) in total.</p>
              <p className="results-summary" style={{ color: '#666', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                {matches.filter(m => m.source === 'Dataset').length} match(es) from protected dataset · {matches.filter(m => m.source === 'YouTube').length} match(es) from YouTube
              </p>
            </div>
            <div className="results-header-right">
              <button className="btn-outline-clean" onClick={handleScanAnother}>SCAN ANOTHER</button>
            </div>
          </div>

          <div className="matches-grid">
            {matches.map((match, idx) => (
              <div key={idx} className="match-card">
                <div className="match-top-row">
                  {match.source === 'YouTube' ? (
                    <a href={match.url} target="_blank" rel="noopener noreferrer" className="match-title-link">
                      <h3 className="match-title">{match.title || match.id}</h3>
                    </a>
                  ) : (
                    <h3 className="match-title">{match.title || match.id}</h3>
                  )}
                  <div className="match-header-right">
                    <span className="match-similarity">{(match.similarity * 100).toFixed(2)}%</span>
                    <span className={`confidence-label ${getConfidenceInfo(match.similarity).class}`}>
                      {getConfidenceInfo(match.similarity).label}
                    </span>
                    <span className={`source-badge ${match.source === 'YouTube' ? 'badge-youtube' : 'badge-dataset'}`}>
                      {match.source}
                    </span>
                  </div>
                </div>
                <div className="match-source-row">
                  <span className="match-source">{match.source}</span>
                  {match.url && (
                    <a href={match.url} target="_blank" rel="noopener noreferrer" className="match-url">
                      {match.url.length > 50 ? match.url.substring(0, 50) + "..." : match.url}
                    </a>
                  )}
                </div>
                <div className="match-divider"></div>
                <div className="match-bottom-section">
                  <div className="info-col">
                    <span className="info-label">MODIFICATION TYPE</span>
                    <span className="info-value">{match.modification_type || 'Analyzing...'}</span>
                  </div>
                  <div className="info-col">
                    <span className="info-label">RISK LEVEL</span>
                    <span className={`info-value ${getRiskColorClass(match.risk_level)}`}>
                      {match.risk_level ? match.risk_level.toUpperCase() : 'Analyzing...'}
                    </span>
                  </div>
                  <div className="info-col">
                    <span className="info-label">RECOMMENDATION</span>
                    <span className="info-value">{match.recommendation || 'Analyzing...'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* ── Propagation Map ── */}
          <div className="pg-section">
            <span className="pg-section-label">PROPAGATION MAP</span>
            <h2 className="pg-section-heading">Content spread detected.</h2>
            <p className="pg-section-subtext">Visual map of where your content was found.</p>
            <PropagationGraph matches={matches} />
          </div>

          <button 
            className="btn-gemini-analysis" 
            onClick={handleGeminiAnalysis} 
            disabled={isAnalyzing || analysisComplete}
          >
            {isAnalyzing ? 'ANALYZING...' : (analysisComplete ? 'ANALYSIS COMPLETE' : 'RUN GEMINI ANALYSIS')}
          </button>

          <div className="bottom-actions">
            <button className="btn-scan-filled" onClick={handleScanAnother}>SCAN ANOTHER FILE</button>
            <button className="btn-home" onClick={() => { 
              localStorage.removeItem('framelens_results'); 
              localStorage.removeItem('framelens_filename');
              navigate('/'); 
            }}>GO HOME</button>
          </div>
        </div>
      </main>
    </>
  );
};

export default ResultsPage;
