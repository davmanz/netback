import { useState, useEffect } from "react";
import { pingDevice, createBackup } from "../../../api";
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button, CircularProgress, Typography,
} from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";

const BackupProcessModal = ({ open, onClose, device }) => {

  useEffect(() => {
    if (open) {
      setStep("ping");
      setErrorMessage("");
    }
  }, [open]);

  const [step, setStep] = useState("ping"); // "ping" | "confirm" | "loading" | "done" | "error"
  const [errorMessage, setErrorMessage] = useState("");

  const handlePing = async () => {
    setStep("loading");
    const response = await pingDevice(device.ipAddress);

    if (response) {
      if (response.success) {
        // Ping exitoso
        setStep("confirm");
      } else {
        // Ping falló con mensaje específico
        setStep("error");
        setErrorMessage(
          response.message || "❌ No se pudo alcanzar el dispositivo"
        );
      }
    } else {
      // Error general de comunicación
      setStep("error");
      setErrorMessage("⚠ Error al comunicarse con el servidor");
    }
  };
  
  const handleBackup = async () => {
    setStep("loading");
    const backupSuccess = await createBackup(device.id);

    if (backupSuccess.success) {
      setStep("done");
      setTimeout(onClose, 2000);
    } else if (backupSuccess.error) { 
      setStep("error");
      setErrorMessage(
        backupSuccess.error && backupSuccess.error.includes("Authentication to device failed")
        ? "❌ Error de autenticación: credenciales erradas."
        : backupSuccess.error || "❌ Error al realizar el backup. Posible bloqueo de puerto 22");
    } else {
      setStep("error");
      setErrorMessage("Error al realizar el backup.");
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Forzar Actualización</DialogTitle>
      <DialogContent>
        {step === "ping" && (
          <Button variant="contained" color="primary" onClick={handlePing}>
            Realizar Ping
          </Button>
        )}

        {step === "loading" && <CircularProgress />}

        {step === "confirm" && (
          <div>
            <Typography>✅ Ping exitoso. ¿Desea iniciar el backup?</Typography>
            <Button variant="contained" color="secondary" onClick={handleBackup}>
              Iniciar Backup
            </Button>
          </div>
        )}

        {step === "done" && (
          <div style={{ textAlign: "center" }}>
            <CheckCircleIcon color="success" fontSize="large" />
            <Typography>Backup completado con éxito.</Typography>
          </div>
        )}

        {step === "error" && (
          <div style={{ textAlign: "center", color: "red" }}>
            <ErrorIcon fontSize="large" />
            <Typography>{errorMessage}</Typography>
          </div>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Cerrar
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BackupProcessModal;
