import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box, Typography, TextField, Menu, MenuItem, 
  CircularProgress, Snackbar, Alert, TablePagination
} from "@mui/material";
import BackupModal from "./modals/Backups/BackupModal";
import BackupProcessModal from "./modals/Backups/BackupProcessModal";
import DeviceTable from "../components/Dashboard/DeviceTable"; 
import { getBackupDetails } from "../api";
import { useDevices } from "../hooks/useDevices"; 

const Dashboard = () => {
  const { devices, isLoading, error, loadDevices } = useDevices();
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [backupData, setBackupData] = useState(null);
  const [openBackupModal, setOpenBackupModal] = useState(false);
  const [backupProcessOpen, setBackupProcessOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "info" });
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const filteredDevices = useMemo(() => {
    return devices.filter(
      (device) =>
        device.hostname.toLowerCase().includes(search.toLowerCase()) ||
        device.ipAddress.toLowerCase().includes(search.toLowerCase()) ||
        device.country_name.toLowerCase().includes(search.toLowerCase())||
        device.site_name.toLowerCase().includes(search.toLowerCase())||
        device.area_name.toLowerCase().includes(search.toLowerCase())
    );
  }, [devices, search]);

  const paginatedDevices = useMemo(() => {
    return filteredDevices.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  }, [filteredDevices, page, rowsPerPage]);

  const handleOpenBackup = async (deviceId) => {
    const device = devices.find((d) => d.id === deviceId);
    if (device && device.backup_id) {
      const backupDetails = await getBackupDetails(device.backup_id);
      if (backupDetails) {
        setBackupData(backupDetails);
        setOpenBackupModal(true);
      } else {
        setSnackbar({ open: true, message: "Error al obtener backup", severity: "error" });
      }
    } else {
      setSnackbar({ open: true, message: "Dispositivo sin backup disponible", severity: "warning" });
    }
  };

  const handleOpenMenu = (event, device) => {
    setAnchorEl(event.currentTarget);
    setSelectedDevice(device);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
  };

  const handleOpenBackupProcess = () => {
    if (selectedDevice) {
      setBackupProcessOpen(true);
      handleCloseMenu();
    }
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h4" gutterBottom>
        📊 Dashboard de Dispositivos
      </Typography>

      <TextField
        label="🔎 Buscar por IP, Hostname, Pais, Area o Sitio"
        variant="outlined"
        fullWidth
        margin="normal"
        value={search}
        onChange={(e) => {
          setSearch(e.target.value);
          setPage(0);
        }}
      />

      {isLoading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 5 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">Error al cargar los dispositivos: {error.message}</Alert>
      ) : (
        <>
          <DeviceTable
            devices={paginatedDevices}
            openBackupClick={handleOpenBackup}
            onMenuClick={handleOpenMenu}
          />

          <TablePagination
            component="div"
            count={filteredDevices.length}
            page={page}
            onPageChange={(e, newPage) => setPage(newPage)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
            rowsPerPageOptions={[5, 10, 25, 50, 100]}
          />
        </>
      )}

      {/* Menú contextual */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleCloseMenu}>
        {selectedDevice && (
          <>
            <MenuItem onClick={() => navigate(`/backup/${selectedDevice.id}/history`)}>
              Ver Historial de Backups
            </MenuItem>
            <MenuItem onClick={handleOpenBackupProcess}>
              Forzar Actualización del Equipo
            </MenuItem>
          </>
        )}
      </Menu>

      {/* Modales */}
      {selectedDevice && (
        <BackupProcessModal
          open={backupProcessOpen}
          onClose={() => {
            setBackupProcessOpen(false);
            loadDevices();
          }}
          device={selectedDevice}
        />
      )}

      {openBackupModal && (
        <BackupModal
          open={openBackupModal}
          onClose={() => setOpenBackupModal(false)}
          backupData={backupData}
        />
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

export default Dashboard;
