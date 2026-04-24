import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword, sendPasswordResetEmail } from 'firebase/auth';
import { auth } from './firebase';
import './login.css';

const getFriendlyError = (errorCode) => {
  switch(errorCode) {
    case 'auth/invalid-credential':
    case 'auth/wrong-password':
    case 'auth/user-not-found':
      return 'Invalid email or password. Please try again.';
    case 'auth/email-already-in-use':
      return 'An account with this email already exists.';
    case 'auth/weak-password':
      return 'Password must be at least 6 characters.';
    case 'auth/invalid-email':
      return 'Please enter a valid email address.';
    case 'auth/too-many-requests':
      return 'Too many attempts. Please try again later.';
    default:
      return 'Something went wrong. Please try again.';
  }
};

const LoginPage = () => {
  const [activeTab, setActiveTab] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [isFading, setIsFading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleAuth = async (e) => {
    e.preventDefault();
    setError('');
    
    if (activeTab === 'signup') {
      if (password !== confirmPassword) {
        setError('Passwords do not match');
        return;
      }
      if (password.length < 6) {
        setError('Password must be at least 6 characters');
        return;
      }
    }

    setLoading(true);
    try {
      if (activeTab === 'login') {
        await signInWithEmailAndPassword(auth, email, password);
      } else {
        await createUserWithEmailAndPassword(auth, email, password);
      }
      navigate('/dashboard');
    } catch (err) {
      setError(getFriendlyError(err.code));
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!email) {
      setError('Enter your email first');
      return;
    }
    try {
      await sendPasswordResetEmail(auth, email);
      setSuccess('Password reset email sent!');
    } catch (err) {
      setError(getFriendlyError(err.code));
    }
  };

  const switchTab = (tab) => {
    if (tab === activeTab) return;
    setIsFading(true);
    setTimeout(() => {
      setActiveTab(tab);
      setError('');
      setSuccess('');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setShowPassword(false);
      setIsFading(false);
    }, 200);
  };

  return (
    <div className="login-page">
      <div className="login-left">
        <div className="login-logo">FrameLens</div>
        <div className="login-left-content">
          <h1 className="login-headline">Protect what's yours.</h1>
          <ul className="login-features">
            <li><span className="feature-dot"></span> AI-powered video & image detection</li>
            <li><span className="feature-dot"></span> Two-stage CLIP + pHash pipeline</li>
            <li><span className="feature-dot"></span> Gemini risk analysis reports</li>
          </ul>
        </div>
      </div>
      
      <div className="login-right">
        <button className="back-link" onClick={() => navigate('/')}>&larr; Back to Home</button>
        
        <div className="auth-container">
          <div className="auth-header">
            <h2 className="auth-title">
              {activeTab === 'login' ? 'Welcome back' : 'Create account'}
            </h2>
            <p className="auth-subtitle">
              {activeTab === 'login' 
                ? 'Sign in to your FrameLens account' 
                : 'Start protecting your content'}
            </p>
          </div>

          <div className="auth-tabs">
            <button 
              type="button"
              className={`auth-tab ${activeTab === 'login' ? 'active' : ''}`}
              onClick={() => switchTab('login')}
            >
              LOGIN
            </button>
            <button 
              type="button"
              className={`auth-tab ${activeTab === 'signup' ? 'active' : ''}`}
              onClick={() => switchTab('signup')}
            >
              SIGN UP
            </button>
          </div>
          
          <form className="auth-form" onSubmit={handleAuth}>
            <div className={`form-fields-wrapper ${isFading ? 'fading' : ''}`}>
            <input 
              type="email" 
              className="form-input" 
              placeholder="Email Address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            
            <div className="password-input-wrapper">
              <input 
                type={showPassword ? "text" : "password"} 
                className="form-input password-input" 
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button 
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={16} strokeWidth={1.5} /> : <Eye size={16} strokeWidth={1.5} />}
              </button>
            </div>
            
            {activeTab === 'signup' && (
              <input 
                type="password" 
                className="form-input" 
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            )}
            
            {activeTab === 'login' && (
              <div className="forgot-password-container">
                <a href="#" className="forgot-password" onClick={handleResetPassword}>Forgot password?</a>
              </div>
            )}
            
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'LOADING...' : (activeTab === 'login' ? 'LOGIN' : 'CREATE ACCOUNT')}
            </button>
            
            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
