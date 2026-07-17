import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('vaani_token'));
  const [role, setRole] = useState(localStorage.getItem('vaani_role'));

  useEffect(() => {
    if (token) localStorage.setItem('vaani_token', token);
    else localStorage.removeItem('vaani_token');
    
    if (role) localStorage.setItem('vaani_role', role);
    else localStorage.removeItem('vaani_role');
  }, [token, role]);

  const login = (newToken, newRole) => {
    setToken(newToken);
    setRole(newRole);
  };

  const logout = () => {
    setToken(null);
    setRole(null);
  };

  return (
    <AuthContext.Provider value={{ token, role, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
