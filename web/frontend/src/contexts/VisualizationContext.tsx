import React, { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

interface VisualizationContextType {
  visualizationUrl: string;
  setVisualizationUrl: (url: string) => void;
  visualizationType: 'band' | 'manipulation' | 'none';
  setVisualizationType: (type: 'band' | 'manipulation' | 'none') => void;
  selectedBand: string;
  setSelectedBand: (band: string) => void;
}

const VisualizationContext = createContext<VisualizationContextType | null>(null);

export const useVisualization = () => {
  const context = useContext(VisualizationContext);
  if (!context) {
    throw new Error('useVisualization must be used within a VisualizationProvider');
  }
  return context;
};

interface VisualizationProviderProps {
  children: ReactNode;
}

export const VisualizationProvider: React.FC<VisualizationProviderProps> = ({ children }) => {
  const [visualizationUrl, setVisualizationUrl] = useState<string>('');
  const [visualizationType, setVisualizationType] = useState<'band' | 'manipulation' | 'none'>('none');
  const [selectedBand, setSelectedBand] = useState<string>('');

  return (
    <VisualizationContext.Provider
      value={{
        visualizationUrl,
        setVisualizationUrl,
        visualizationType,
        setVisualizationType,
        selectedBand,
        setSelectedBand
      }}
    >
      {children}
    </VisualizationContext.Provider>
  );
}; 