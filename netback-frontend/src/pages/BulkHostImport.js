import { useEffect, useState, useCallback, useMemo } from "react";
import {
  getClassificationRules,
  classifyFromZabbix,
  classifyFromCSV,
  saveClassifiedHosts,
} from "../api";
import {
  Box, Button, Typography, Select, MenuItem, InputLabel, FormControl,
  Snackbar, Alert, CircularProgress, TextField, Paper, Chip, IconButton
} from "@mui/material";
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';

import HostsTable from "../components/BulkHostImport/HostsTable";
import ImportControls from "../components/BulkHostImport/ImportControls";

const BulkHostImport = () => {
  const [rules, setRules] = useState([]);
  const [selectedRule, setSelectedRule] = useState("");
  const [hosts, setHosts] = useState([]);
  const [selectedHosts, setSelectedHosts] = useState([]);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "info" });

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState("");
  
  // Estados para filtros avanzados
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    manufacturer: "",
    deviceType: "",
    area: "",
    status: "all" // all, complete, incomplete
  });

  useEffect(() => {
    const fetchRules = async () => {
      const data = await getClassificationRules();
      if (data) setRules(data);
    };
    fetchRules();
  }, []);

  // Obtener valores únicos para los filtros
  const filterOptions = useMemo(() => {
    if (!hosts || hosts.length === 0) return { manufacturers: [], deviceTypes: [], areas: [] };
    
    return {
      manufacturers: [...new Set(hosts.map(h => h.manufacturer?.name).filter(Boolean))].sort(),
      deviceTypes: [...new Set(hosts.map(h => h.deviceType?.name).filter(Boolean))].sort(),
      areas: [...new Set(hosts.map(h => h.area?.name).filter(Boolean))].sort()
    };
  }, [hosts]);

  // Filtrar hosts
  const filteredHosts = useMemo(() => {
    if (!hosts || hosts.length === 0) return [];
    
    return hosts.filter(host => {
      // Búsqueda por texto
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = 
        host.hostname?.toLowerCase().includes(searchLower) ||
        host.ip?.toLowerCase().includes(searchLower) ||
        host.model?.toLowerCase().includes(searchLower) ||
        host.classification?.model?.toLowerCase().includes(searchLower);

      // Filtros avanzados
      const matchesManufacturer = !filters.manufacturer || 
        host.manufacturer?.name === filters.manufacturer;
      
      const matchesDeviceType = !filters.deviceType || 
        host.deviceType?.name === filters.deviceType;
      
      const matchesArea = !filters.area || 
        host.area?.name === filters.area;
      
      const matchesStatus = 
        filters.status === "all" ||
        (filters.status === "complete" && (!host.missing || host.missing.length === 0)) ||
        (filters.status === "incomplete" && host.missing && host.missing.length > 0);

      return matchesSearch && matchesManufacturer && matchesDeviceType && 
             matchesArea && matchesStatus;
    });
  }, [hosts, searchTerm, filters]);

  // Hosts paginados
  const paginatedHosts = useMemo(() => {
    const startIndex = page * rowsPerPage;
    return filteredHosts.slice(startIndex, startIndex + rowsPerPage);
  }, [filteredHosts, page, rowsPerPage]);

  const handleZabbixImport = async () => {
    if (!selectedRule) return;
    setLoading(true);
    try {
      const result = await classifyFromZabbix(selectedRule);
      if (result) {
        setHosts(result);
        setSelectedHosts([]);
        setPage(0);
        setSnackbar({ 
          open: true, 
          message: `✅ ${result.length} hosts importados desde Zabbix`, 
          severity: "success" 
        });
      }
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: "❌ Error al importar desde Zabbix", 
        severity: "error" 
      });
    }
    setLoading(false);
  };

  const handleCSVImport = async () => {
    if (!selectedRule || !file) return;
    const formData = new FormData();
    formData.append("file", file);
    formData.append("ruleSetId", selectedRule);
    setLoading(true);
    try {
      const result = await classifyFromCSV(formData);
      if (result) {
        setHosts(result);
        setSelectedHosts([]);
        setPage(0);
        setSnackbar({ 
          open: true, 
          message: `✅ ${result.length} hosts importados desde CSV`, 
          severity: "success" 
        });
      }
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: "❌ Error al importar CSV", 
        severity: "error" 
      });
    }
    setLoading(false);
  };

  const handleCheckboxToggle = useCallback((hostname) => {
    setSelectedHosts((prev) =>
      prev.includes(hostname)
        ? prev.filter((h) => h !== hostname)
        : [...prev, hostname]
    );
  }, []);

  // Seleccionar todos en la página actual
  const handleSelectAllCurrentPage = useCallback(() => {
    const currentPageHostnames = paginatedHosts.map(h => h.hostname);
    const allSelected = currentPageHostnames.every(hostname => 
      selectedHosts.includes(hostname)
    );

    if (allSelected) {
      // Deseleccionar todos de la página actual
      setSelectedHosts(prev => 
        prev.filter(hostname => !currentPageHostnames.includes(hostname))
      );
    } else {
      // Seleccionar todos de la página actual
      setSelectedHosts(prev => {
        const newSelection = [...prev];
        currentPageHostnames.forEach(hostname => {
          if (!newSelection.includes(hostname)) {
            newSelection.push(hostname);
          }
        });
        return newSelection;
      });
    }
  }, [paginatedHosts, selectedHosts]);

  // Seleccionar todos los filtrados
  const handleSelectAllFiltered = useCallback(() => {
    const allFilteredHostnames = filteredHosts.map(h => h.hostname);
    const allSelected = allFilteredHostnames.every(hostname => 
      selectedHosts.includes(hostname)
    );

    if (allSelected) {
      // Deseleccionar todos los filtrados
      setSelectedHosts(prev => 
        prev.filter(hostname => !allFilteredHostnames.includes(hostname))
      );
    } else {
      // Seleccionar todos los filtrados
      setSelectedHosts(allFilteredHostnames);
    }
    
    setSnackbar({ 
      open: true, 
      message: allSelected 
        ? `✅ ${allFilteredHostnames.length} hosts deseleccionados`
        : `✅ ${allFilteredHostnames.length} hosts seleccionados`, 
      severity: "info" 
    });
  }, [filteredHosts, selectedHosts]);

  const handleClearFilters = () => {
    setSearchTerm("");
    setFilters({
      manufacturer: "",
      deviceType: "",
      area: "",
      status: "all"
    });
    setPage(0);
  };

  const handleSave = async () => {
    const filtered = hosts.filter((h) => selectedHosts.includes(h.hostname));
    const payload = {
      hosts: filtered.map((host) => ({
        hostname: host.hostname,
        ipAddress: host.ip,
        model: host.classification?.model || host.model,
        manufacturer: host.manufacturer?.id,
        deviceType: host.deviceType?.id,
        area: host.area?.id,
        vaultCredential: host.vaultCredential || null,
      })),
    };

    try {
      const result = await saveClassifiedHosts(payload);
      if (result?.created > 0) {
        setSnackbar({ 
          open: true, 
          message: `✅ ${result.created} host(s) guardado(s)`, 
          severity: "success" 
        });
        setHosts([]);
        setSelectedHosts([]);
      } else {
        setSnackbar({ 
          open: true, 
          message: `❌ Error: ${result?.errors?.[0]?.error || "Falló el guardado"}`, 
          severity: "error" 
        });
      }
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: "❌ Error al guardar hosts", 
        severity: "error" 
      });
    }
  };

  // Calcular estados de selección
  const allCurrentPageSelected = paginatedHosts.length > 0 && 
    paginatedHosts.every(host => selectedHosts.includes(host.hostname));
  
  const someCurrentPageSelected = paginatedHosts.some(host => 
    selectedHosts.includes(host.hostname)) && !allCurrentPageSelected;

  // Contar filtros activos
  const activeFilterCount = [
    searchTerm,
    filters.manufacturer,
    filters.deviceType,
    filters.area,
    filters.status !== "all"
  ].filter(Boolean).length;

  return (
    <Box sx={{
      p: { xs: 2, sm: 3, md: 4 },
      width: "100%",
      maxWidth: { xs: '100%', md: 1200 },
      mx: "auto"
    }}>
      <Typography variant="h4" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1 }}>
        🧩 Ingreso Masivo de Hosts
      </Typography>

      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Conjunto de Reglas</InputLabel>
        <Select value={selectedRule} onChange={(e) => setSelectedRule(e.target.value)}>
          {rules.map((rule) => (
            <MenuItem key={rule.id} value={rule.id}>{rule.name}</MenuItem>
          ))}
        </Select>
      </FormControl>

      <ImportControls
        onZabbixImport={handleZabbixImport}
        onFileChange={(e) => setFile(e.target.files[0])}
        onCSVImport={handleCSVImport}
        loading={loading}
        selectedRule={selectedRule}
        file={file}
      />

      {hosts.length > 0 && (
        <>
          {/* Barra de búsqueda y filtros */}
          <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
              <TextField
                label="Buscar por hostname, IP o modelo"
                variant="outlined"
                size="small"
                sx={{ flex: 1, minWidth: 300 }}
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setPage(0);
                }}
              />
              
              <Button
                variant={showFilters ? "contained" : "outlined"}
                startIcon={<FilterListIcon />}
                onClick={() => setShowFilters(!showFilters)}
                sx={{ position: 'relative' }}
              >
                Filtros
                {activeFilterCount > 0 && (
                  <Chip
                    label={activeFilterCount}
                    size="small"
                    color="primary"
                    sx={{ 
                      position: 'absolute', 
                      top: -8, 
                      right: -8,
                      height: 20,
                      fontSize: '0.75rem'
                    }}
                  />
                )}
              </Button>

              {filteredHosts.length > 0 && (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleSelectAllFiltered}
                >
                  Seleccionar todos ({filteredHosts.length})
                </Button>
              )}
            </Box>

            {/* Filtros avanzados */}
            {showFilters && (
              <Box sx={{ 
                mt: 2, 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(4, 1fr)' }, 
                gap: 2 
              }}>
                <FormControl size="small">
                  <InputLabel>Fabricante</InputLabel>
                  <Select
                    value={filters.manufacturer}
                    onChange={(e) => {
                      setFilters({ ...filters, manufacturer: e.target.value });
                      setPage(0);
                    }}
                  >
                    <MenuItem value="">Todos</MenuItem>
                    {filterOptions.manufacturers.map(mfr => (
                      <MenuItem key={mfr} value={mfr}>{mfr}</MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl size="small">
                  <InputLabel>Tipo de Dispositivo</InputLabel>
                  <Select
                    value={filters.deviceType}
                    onChange={(e) => {
                      setFilters({ ...filters, deviceType: e.target.value });
                      setPage(0);
                    }}
                  >
                    <MenuItem value="">Todos</MenuItem>
                    {filterOptions.deviceTypes.map(type => (
                      <MenuItem key={type} value={type}>{type}</MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl size="small">
                  <InputLabel>Área</InputLabel>
                  <Select
                    value={filters.area}
                    onChange={(e) => {
                      setFilters({ ...filters, area: e.target.value });
                      setPage(0);
                    }}
                  >
                    <MenuItem value="">Todas</MenuItem>
                    {filterOptions.areas.map(area => (
                      <MenuItem key={area} value={area}>{area}</MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl size="small">
                  <InputLabel>Estado</InputLabel>
                  <Select
                    value={filters.status}
                    onChange={(e) => {
                      setFilters({ ...filters, status: e.target.value });
                      setPage(0);
                    }}
                  >
                    <MenuItem value="all">Todos</MenuItem>
                    <MenuItem value="complete">✅ Completos</MenuItem>
                    <MenuItem value="incomplete">⚠️ Incompletos</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            )}

            {activeFilterCount > 0 && (
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  {filteredHosts.length} de {hosts.length} hosts encontrados
                </Typography>
                <IconButton size="small" onClick={handleClearFilters} title="Limpiar filtros">
                  <ClearIcon fontSize="small" />
                </IconButton>
              </Box>
            )}
          </Paper>
        </>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : hosts.length > 0 ? (
        <HostsTable
          paginatedHosts={paginatedHosts}
          filteredHostsLength={filteredHosts.length}
          page={page}
          rowsPerPage={rowsPerPage}
          onPageChange={(e, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          selectedHosts={selectedHosts}
          onHostToggle={handleCheckboxToggle}
          onSelectAll={handleSelectAllCurrentPage}
          onSelectAllFiltered={handleSelectAllFiltered}
          allCurrentPageSelected={allCurrentPageSelected}
          someCurrentPageSelected={someCurrentPageSelected}
          totalFiltered={filteredHosts.length}
          totalSelected={selectedHosts.length}
        />
      ) : null}

      {selectedHosts.length > 0 && (
        <Box sx={{ mt: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button 
            variant="contained" 
            color="success" 
            size="large"
            onClick={handleSave}
          >
            💾 Guardar {selectedHosts.length} Host(s) Seleccionado(s)
          </Button>
          <Button 
            variant="outlined" 
            color="error"
            onClick={() => setSelectedHosts([])}
          >
            Limpiar Selección
          </Button>
        </Box>
      )}

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default BulkHostImport;