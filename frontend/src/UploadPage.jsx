import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, CheckCircle2 } from 'lucide-react';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from './firebase';
import './upload.css';

const SCAN_MESSAGES = [
  "Extracting frames from your content...",
  "Generating CLIP embeddings...",
  "Matching against protected dataset...",
  "Running Gemini risk analysis..."
];

const UploadPage = () => {
  const [user, setUser] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanStatusIndex, setScanStatusIndex] = useState(0);
  const [isClean, setIsClean] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const abortRef = useRef(null);

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
    let interval;
    if (isScanning) {
      setScanStatusIndex(0);
      interval = setInterval(() => {
        setScanStatusIndex((prev) => (prev + 1) % SCAN_MESSAGES.length);
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [isScanning]);

  const handleLogout = async () => {
    try {
      await signOut(auth);
      navigate('/');
    } catch (err) {
      console.error(err);
    }
  };

  const processFile = (selectedFile) => {
    setError('');
    if (!selectedFile) return;
    
    // Size check
    if (selectedFile.size > 100 * 1024 * 1024) {
      setError('File exceeds 100MB limit.');
      return;
    }
    
    // Type check
    const validTypes = ['video/mp4', 'video/quicktime', 'image/jpeg', 'image/png'];
    if (!validTypes.includes(selectedFile.type)) {
      setError('Unsupported file type. Please upload MP4, MOV, JPG, or PNG.');
      return;
    }

    setFile(selectedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    if (isScanning) return;
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    if (isScanning) return;
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (isScanning) return;
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleScan = async () => {
    if (!file || isScanning) return;
    setIsScanning(true);
    setError('');
    
    try {
      const abortController = new AbortController();
      abortRef.current = abortController;

      // Determine endpoint based on file type
      const isVideo = file.type.startsWith('video/');
      const uploadUrl = isVideo ? 'http://localhost:8000/upload/video' : 'http://localhost:8000/upload/image';
      
      const formData = new FormData();
      formData.append('file', file);

      // Upload and get frames
      const uploadRes = await fetch(uploadUrl, {
        method: 'POST',
        body: formData,
        signal: abortController.signal
      });
      
      if (!uploadRes.ok) throw new Error('Upload failed');
      const uploadData = await uploadRes.json();
      
      if (!uploadData.frames || uploadData.frames.length === 0) {
        throw new Error('Failed to extract frames');
      }

      // Compare frames
      const compareRes = await fetch('http://localhost:8000/compare/auto', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query_frames: uploadData.frames }),
        signal: abortController.signal
      });
      
      if (!compareRes.ok) throw new Error('Comparison failed');
      const compareData = await compareRes.json();
      
      if (compareData.matches && compareData.matches.length > 0) {
        localStorage.setItem('framelens_results', JSON.stringify(compareData.matches));
        setIsScanning(false);
        navigate('/results');
      } else {
        setIsScanning(false);
        setIsClean(true);
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        setIsScanning(false);
        return;
      }
      console.error(err);
      setIsScanning(false);
      setError('Scan failed. Make sure the backend is running and try again.');
    }
  };

  if (!user) return null;

  return (
    <>
      {isScanning && (
        <div className="scanning-overlay">
          <div className="scan-line"></div>
          <div className="scanning-content">
            <h1 className="scanning-title">SCANNING</h1>
            <div className="scanning-status">{SCAN_MESSAGES[scanStatusIndex]}</div>
            <div className="scanning-estimate">This may take 20–40 seconds depending on file size</div>
          </div>
          <button 
            className="btn-cancel-scan" 
            onClick={() => { if(abortRef.current) abortRef.current.abort(); }}
          >
            CANCEL SCAN
          </button>
        </div>
      )}

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

      <main className="dashboard-main">
        <div className="container upload-container">
          {!isClean ? (
            <>
              <span className="section-label" style={{ marginBottom: '1.5rem' }}>SCAN CONTENT</span>
              <h1 className="upload-heading">Upload to detect infringement.</h1>
              <p className="upload-subtext" style={{ marginBottom: '3rem' }}>Drop your video or image and let FrameLens scan it against your protected dataset.</p>

              <div 
                className={`drop-zone ${isDragging ? 'dragging' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => !isScanning && !file && fileInputRef.current?.click()}
              >
                {!file ? (
                  <div className="drop-zone-content">
                    <Upload size={48} className="upload-icon" />
                    <h3 className="drop-zone-text">Drag & drop your file here</h3>
                    <p className="drop-zone-subtext">Supported: MP4, MOV, JPG, PNG — Max 100MB</p>
                  </div>
                ) : (
                  <div className="file-selected">
                    <h3 className="file-name">{file.name}</h3>
                    <p className="file-size">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                    <button className="btn-scan" onClick={(e) => { e.stopPropagation(); handleScan(); }} disabled={isScanning}>SCAN NOW</button>
                    <button className="btn-clear" onClick={(e) => { e.stopPropagation(); setFile(null); }} disabled={isScanning}>Clear</button>
                  </div>
                )}
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  style={{ display: 'none' }} 
                  accept=".mp4,.mov,.jpg,.jpeg,.png"
                  onChange={(e) => {
                    if (e.target.files && e.target.files.length > 0) {
                      processFile(e.target.files[0]);
                    }
                  }}
                />
              </div>
              
              {error && <div className="upload-error">{error}</div>}
            </>
          ) : (
            <div className="clean-state">
              <CheckCircle2 size={64} className="clean-icon" />
              <h2 className="clean-heading">You're safe.</h2>
              <p className="clean-subtext">No infringement detected. Your content appears to be original.</p>
              <div className="clean-actions">
                <button className="btn-outline-clean" onClick={() => { setIsClean(false); setFile(null); }}>SCAN ANOTHER</button>
                <button className="btn-home" onClick={() => navigate('/')}>GO HOME</button>
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  );
};

export default UploadPage;
