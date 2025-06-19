import { useEffect, useState } from "react";
import {
  getDevices,
  getBackupHistory,
  compareSpecificBackups,
} from "../api";
import {
  Box,
  Typography,
  Autocomplete,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  CircularProgress,
  Snackbar,
  Alert,
} from "@mui/material";
import CompareArrowsIcon from "@mui/icons-material/CompareArrows";
import BackupList from "./modals/CompareBackups/BackupList";
import ComparisonResult from "./modals/CompareBackups/ComparisonResult";

const CompareBackups = () => {
  const [devices, setDevices] = useState([]);
  const [filteredDevices, setFilteredDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState("");
  const [backups, setBackups] = useState([]);
  const [selectedBackups, setSelectedBackups] = useState([]);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState("all");
  const [searchQuery] = useState("");
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "info" });

  useEffect(() => {
    fetchDevices();
  }, []);

  useEffect(() => {
    const filtered = devices.filter(device => {
      const matchesSearch =
        device.hostname.toLowerCase().includes(searchQuery.toLowerCase()) ||
        device.ipAddress.toLowerCase().includes(searchQuery.toLowerCase());
      if (filterType === "all") return matchesSearch;
      return matchesSearch && device.type === filterType;
    });
    setFilteredDevices(filtered);
  }, [devices, searchQuery, filterType]);

  const fetchDevices = async () => {
    setLoading(true);
    try {
      const data = await getDevices();
      if (data) setDevices(data);
    } catch {
      setSnackbar({ open: true, message: "Error al obtener dispositivos.", severity: "error" });
    }
    setLoading(false);
  };

  const handleDeviceSelect = async (deviceId) => {
    setSelectedDevice(deviceId);
    setSelectedBackups([]);
    setComparisonResult(null);
    setLoading(true);
    try {
      const history = await getBackupHistory(deviceId);
      setBackups(history || []);
    } catch {
      setSnackbar({ open: true, message: "Error al obtener respaldos.", severity: "error" });
    }
    setLoading(false);
  };

  const handleBackupSelection = (backupId) => {
    let updated = [...selectedBackups];
    if (updated.includes(backupId)) {
      updated = updated.filter((id) => id !== backupId);
    } else if (updated.length < 2) {
      updated.push(backupId);
    }
    setSelectedBackups(updated);
  };

  const handleCompare = async () => {
    if (selectedBackups.length !== 2) {
      setSnackbar({ open: true, message: "Selecciona exactamente dos respaldos.", severity: "warning" });
      return;
    }
    setLoading(true);
    try {
      const result = await compareSpecificBackups(selectedBackups[0], selectedBackups[1]);
      setComparisonResult(result?.changes || null);
      setSnackbar({ open: true, message: "Comparación completada.", severity: "success" });
    } catch {
      setSnackbar({ open: true, message: "Error al comparar respaldos.", severity: "error" });
    }
    setLoading(false);
  };

  return (
    <Box sx={{
      p: { xs: 2, sm: 3, md: 4 },
      width: "100%",
      maxWidth: { xs: '100%', md: 900 },
      mx: "auto"
    }}>
      <Typography variant="h4" gutterBottom>
        Comparación de Respaldos
      </Typography>

      <Box sx={{ display: "flex", gap: 2, mb: 2, flexWrap: "wrap" }}>
        <Autocomplete
          options={filteredDevices}
          getOptionLabel={(device) => `${device.hostname} (${device.ipAddress})`}
          value={filteredDevices.find((d) => d.id === selectedDevice) || null}
          onChange={(e, newValue) => handleDeviceSelect(newValue ? newValue.id : "")}
          renderInput={(params) => (
            <TextField {...params} label="Buscar dispositivo" placeholder="Hostname o IP" />
          )}
          fullWidth
          loading={loading}
        />

        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Tipo</InputLabel>
          <Select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
            <MenuItem value="all">Todos</MenuItem>
            <MenuItem value="router">Router</MenuItem>
            <MenuItem value="switch">Switch</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {selectedDevice && (
        <>
          <BackupList
            backups={backups}
            selectedBackups={selectedBackups}
            onToggle={handleBackupSelection}
          />

          <Button
            variant="contained"
            startIcon={<CompareArrowsIcon />}
            onClick={handleCompare}
            disabled={selectedBackups.length !== 2 || loading}
            sx={{ mt: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : "Comparar Respaldos"}
          </Button>
        </>
      )}

      {comparisonResult && (
        <ComparisonResult comparisonResult={comparisonResult} />
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

export default CompareBackups;
