import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  TextField,
  FormControlLabel,
  Switch,
  Typography,
  Paper,
  Grid,
  IconButton,
} from '@mui/material';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import { getSite, createSite, updateSite } from '../api';
import type { Site, SitePayload } from '../types';

interface SiteEditFormProps {
  siteId: string | null;
  onBack: () => void;
  onSave: () => void;
}

export default function SiteEditForm({ siteId, onBack, onSave }: SiteEditFormProps) {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState<SitePayload>({
    domain: '',
    ssl: false,
    ssl_provider: '',
    proxy_pass: '',
    proxy_headers: {},
  });
  const [proxyHeaders, setProxyHeaders] = useState<{ key: string; value: string }[]>([]);

  useEffect(() => {
    if (siteId) {
      loadSite();
    } else {
      setFormData({
        domain: '',
        ssl: false,
        ssl_provider: '',
        proxy_pass: '',
        proxy_headers: {},
      });
      setProxyHeaders([]);
    }
  }, [siteId]);

  const loadSite = async () => {
    if (!siteId) return;
    try {
      setLoading(true);
      const site = await getSite(siteId);
      setFormData({
        domain: site.domain,
        ssl: site.ssl,
        ssl_provider: site.ssl_provider,
        proxy_pass: site.proxy_pass,
        proxy_headers: site.proxy_headers,
      });
      setProxyHeaders(
        Object.entries(site.proxy_headers).map(([key, value]) => ({ key, value }))
      );
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to load site');
      onBack();
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      const headers: Record<string, string> = {};
      proxyHeaders.forEach(({ key, value }) => {
        if (key.trim()) {
          headers[key.trim()] = value.trim();
        }
      });

      const payload: SitePayload = {
        ...formData,
        proxy_headers: headers,
      };

      if (siteId) {
        await updateSite(siteId, payload);
      } else {
        await createSite(payload);
      }
      onSave();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save site');
    } finally {
      setSaving(false);
    }
  };

  const addProxyHeader = () => {
    setProxyHeaders([...proxyHeaders, { key: '', value: '' }]);
  };

  const removeProxyHeader = (index: number) => {
    setProxyHeaders(proxyHeaders.filter((_, i) => i !== index));
  };

  const updateProxyHeader = (index: number, field: 'key' | 'value', value: string) => {
    const updated = [...proxyHeaders];
    updated[index] = { ...updated[index], [field]: value };
    setProxyHeaders(updated);
  };

  if (loading) {
    return (
      <Container>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton onClick={onBack} sx={{ mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1">
          {siteId ? 'Edit Site' : 'Add Site'}
        </Typography>
      </Box>

      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Domain"
                value={formData.domain}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                required
              />
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.ssl}
                    onChange={(e) => setFormData({ ...formData, ssl: e.target.checked })}
                  />
                }
                label="Enable SSL"
              />
            </Grid>

            {formData.ssl && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="SSL Provider"
                  value={formData.ssl_provider}
                  onChange={(e) => setFormData({ ...formData, ssl_provider: e.target.value })}
                />
              </Grid>
            )}

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Proxy Pass"
                value={formData.proxy_pass}
                onChange={(e) => setFormData({ ...formData, proxy_pass: e.target.value })}
                placeholder="http://localhost:8080"
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Proxy Headers
              </Typography>
              {proxyHeaders.map((header, index) => (
                <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2 }}>
                  <TextField
                    label="Header Name"
                    value={header.key}
                    onChange={(e) => updateProxyHeader(index, 'key', e.target.value)}
                    size="small"
                  />
                  <TextField
                    label="Header Value"
                    value={header.value}
                    onChange={(e) => updateProxyHeader(index, 'value', e.target.value)}
                    size="small"
                    sx={{ flex: 1 }}
                  />
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={() => removeProxyHeader(index)}
                  >
                    Remove
                  </Button>
                </Box>
              ))}
              <Button variant="outlined" onClick={addProxyHeader}>
                Add Header
              </Button>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button variant="outlined" onClick={onBack} disabled={saving}>
                  Cancel
                </Button>
                <Button type="submit" variant="contained" disabled={saving}>
                  {saving ? 'Saving...' : 'Save'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
}

