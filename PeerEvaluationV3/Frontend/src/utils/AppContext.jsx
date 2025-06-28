import { createContext, useState } from 'react';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [refreshApp, setRefreshApp] = useState(false);

  return (
    <AppContext.Provider value={{ refreshApp, setRefreshApp }}>
      {children}
    </AppContext.Provider>
  );
};