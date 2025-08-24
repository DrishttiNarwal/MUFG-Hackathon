import React, { createContext, useContext, useState, useEffect } from 'react';

const CurrencyContext = createContext();

export const CURRENCY_CONFIG = {
  IN: {
    symbol: '₹',
    code: 'INR',
    name: 'Indian Rupee'
  },
  AU: {
    symbol: '$',
    code: 'AUD',
    name: 'Australian Dollar'
  }
};

export const CurrencyProvider = ({ children }) => {
  const [currency, setCurrency] = useState(() => {
    // Try to get saved currency from localStorage
    const savedCurrency = localStorage.getItem('selectedCountry');
    const savedInsuranceType = localStorage.getItem('insuranceType');
    
    // If it's Australia, always return AUD
    if (savedCurrency === 'AU') {
      return CURRENCY_CONFIG.AU;
    }
    
    // For India return INR
    return CURRENCY_CONFIG.IN;
  });

  const updateCurrency = (countryCode) => {
    if (countryCode === 'AU') {
      setCurrency(CURRENCY_CONFIG.AU);
      localStorage.setItem('selectedCountry', 'AU');
    } else {
      setCurrency(CURRENCY_CONFIG.IN);
      localStorage.setItem('selectedCountry', 'IN');
    }
  };

  return (
    <CurrencyContext.Provider value={{ currency, updateCurrency }}>
      {children}
    </CurrencyContext.Provider>
  );
};

export const useCurrency = () => {
  const context = useContext(CurrencyContext);
  if (!context) {
    throw new Error('useCurrency must be used within a CurrencyProvider');
  }
  return context;
};
