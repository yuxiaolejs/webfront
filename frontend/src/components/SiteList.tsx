import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Paper,
  Chip,
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { listSites, deleteSite, retryCert } from '../api';
import type { Site } from '../types';

interface SiteListProps {
  onEdit: (site: Site) => void;
  onAdd: () => void;
  refreshTrigger: number;
}

export default function SiteList({ onEdit, onAdd, refreshTrigger }: SiteListProps) {
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSites = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listSites();
      setSites(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sites');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSites();
  }, [refreshTrigger]);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this site?')) {
      return;
    }
    try {
      await deleteSite(id);
      await loadSites();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete site');
    }
  };

  if (loading) {
    return (
      <Container>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Typography color="error">{error}</Typography>
      </Container>
    );
  }

  const retryCertHandler = async (site: Site) => {
    try {
      await retryCert(site.id);
      alert('Certificate retry task created successfully');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create certificate retry task');
    }
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Sites
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={onAdd}>
          Add Site
        </Button>
      </Box>

      {sites.length === 0 ? (
        <Card>
          <CardContent>
            <Typography>No sites configured. Click "Add Site" to create one.</Typography>
          </CardContent>
        </Card>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Domain</TableCell>
                <TableCell>SSL</TableCell>
                <TableCell>SSL Provider</TableCell>
                <TableCell>Proxy Pass</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sites.map((site) => (
                <TableRow key={site.id}>
                  <TableCell>{site.domain}</TableCell>
                  <TableCell>
                    <Chip
                      label={site.ssl ? 'Enabled' : 'Disabled'}
                      color={site.ssl ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{site.ssl_provider || '-'}</TableCell>
                  <TableCell>{site.proxy_pass || '-'}</TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => onEdit(site)}
                      aria-label="edit"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(site.id)}
                      aria-label="delete"
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                    {site.ssl && (
                      <Button
                        size="small"
                        onClick={() => retryCertHandler(site)}
                        aria-label="retry cert"
                        sx={{ ml: 1 }}
                      >
                        Retry Cert
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
}

