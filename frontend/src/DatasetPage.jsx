import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, Upload, X, Trash2 } from 'lucide-react';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from './firebase';
import './upload.css';
import './dataset.css';

const DatasetPage = () => {
  const [user, setUser] = useState(null);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // Form State
  const [formData, setFormData] = useState({
    title: '',
    source: '',
    url: ''
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (!currentUser) {
        navigate('/login');
      } else {
        setUser(currentUser);
        fetchAssets();
      }
    });
    return () => unsubscribe();
  }, [navigate]);

  const fetchAssets = async () => {
    try {
      const res = await fetch('http://localhost:8000/dataset/');
      if (res.ok) {
        const data = await res.json();
        setAssets(Array.isArray(data) ? data : data.items || data.dataset || []);
      }
    } catch (err) {
      console.error("Failed to fetch assets", err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
      navigate('/');
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to remove this asset from protection?")) return;
    try {
      const res = await fetch(`http://localhost:8000/dataset/${id}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        fetchAssets();
      }
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > 100 * 1024 * 1024) {
        setError('File exceeds 100MB limit.');
        return;
      }
      setSelectedFile(file);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile || !formData.title || !formData.source) {
      setError('Please fill all fields and select a file.');
      return;
    }

    setIsProcessing(true);
    setError('');

    try {
      // 1. Upload to get embeddings
      const isVideo = selectedFile.type.startsWith('video/');
      const uploadUrl = isVideo ? 'http://localhost:8000/upload/video' : 'http://localhost:8000/upload/image';
      
      const uploadFormData = new FormData();
      uploadFormData.append('file', selectedFile);

      const uploadRes = await fetch(uploadUrl, {
        method: 'POST',
        body: uploadFormData
      });

      if (!uploadRes.ok) throw new Error('File upload/processing failed');
      const uploadData = await uploadRes.json();
      
      if (!uploadData.frames || uploadData.frames.length === 0) {
        throw new Error('Failed to extract features from file');
      }

      const frame = uploadData.frames[0];

      // 2. Add to dataset
      const assetPayload = {
        id: Date.now().toString(),
        title: formData.title,
        source: formData.source,
        url: formData.url || 'Internal Source',
        phash: frame.phash,
        embedding: frame.embedding
      };

      const addRes = await fetch('http://localhost:8000/dataset/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(assetPayload)
      });

      if (!addRes.ok) throw new Error('Failed to register asset in dataset');

      // Success
      setShowModal(false);
      setFormData({ title: '', source: '', url: '' });
      setSelectedFile(null);
      fetchAssets();
    } catch (err) {
      console.error(err);
      setError(err.message || 'Registration failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  if (!user) return null;

  return (
    <div className="dataset-page">
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button className="btn-close-modal" onClick={() => setShowModal(false)}><X /></button>
            <h2 className="modal-title">Register New Asset</h2>
            
            <form className="modal-form" onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Title</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. Movie Trailer Final"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Source Name</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. Studio X"
                  value={formData.source}
                  onChange={(e) => setFormData({...formData, source: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Source URL</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. https://youtube.com/..."
                  value={formData.url}
                  onChange={(e) => setFormData({...formData, url: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Media File</label>
                <div 
                  className={`modal-dropzone ${selectedFile ? 'has-file' : ''}`}
                  onClick={() => fileInputRef.current.click()}
                >
                  {selectedFile ? (
                    <div>
                      <p style={{ fontWeight: 700, color: '#FF3D00' }}>{selectedFile.name}</p>
                      <p style={{ fontSize: '0.75rem', color: '#888' }}>{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  ) : (
                    <>
                      <Upload size={24} style={{ marginBottom: '0.5rem', color: '#444' }} />
                      <p style={{ fontSize: '0.875rem', color: '#888' }}>Click to select media</p>
                    </>
                  )}
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    style={{ display: 'none' }} 
                    onChange={handleFileChange}
                    accept="image/*,video/*"
                  />
                </div>
              </div>

              {error && <div className="modal-error">{error}</div>}

              <button 
                type="submit" 
                className="btn-register-asset"
                disabled={isProcessing}
              >
                {isProcessing ? 'PROCESSING...' : 'REGISTER ASSET'}
              </button>
            </form>
          </div>
        </div>
      )}

      <nav className="dashboard-navbar">
        <div className="container dashboard-nav-container">
          <div className="navbar-logo">FrameLens</div>
          
          <div className="nav-links">
            <Link to="/dashboard" className="nav-link">SCAN</Link>
            <Link to="/dataset" className="nav-link active">PROTECT</Link>
          </div>

          <div className="dashboard-nav-right">
            <div className="user-avatar" title={user.email}>
              {user.email ? user.email.charAt(0).toUpperCase() : '?'}
            </div>
            <button onClick={handleLogout} className="logout-btn">LOGOUT</button>
          </div>
        </div>
      </nav>

      <main className="dataset-main">
        <div className="container">
          <div className="dataset-header-container">
            <div className="dataset-header-left">
              <span className="section-label" style={{ marginBottom: '1.5rem', color: '#FF3D00' }}>PROTECTED ASSETS</span>
              <h1 className="dataset-heading">Your registered content.</h1>
              <p className="dataset-subtext">Add your original media to protect it from unauthorized use.</p>
            </div>
            <div className="dataset-header-right">
              <button className="btn-add-asset" onClick={() => setShowModal(true)}>ADD ASSET</button>
            </div>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '4rem', color: '#444' }}>Loading dataset...</div>
          ) : assets.length === 0 ? (
            <div className="empty-state">
              <Shield size={48} className="empty-icon" />
              <h2 className="empty-heading">No protected assets yet.</h2>
              <p className="empty-subtext">Add your first asset to start protecting your content.</p>
              <button className="btn-add-asset" onClick={() => setShowModal(true)}>ADD FIRST ASSET</button>
            </div>
          ) : (
            <div className="asset-grid">
              {(assets || []).map((asset) => (
                <div key={asset.id} className="asset-card">
                  <h3 className="asset-title">{asset.title}</h3>
                  <span className="asset-source">{asset.source}</span>
                  <a href={asset.url} target="_blank" rel="noopener noreferrer" className="asset-url">
                    {asset.url}
                  </a>
                  <div className="asset-card-bottom">
                    <span />
                    <button className="btn-delete-asset" onClick={() => handleDelete(asset.id)}>
                      <Trash2 size={14} style={{ marginRight: '4px' }} /> DELETE
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DatasetPage;
