import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './LandingPage';
import LoginPage from './LoginPage';
import UploadPage from './UploadPage';
import ResultsPage from './ResultsPage';
import DatasetPage from './DatasetPage';
import './landing.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<UploadPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/dataset" element={<DatasetPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
