import { useEffect, useState, useMemo } from "react";
import {
  getDevices,
  deleteDevice,
} from "../api";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Button,
  TextField,
  Box,
  Typography,
  CircularProgress,
  Snackbar,
  Alert,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TablePagination,
} from "@mui/material";
import { Delete, Edit, Add, FileDownload } from "@mui/icons-material";
import AddDeviceModal from "../components/DeviceManagement/AddDeviceModal";
import EditDeviceDialog from "./modals/DeviceManagements/EditDeviceDialog";

const DeviceManagement = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [openEditModal, setOpenEditModal] = useState(false);
  const [openAddModal, setOpenAddModal] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "info" });

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deviceToDelete, setDeviceToDelete] = useState(null);

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    setLoading(true);
    try {
      const data = await getDevices();
      setDevices(Array.isArray(data) ? data : []);
      setError("");
    } catch (err) {
      setError("Error de conexión con la API.");
      setSnackbar({
        open: true,
        message: "Error al cargar los dispositivos",
        severity: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEditDevice = (device) => {
    setSelectedDevice(device);
    setOpenEditModal(true);
  };

  const handleDeleteClick = (device) => {
    setDeviceToDelete(device);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    try {
      await deleteDevice(deviceToDelete.id);
      setSnackbar({ open: true, message: "Dispositivo eliminado.", severity: "success" });
      fetchDevices();
    } catch {
      setSnackbar({ open: true, message: "Error al eliminar el dispositivo.", severity: "error" });
    } finally {
      setDeleteDialogOpen(false);
      setDeviceToDelete(null);
    }
  };

  const handleFilterChange = (e) => {
    setFilter(e.target.value);
    setPage(0);
  };

  const filteredDevices = useMemo(() =>
    devices.filter((device) =>
      device.hostname.toLowerCase().includes(filter.toLowerCase()) ||
      device.ipAddress.toLowerCase().includes(filter.toLowerCase()) ||
      (device.manufacturer_name && device.manufacturer_name.toLowerCase().includes(filter.toLowerCase()))
    ),
    [devices, filter]
  );

  const exportToCSV = () => {
    const headers = ["Hostname,IP,País,Sitio,Area,Fabricante"];
    const csvData = filteredDevices.map(device =>
      `${device.hostname},${device.ipAddress},${device.country_name},${device.site_name},${device.area_name},${device.manufacturer_name || "N/A"}`
    );
    const csv = [headers, ...csvData].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "dispositivos.csv";
    link.click();
  };

  return (
    <Box sx={{ padding: 4 }}>
      <Typography variant="h4" gutterBottom>
        Gestión de Equipos
      </Typography>

      <TextField
        fullWidth
        label="Buscar por hostname, IP o fabricante..."
        value={filter}
        onChange={handleFilterChange}
        sx={{ mb: 2 }}
      />

      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", height: "50vh" }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Hostname</TableCell>
                <TableCell>IP</TableCell>
                <TableCell>País</TableCell>
                <TableCell>Sitio</TableCell>
                <TableCell>Area</TableCell>
                <TableCell>Fabricante</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredDevices.length > 0 ? (
                filteredDevices.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((device) => (
                  <TableRow key={device.id}>
                    <TableCell>{device.hostname}</TableCell>
                    <TableCell>{device.ipAddress}</TableCell>
                    <TableCell>{device.country_name}</TableCell>
                    <TableCell>{device.site_name}</TableCell>
                    <TableCell>{device.area_name}</TableCell>
                    <TableCell>{device.manufacturer_name || "N/A"}</TableCell>
                    <TableCell>
                      <IconButton color="primary" onClick={() => handleEditDevice(device)}>
                        <Edit />
                      </IconButton>
                      <IconButton color="error" onClick={() => handleDeleteClick(device)}>
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No hay dispositivos disponibles.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
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
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        </TableContainer>
      )}

      <Box sx={{ mt: 2 }}>
        <Button
          variant="contained"
          color="success"
          startIcon={<Add />}
          onClick={() => setOpenAddModal(true)}
          sx={{ mr: 2 }}
        >
          Agregar Dispositivo
        </Button>

        <Button
          variant="outlined"
          startIcon={<FileDownload />}
          onClick={exportToCSV}
        >
          Exportar CSV
        </Button>
      </Box>

      {/* Modal Editar */}
      {selectedDevice && (
        <EditDeviceDialog
          open={openEditModal}
          onClose={() => setOpenEditModal(false)}
          deviceId={selectedDevice.id}
          onDeviceUpdated={fetchDevices}
        />
      )}

      <AddDeviceModal
        open={openAddModal}
        onClose={() => setOpenAddModal(false)}
        onDeviceAdded={fetchDevices}
      />

      {/* Dialog Confirmación de Eliminación */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirmar eliminación</DialogTitle>
        <DialogContent>
          ¿Estás seguro que deseas eliminar el dispositivo <strong>{deviceToDelete?.hostname}</strong>?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancelar</Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained">Eliminar</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar open={snackbar.open} autoHideDuration={3000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default DeviceManagement;
