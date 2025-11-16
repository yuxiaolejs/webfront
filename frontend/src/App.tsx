import React, { useState } from 'react';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import SiteList from './components/SiteList';
import SiteEditForm from './components/SiteEditForm';
import type { Site } from './types';

const theme = createTheme({
  palette: {
    mode: 'light',
  },
});

type View = 'list' | 'edit' | 'add';

export default function App() {
  const [view, setView] = useState<View>('list');
  const [selectedSite, setSelectedSite] = useState<Site | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleEdit = (site: Site) => {
    setSelectedSite(site);
    setView('edit');
  };

  const handleAdd = () => {
    setSelectedSite(null);
    setView('add');
  };

  const handleBack = () => {
    setView('list');
    setSelectedSite(null);
  };

  const handleSave = () => {
    setView('list');
    setSelectedSite(null);
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {view === 'list' && (
        <SiteList
          onEdit={handleEdit}
          onAdd={handleAdd}
          refreshTrigger={refreshTrigger}
        />
      )}
      {(view === 'edit' || view === 'add') && (
        <SiteEditForm
          siteId={selectedSite?.id || null}
          onBack={handleBack}
          onSave={handleSave}
        />
      )}
    </ThemeProvider>
  );
}

