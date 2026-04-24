import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from './firebase';
import { onAuthStateChanged, signOut } from 'firebase/auth';
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
    try {
      const res = await fetch('http://localhost:8000/results/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          original_title: "Scanned Content",
          matches: matches
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

  if (!user || matches.length === 0) return null;

  return (
    <>
      <nav className="dashboard-navbar">
        <div className="container dashboard-nav-container">
          <div className="navbar-logo">FrameLens</div>
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
              <h1 className="results-heading">Infringement Detected.</h1>
              <p className="results-subtext">We found {matches.length} match(es) against your protected dataset.</p>
            </div>
            <div className="results-header-right">
              <button className="btn-outline-clean" onClick={handleScanAnother}>SCAN ANOTHER</button>
            </div>
          </div>

          <div className="matches-grid">
            {matches.map((match, idx) => (
              <div key={idx} className="match-card">
                <div className="match-top-row">
                  <h3 className="match-title">{match.title || match.id}</h3>
                  <span className="match-similarity">{(match.similarity * 100).toFixed(2)}%</span>
                </div>
                <div className="match-source-row">
                  <span className="match-source">{match.source}</span>
                  {match.url && <a href={match.url} target="_blank" rel="noopener noreferrer" className="match-url">{match.url}</a>}
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

          <button 
            className="btn-gemini-analysis" 
            onClick={handleGeminiAnalysis} 
            disabled={isAnalyzing || analysisComplete}
          >
            {isAnalyzing ? 'ANALYZING...' : (analysisComplete ? 'ANALYSIS COMPLETE' : 'RUN GEMINI ANALYSIS')}
          </button>

          <div className="bottom-actions">
            <button className="btn-scan-filled" onClick={handleScanAnother}>SCAN ANOTHER FILE</button>
            <button className="btn-home" onClick={() => { localStorage.removeItem('framelens_results'); navigate('/'); }}>GO HOME</button>
          </div>
        </div>
      </main>
    </>
  );
};

export default ResultsPage;
