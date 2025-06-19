import { useEffect, useState, useCallback } from "react";
import { getBackupHistory, getBackupDetails } from "../api";
import {
  Box, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, CircularProgress,
  Snackbar, Alert, Button,
} from "@mui/material";
import { useParams } from "react-router-dom";
import BackupModal from "./modals/Backups/BackupModal";

const Backups = () => {
  const { deviceId } = useParams();
  const [backups, setBackups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [backupDetails, setBackupDetails] = useState(null);
  const [openModal, setOpenModal] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "info" });

  const fetchBackups = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const history = await getBackupHistory(deviceId);
      if (Array.isArray(history) && history.length > 0) {
        setBackups(history);
      } else {
        setError("No hay respaldos disponibles.");
      }
    } catch (error) {
      setError("Error de conexión con la API.");
    }
    setLoading(false);
  }, [deviceId]);

  const handleViewBackup = async (backupId) => {
    try {
      const details = await getBackupDetails(backupId);
      if (details) {
        setBackupDetails(details);
        setOpenModal(true);
      } else {
        setSnackbar({ open: true, message: "No hay detalles disponibles.", severity: "warning" });
      }
    } catch (error) {
      setSnackbar({ open: true, message: "Error al obtener el respaldo.", severity: "error" });
    }
  };

  useEffect(() => {
    fetchBackups();
  }, [deviceId, fetchBackups]);

  return (
    <Box sx={{
      p: { xs: 2, sm: 3, md: 4 },
      width: "100%",
      maxWidth: { xs: '100%', md: 900 },
      mx: "auto"
    }}>
      <Typography variant="h4" gutterBottom>
        Historial de Respaldos
      </Typography>

      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "200px" }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Fecha</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {backups.length > 0 ? (
                backups.map((backup) => (
                  <TableRow key={backup.id}>
                    <TableCell>{new Date(backup.backupTime).toLocaleString()}</TableCell>
                    <TableCell>
                      <Button variant="outlined" onClick={() => handleViewBackup(backup.id)}>
                        Ver Detalles
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={2} align="center">
                    No hay respaldos disponibles.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* 🔹 Ahora usamos el BackupModal en lugar de tener un modal repetido */}
      <BackupModal open={openModal} onClose={() => setOpenModal(false)} backupData={backupDetails} />

      {/* Snackbar para errores */}
      <Snackbar open={snackbar.open} autoHideDuration={3000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default Backups;
