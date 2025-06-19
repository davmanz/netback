import { useEffect, useState, useCallback } from "react";
import {
  getClassificationRules,
  classifyFromZabbix,
  classifyFromCSV,
  saveClassifiedHosts,
} from "../api";
import {
  Box, Button, Typography, Select, MenuItem, InputLabel, FormControl,
  Snackbar, Alert, CircularProgress, TextField,
} from "@mui/material";

import useHostsFiltering from "../hooks/useHostsFiltering";
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

  const { filteredHosts, paginatedHosts } = useHostsFiltering(hosts, searchTerm, page, rowsPerPage);

  useEffect(() => {
    const fetchRules = async () => {
      const data = await getClassificationRules();
      if (data) setRules(data);
    };
    fetchRules();
  }, []);

  const handleZabbixImport = async () => {
    if (!selectedRule) return;
    setLoading(true);
    const result = await classifyFromZabbix(selectedRule);
    if (result) setHosts(result);
    setLoading(false);
    setPage(0);
  };

  const handleCSVImport = async () => {
    if (!selectedRule || !file) return;
    const formData = new FormData();
    formData.append("file", file);
    formData.append("ruleSetId", selectedRule);
    setLoading(true);
    const result = await classifyFromCSV(formData);
    if (result) setHosts(result);
    setLoading(false);
    setPage(0);
  };

  const handleCheckboxToggle = useCallback((hostname) => {
    setSelectedHosts((prev) =>
      prev.includes(hostname)
        ? prev.filter((h) => h !== hostname)
        : [...prev, hostname]
    );
  }, []);

  const handleSave = async () => {
    const filtered = hosts.filter((h) => selectedHosts.includes(h.hostname));
    const payload = {
      hosts: filtered.map((host) => ({
        hostname: host.hostname,
        ipAddress: host.ip,
        model: host.classification.model,
        manufacturer: host.manufacturer.id,
        deviceType: host.deviceType.id,
        area: host.area.id,
        vaultCredential: host.vaultCredential || null,
      })),
    };

    const result = await saveClassifiedHosts(payload);
    if (result?.created > 0) {
      setSnackbar({ open: true, message: `✅ ${result.created} host(s) guardado(s)`, severity: "success" });
      setHosts([]);
      setSelectedHosts([]);
    } else {
      setSnackbar({ open: true, message: `❌ Error: ${result?.errors?.[0]?.error || "Falló el guardado"}`, severity: "error" });
    }
  };

  return (
    <Box sx={{
      p: { xs: 2, sm: 3, md: 4 },
      width: "100%",
      maxWidth: { xs: '100%', md: 900 },
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
        <TextField
          label="Buscar por hostname"
          variant="outlined"
          fullWidth
          sx={{ mb: 2 }}
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setPage(0);
          }}
        />
      )}

      {loading ? (
        <CircularProgress />
      ) : filteredHosts.length > 0 ? (
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
        />
      ) : (
        hosts.length > 0 && (
          <Typography variant="body2" color="text.secondary">
            No se encontraron resultados con el filtro aplicado.
          </Typography>
        )
      )}

      {selectedHosts.length > 0 && (
        <Button variant="contained" color="success" sx={{ mt: 3 }} onClick={handleSave}>
          Guardar Seleccionados ({selectedHosts.length})
        </Button>
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
