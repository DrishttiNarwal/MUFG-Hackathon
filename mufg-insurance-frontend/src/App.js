import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import theme from './theme';
import { CurrencyProvider } from './context/CurrencyContext';

// Pages
import LandingPage from './pages/LandingPage';
import CountrySelection from './pages/CountrySelection';
import InsuranceSelection from './pages/InsuranceSelection';
import InsuranceForm from './components/forms/InsuranceForm';
import ResultsPage from './pages/ResultsPage';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <CurrencyProvider>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/select-country" element={<CountrySelection />} />
            <Route path="/insurance-selection/:countryCode" element={<InsuranceSelection />} />
            <Route path="/insurance-form/:countryCode/:insuranceType" element={<InsuranceForm />} />
            <Route path="/results" element={<ResultsPage />} />
          </Routes>
        </CurrencyProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;
