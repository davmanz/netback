import { useEffect, useState } from "react";
import { getBackupSchedule, updateBackupSchedule } from "../api";
import { Box, Typography, Button, Alert, Snackbar, TextField } from "@mui/material";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import LoadingOverlay from "../components/common/LoadingOverlay";
import ConfirmDialog from "../components/common/ConfirmDialog";

// 📌 Mensajes de error predefinidos
const ERROR_MESSAGES = {
  FETCH_ERROR: "Error al obtener la hora programada.",
  UPDATE_ERROR: "Error al actualizar la hora del respaldo.",
  INVALID_FORMAT: "Formato de hora inválido. Use HH:MM",
  NO_TIME: "No se pudo obtener la hora programada.",
};

// 📌 Validación de formato de hora (HH:MM 24h)
const validateTimeFormat = (time) => {
  const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
  return timeRegex.test(time);
};

const BackupSchedule = () => {
  const [state, setState] = useState({
    scheduledTime: "",
    loading: true,
    success: false,
    error: "",
  });

  const [confirmOpen, setConfirmOpen] = useState(false); // ✅ nuevo estado

  useEffect(() => {
    fetchScheduledTime();
  }, []);

  const fetchScheduledTime = async () => {
    setState((prev) => ({ ...prev, loading: true, error: "" }));
    try {
      const response = await getBackupSchedule();
      if (response?.scheduled_time) {
        setState((prev) => ({
          ...prev,
          scheduledTime: response.scheduled_time,
        }));
      } else {
        throw new Error(ERROR_MESSAGES.NO_TIME);
      }
    } catch (err) {
      setState((prev) => ({
        ...prev,
        error: err.message || ERROR_MESSAGES.FETCH_ERROR,
      }));
    } finally {
      setState((prev) => ({ ...prev, loading: false }));
    }
  };

  // ✅ Función que lanza el modal
  const handleOpenConfirm = () => {
    if (!validateTimeFormat(state.scheduledTime)) {
      setState((prev) => ({
        ...prev,
        error: ERROR_MESSAGES.INVALID_FORMAT,
      }));
      return;
    }
    setConfirmOpen(true);
  };

  // ✅ Confirmación del modal
  const handleConfirmUpdate = async () => {
    setConfirmOpen(false);
    setState((prev) => ({ ...prev, loading: true, error: "", success: false }));
    try {
      const response = await updateBackupSchedule(state.scheduledTime);
      if (response?.success) {
        setState((prev) => ({ ...prev, success: true }));
      } else {
        throw new Error(ERROR_MESSAGES.UPDATE_ERROR);
      }
    } catch (err) {
      setState((prev) => ({
        ...prev,
        error: err.message || ERROR_MESSAGES.UPDATE_ERROR,
      }));
    } finally {
      setState((prev) => ({ ...prev, loading: false }));
    }
  };

  return (
    <Box sx={{
      p: { xs: 2, sm: 3, md: 4 },
      width: "100%",
      maxWidth: { xs: '100%', md: 900 },
      mx: "auto"
    }}>
      <Typography variant="h4" gutterBottom>
        Configuración del Respaldo Automático
      </Typography>

      {state.loading && <LoadingOverlay />}
      {state.error && <Alert severity="error" sx={{ mb: 2 }}>{state.error}</Alert>}

      <Box sx={{ display: "flex", alignItems: "center", gap: 2, justifyContent: "center", mt: 2 }}>
        <AccessTimeIcon color="primary" />
        <TextField
          label="Hora del respaldo (HH:MM)"
          type="time"
          value={state.scheduledTime}
          onChange={(e) => setState({ ...state, scheduledTime: e.target.value })}
          slotProps={{ inputLabel: { shrink: true } }}
          sx={{ width: "50%" }}
        />
      </Box>

      <Button variant="contained" color="primary" sx={{ mt: 3 }} onClick={handleOpenConfirm} disabled={state.loading}>
        Guardar Cambios
      </Button>

      <Snackbar
        open={state.success}
        autoHideDuration={3000}
        onClose={() => setState({ ...state, success: false })}
      >
        <Alert severity="success">Respaldo programado a las {state.scheduledTime}</Alert>
      </Snackbar>

      {/* ✅ Modal de confirmación */}
      <ConfirmDialog
        open={confirmOpen}
        title="Confirmar Programación"
        content={`¿Está seguro de programar el respaldo a las ${state.scheduledTime}?`}
        onClose={() => setConfirmOpen(false)}
        onConfirm={handleConfirmUpdate}
      />
    </Box>
  );
};

export default BackupSchedule;
