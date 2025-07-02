import { 
  Chip, Tooltip, Typography, Box,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, 
  Paper, IconButton, useMediaQuery, useTheme, Stack
} from "@mui/material";
import PropTypes from "prop-types";
import BackupIcon from "@mui/icons-material/CloudDownload";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import { useState } from "react";

const StatusChip = ({ label, color, icon, lastAttemptTime }) => (
  <Tooltip 
    title={lastAttemptTime ? `Último intento: ${new Date(lastAttemptTime).toLocaleString()}` : "Sin información"}
    arrow 
    placement="top"
  >
    <Chip 
      label={label} 
      color={color} 
      size="small" 
      icon={icon}
      sx={{ 
        fontWeight: 500,
        fontSize: "0.75rem",
        transition: "all 0.2s ease",
        '&:hover': {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          transform: 'translateY(-1px)'
        }
      }} 
    />
  </Tooltip>
);

// Función mejorada de renderizado de resumen de respaldo
const renderBackupSummary = (tracker) => {
  if (!tracker) return (
    <StatusChip 
      label="Sin datos" 
      color="default" 
      icon={<InfoOutlinedIcon fontSize="small" />}
    />
  );

  const { success_count, no_change_count, error_count, last_attempt_time } = tracker;

  if (error_count > 0) {
    return (
      <StatusChip 
        label={`${error_count} errores`} 
        color="error" 
        icon={<ErrorOutlineIcon fontSize="small" />}
        lastAttemptTime={last_attempt_time}
      />
    );
  }

  if (success_count > 0) {
    return (
      <StatusChip 
        label={`${success_count} con cambios`} 
        color="primary" 
        icon={<WarningAmberIcon fontSize="small" />}
        lastAttemptTime={last_attempt_time}
      />
    );
  }

  if (no_change_count > 0) {
    return (
      <StatusChip 
        label={`${no_change_count} sin cambios`} 
        color="success" 
        icon={<CheckCircleOutlineIcon fontSize="small" />}
        lastAttemptTime={last_attempt_time}
      />
    );
  }

  return (
    <StatusChip 
      label="Sin actividad" 
      color="default" 
      icon={<InfoOutlinedIcon fontSize="small" />}
    />
  );
};

const DeviceTable = ({ devices, openBackupClick, onMenuClick }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [hoveredRow, setHoveredRow] = useState(null);

  // Obtener fecha formateada en un formato más legible
  const formatDate = (dateString) => {
    if (!dateString) return "No disponible";
    
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) {
        return `Hoy, ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      } else if (diffDays === 1) {
        return `Ayer, ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      } else if (diffDays < 7) {
        return `Hace ${diffDays} días`;
      } else {
        return date.toLocaleDateString([], { 
          day: '2-digit', 
          month: '2-digit', 
          year: 'numeric' 
        });
      }
    } catch (e) {
      return dateString;
    }
  };

  return (
    <TableContainer 
      component={Paper} 
      elevation={2}
      sx={{ 
        borderRadius: 2,
        overflow: 'hidden',
        boxShadow: '0 4px 6px rgba(0,0,0,0.07)'
      }}
    >
      <Table stickyHeader size={isMobile ? "small" : "medium"}>
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 'bold', backgroundColor: theme.palette.primary.light, color: theme.palette.primary.contrastText }}>
              Hostname
            </TableCell>
            <TableCell sx={{ fontWeight: 'bold', backgroundColor: theme.palette.primary.light, color: theme.palette.primary.contrastText }}>
              IP
            </TableCell>
            {!isMobile && (
              <>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: theme.palette.primary.light, color: theme.palette.primary.contrastText }}>
                  País
                </TableCell>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: theme.palette.primary.light, color: theme.palette.primary.contrastText }}>
                  Sitio
                </TableCell>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: theme.palette.primary.light, color: theme.palette.primary.contrastText }}>
                  Área
                </TableCell>
              </>
            )}
            <TableCell sx={{ fontWeight: 'bold', backgroundColor: theme.palette.primary.light, color: theme.palette.primary.contrastText }}>
              Intentos
            </TableCell>
            <TableCell sx={{ fontWeight: 'bold', backgroundColor: theme.palette.primary.light, color: theme.palette.primary.contrastText }}>
              Última Modif.
            </TableCell>
            <TableCell sx={{ fontWeight: 'bold', backgroundColor: theme.palette.primary.light, color: theme.palette.primary.contrastText }}>
              Acciones
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {devices.map((device) => (
            <TableRow 
              key={device.id} 
              hover
              onMouseEnter={() => setHoveredRow(device.id)}
              onMouseLeave={() => setHoveredRow(null)}
              sx={{ 
                transition: 'background-color 0.2s ease',
                backgroundColor: hoveredRow === device.id ? 'rgba(0, 0, 0, 0.04)' : 'transparent',
                '&:nth-of-type(odd)': {
                  backgroundColor: hoveredRow === device.id ? 'rgba(0, 0, 0, 0.04)' : theme.palette.action.hover,
                }
              }}
            >
              <TableCell>
                <Typography variant="body2" fontWeight={500}>
                  {device.hostname}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2" fontFamily="monospace">
                  {device.ipAddress}
                </Typography>
              </TableCell>
              {!isMobile && (
                <>
                  <TableCell>{device.country_name}</TableCell>
                  <TableCell>{device.site_name}</TableCell>
                  <TableCell>{device.area_name}</TableCell>
                </>
              )}
              <TableCell>
                {renderBackupSummary(device.backup_tracker)}
              </TableCell>
              <TableCell>
                <Tooltip title={device.last_updated ? new Date(device.last_updated).toLocaleString() : "No disponible"}>
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(device.last_updated)}
                  </Typography>
                </Tooltip>
              </TableCell>
              <TableCell>
                <Stack direction="row" spacing={1}>
                  <Tooltip title="Ver Respaldo">
                    <IconButton 
                      color="primary" 
                      onClick={() => openBackupClick(device.id)}
                      size="small"
                      sx={{ 
                        backgroundColor: theme.palette.primary.light,
                        color: theme.palette.primary.main,
                        '&:hover': {
                          backgroundColor: theme.palette.primary.main,
                          color: theme.palette.primary.contrastText,
                        }
                      }}
                    >
                      <BackupIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Más opciones">
                    <IconButton 
                      color="secondary" 
                      onClick={(e) => onMenuClick(e, device)}
                      size="small"
                    >
                      <MoreVertIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Stack>
              </TableCell>
            </TableRow>
          ))}
          {devices.length === 0 && (
            <TableRow>
              <TableCell colSpan={isMobile ? 5 : 8} align="center" sx={{ py: 4 }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                  <InfoOutlinedIcon fontSize="large" color="disabled" />
                  <Typography variant="body1" color="text.secondary">
                    No se encontraron dispositivos
                  </Typography>
                </Box>
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

DeviceTable.propTypes = {
  devices: PropTypes.array.isRequired,
  onBackupClick: PropTypes.func.isRequired,
  onMenuClick: PropTypes.func.isRequired,
};

export default DeviceTable;