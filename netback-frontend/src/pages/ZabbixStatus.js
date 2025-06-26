import { useState } from "react";
import { getZabbixStatus } from "../api";
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  Button,
} from "@mui/material";
import NetworkCheckIcon from '@mui/icons-material/NetworkCheck';
import ErrorIcon from '@mui/icons-material/Error';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useZabbixStore } from "../store/zabbixStore";

const ZabbixStatus = () => {
  const { setZabbixStatus } = useZabbixStore();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  const startDiagnostic = async () => {
    setLoading(true);
    setError(null);
    setStatus(null);
    
    try {
      const result = await getZabbixStatus();
      setStatus(result);
       setZabbixStatus(result);
    } catch (err) {
      setError("Error en la conexión con el servidor");
    } finally {
      setLoading(false);
    }
  };

  const getApiStatusColor = (status) => {
    switch(status) {
      case 'ok': return 'success';
      case 'error': return 'error';
      case 'skipped': return 'warning';
      default: return 'default';
    }
  };

  const getNetworkStatus = (status) => {
    if (!status) return null;
    
    // Red está bien y Zabbix respondió correctamente
    if (status.activate) {
      return { label: "Red y Zabbix OK", color: "success", icon: <CheckCircleIcon /> };
    }
    
    // Si hay respuestas del ping pero Zabbix no responde
    if (status.ping.pass > 0) {
      return { label: "Red OK, Zabbix Error", color: "warning", icon: <ErrorIcon /> };
    }
    
    // No hay conectividad de red
    return { label: "Sin Conectividad", color: "error", icon: <ErrorIcon /> };
  };

  return (
    <Box sx={{ p: 4, textAlign: 'center' }}>
      <Typography variant="h4" gutterBottom>
        🧪 Diagnóstico de Conexión Zabbix
      </Typography>

      <Button
        variant="contained"
        startIcon={<NetworkCheckIcon />}
        onClick={startDiagnostic}
        disabled={loading}
        sx={{ mb: 4 }}
      >
        Iniciar Diagnóstico
      </Button>

      {loading && (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 4 }}>
          <CircularProgress size={60} />
          <Typography sx={{ mt: 2 }}>
            Ejecutando diagnóstico... Por favor espere
          </Typography>
        </Box>
      )}

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {status && (
        <>
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6">Estado de la Red</Typography>
            {getNetworkStatus(status) && (
              <Chip
                label={getNetworkStatus(status).label}
                color={getNetworkStatus(status).color}
                icon={getNetworkStatus(status).icon}
                sx={{ mt: 1 }}
              />
            )}

            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1">
                API Zabbix: {' '}
                <Chip 
                  size="small"
                  label={status.zabbix_api_status.toUpperCase()}
                  color={getApiStatusColor(status.zabbix_api_status)}
                />
              </Typography>
              <Typography variant="subtitle1">
                {status.connect_attempted ? 
                  "✓ Se intentó conexión con Zabbix" : 
                  "✗ No se intentó conexión con Zabbix"}
              </Typography>
            </Box>
          </Paper>

          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6">Diagnóstico de Red</Typography>
            <Box sx={{ mt: 2 }}>
              <Typography>
                Ping: {status.ping.pass} respuesta(s) exitosa(s)
                {status.ping.pass === 0 && " (posible bloqueo ICMP)"}
              </Typography>
              <Typography>
                Paquetes perdidos: {status.ping.drop}
              </Typography>
            </Box>
          </Paper>
        </>
      )}
    </Box>
  );
};

export default ZabbixStatus;
