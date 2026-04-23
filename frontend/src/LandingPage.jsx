import React from 'react';
import { Upload, Search, ShieldAlert, Fingerprint, Eye, Sparkles } from 'lucide-react';
import { FaXTwitter, FaGithub, FaLinkedinIn } from 'react-icons/fa6';
import './landing.css';

const LandingPage = () => {
  return (
    <>
      <nav className="navbar">
        <div className="container">
          <a href="/" className="navbar-logo">FrameLens</a>
          <div className="navbar-links">
            <a href="#login" className="nav-link">Login</a>
            <a href="#get-started" className="nav-link">Get Started</a>
          </div>
        </div>
      </nav>

      <main>
        <section className="hero">
          <div className="hero-bg-noise">
            <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
              <filter id="noiseFilter">
                <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch" />
              </filter>
              <rect width="100%" height="100%" filter="url(#noiseFilter)" />
            </svg>
          </div>
          <div className="container hero-container">
            <h1 className="hero-title">Your Content.<br />Protected by AI.</h1>
            <p className="hero-subtitle">
              FrameLens automatically finds stolen, cropped, or reposted versions of your videos and images across the web — before you even know they exist.
            </p>
            <div className="hero-actions">
              <a href="#get-started" className="btn btn-text-primary">Get Started</a>
              <a href="#how-it-works" className="btn btn-outline">See How It Works</a>
            </div>
          </div>
        </section>

        <section className="stats">
          <div className="container">
            <div className="stats-grid">
              <div className="stat-block">
                <div className="stat-number">2-Stage</div>
                <div className="stat-label">AI PIPELINE</div>
                <div className="stat-subtitle">pHash + CLIP</div>
              </div>
              <div className="stat-block">
                <div className="stat-number">512-DIM</div>
                <div className="stat-label">EMBEDDINGS</div>
                <div className="stat-subtitle">CLIP ViT-B/32</div>
              </div>
              <div className="stat-block">
                <div className="stat-number">Gemini</div>
                <div className="stat-label">RISK ANALYSIS</div>
                <div className="stat-subtitle">AI Powered</div>
              </div>
              <div className="stat-block">
                <div className="stat-number">Instant</div>
                <div className="stat-label">REPORTS</div>
                <div className="stat-subtitle">Per Upload</div>
              </div>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="how-it-works">
          <div className="container">
            <span className="section-label">PROCESS</span>
            <h2 className="section-heading">Three steps to protection.</h2>
            <div className="steps-list">
              <div className="step-row">
                <div className="step-num-col">01</div>
                <div className="step-title-col">Upload your video or image</div>
                <div className="step-desc-col">Securely upload your digital asset. FrameLens extracts individual frames to build a complete visual profile for matching.</div>
              </div>
              <div className="step-row">
                <div className="step-num-col">02</div>
                <div className="step-title-col">AI scans and matches against your protected dataset</div>
                <div className="step-desc-col">Our two-stage pipeline filters candidates with perceptual hashing, then verifies exact matches using CLIP deep embeddings.</div>
              </div>
              <div className="step-row">
                <div className="step-num-col">03</div>
                <div className="step-title-col">Get a full infringement report with risk level</div>
                <div className="step-desc-col">Gemini AI analyzes any detected modifications (like crops or filters) and generates an actionable report with a precise risk level.</div>
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="features">
          <div className="container">
            <span className="section-label">DETECTION ENGINE</span>
            <h2 className="section-heading">Core capabilities.</h2>
            <div className="features-grid">
              <div className="feature-item">
                <h3 className="feature-item-title">Perceptual Hash Matching</h3>
                <p className="feature-item-text">Fast first-pass detection using pHash Hamming distance filtering</p>
              </div>
              <div className="feature-item">
                <h3 className="feature-item-title">CLIP Deep Verification</h3>
                <p className="feature-item-text">512-dimension visual embeddings for precise similarity matching</p>
              </div>
              <div className="feature-item">
                <h3 className="feature-item-title">Gemini Risk Analysis</h3>
                <p className="feature-item-text">AI-generated modification type, risk level, and recommended action</p>
              </div>
            </div>
          </div>
        </section>

        <section className="cta-section">
          <div className="cta-bg-text">FRAMELENS</div>
          <div className="container">
            <h2 className="cta-title">Your content is being stolen right now.</h2>
            <p className="cta-subtitle">Start detecting it in minutes.</p>
            <a href="#get-started" className="btn-cta">Get Started</a>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="container">
          <div className="footer-top">
            <div className="footer-left">
              <a href="/" className="footer-logo">FrameLens</a>
              <p className="footer-tagline">AI-powered copyright protection for digital creators.</p>
            </div>
            
            <div className="footer-right">
              <div className="footer-col">
                <h4 className="footer-col-title">PRODUCT</h4>
                <a href="#features" className="footer-link">Features</a>
                <a href="#how-it-works" className="footer-link">How It Works</a>
                <a href="#get-started" className="footer-link">Get Started</a>
              </div>
              <div className="footer-col">
                <h4 className="footer-col-title">COMPANY</h4>
                <a href="#about" className="footer-link">About</a>
                <a href="#contact" className="footer-link">Contact</a>
              </div>
              <div className="footer-col">
                <h4 className="footer-col-title">LEGAL</h4>
                <a href="#privacy" className="footer-link">Privacy Policy</a>
                <a href="#terms" className="footer-link">Terms of Service</a>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <span>&copy; 2025 FrameLens. All rights reserved.</span>
            <div className="footer-bottom-socials">
              <a href="#" className="social-link"><FaXTwitter size={18} /></a>
              <a href="#" className="social-link"><FaGithub size={18} /></a>
              <a href="#" className="social-link"><FaLinkedinIn size={18} /></a>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
};

export default LandingPage;
