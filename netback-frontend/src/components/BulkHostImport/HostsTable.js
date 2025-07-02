import React from "react";
import {
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Checkbox,
  Chip,
  Paper,
  TablePagination,
  Typography,
  Box,
  Button
} from "@mui/material";
import CheckBoxIcon from '@mui/icons-material/CheckBox';

const HostsTable = ({
  paginatedHosts = [], // Valor por defecto para evitar undefined
  filteredHostsLength = 0,
  page = 0,
  rowsPerPage = 10,
  onPageChange,
  onRowsPerPageChange,
  selectedHosts = [],
  onHostToggle,
  onSelectAll, // Nueva prop para seleccionar todos
  onSelectAllFiltered, // Nueva prop para seleccionar todos los filtrados
  allCurrentPageSelected = false,
  someCurrentPageSelected = false,
  totalFiltered = 0,
  totalSelected = 0
}) => {
  // Validación de datos
  if (!Array.isArray(paginatedHosts)) {
    console.error("paginatedHosts debe ser un array");
    return <Typography color="error">Error: Datos inválidos</Typography>;
  }

  return (
    <Paper elevation={3} sx={{ padding: 2, borderRadius: 2, mb: 2 }}>
      {/* Barra de acciones superior */}
      {totalFiltered > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            {totalSelected} de {totalFiltered} hosts seleccionados
          </Typography>
          {onSelectAllFiltered && (
            <Button
              size="small"
              onClick={onSelectAllFiltered}
              startIcon={<CheckBoxIcon />}
            >
              Seleccionar todos los {totalFiltered} hosts filtrados
            </Button>
          )}
        </Box>
      )}

      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              {onSelectAll && (
                <Checkbox
                  indeterminate={someCurrentPageSelected}
                  checked={allCurrentPageSelected}
                  onChange={onSelectAll}
                  inputProps={{
                    'aria-label': 'seleccionar todos en esta página',
                  }}
                />
              )}
            </TableCell>
            <TableCell>Hostname</TableCell>
            <TableCell>IP</TableCell>
            <TableCell>Modelo</TableCell>
            <TableCell>Fabricante</TableCell>
            <TableCell>Tipo</TableCell>
            <TableCell>Área</TableCell>
            <TableCell>Faltantes</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {paginatedHosts.length > 0 ? (
            paginatedHosts.map((host) => {
              // Validación de datos del host
              if (!host || !host.hostname) {
                console.warn("Host inválido encontrado:", host);
                return null;
              }

              const isSelected = selectedHosts.includes(host.hostname);
              const hasMissing = host.missing && host.missing.length > 0;

              return (
                <TableRow
                  key={host.hostname}
                  sx={{
                    backgroundColor: hasMissing 
                      ? theme => theme.palette.mode === 'dark' ? 'rgba(144, 202, 249, 0.08)' : '#e3f2fd'
                      : 'inherit',
                    '&:hover': {
                      backgroundColor: theme => hasMissing 
                        ? theme.palette.mode === 'dark' ? 'rgba(144, 202, 249, 0.16)' : '#bbdefb'
                        : theme.palette.action.hover
                    }
                  }}
                  selected={isSelected}
                >
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={isSelected}
                      onChange={() => onHostToggle(host.hostname)}
                      inputProps={{
                        'aria-labelledby': `host-${host.hostname}`,
                      }}
                    />
                  </TableCell>
                  <TableCell id={`host-${host.hostname}`}>
                    <strong>{host.hostname}</strong>
                  </TableCell>
                  <TableCell>{host.ip || '-'}</TableCell>
                  <TableCell>{host.classification?.model || host.model || '-'}</TableCell>
                  <TableCell>{host.manufacturer?.name || '-'}</TableCell>
                  <TableCell>{host.deviceType?.name || '-'}</TableCell>
                  <TableCell>{host.area?.name || "Sin asignar"}</TableCell>
                  <TableCell>
                    {hasMissing ? (
                      <Chip 
                        label={host.missing.join(", ")} 
                        color="warning" 
                        size="small" 
                        sx={{
                          backgroundColor: theme => 
                            theme.palette.mode === 'dark' 
                              ? 'rgba(255, 167, 38, 0.2)' 
                              : theme.palette.warning.light,
                          color: theme => 
                            theme.palette.mode === 'dark'
                              ? theme.palette.warning.light
                              : theme.palette.warning.dark
                        }}
                      />
                    ) : (
                      <Chip 
                        label="✔ Completo" 
                        color="success" 
                        size="small" 
                        sx={{
                          backgroundColor: theme => 
                            theme.palette.mode === 'dark' 
                              ? 'rgba(102, 187, 106, 0.2)' 
                              : theme.palette.success.light,
                          color: theme => 
                            theme.palette.mode === 'dark'
                              ? theme.palette.success.light
                              : theme.palette.success.dark
                        }}
                      />
                    )}
                  </TableCell>
                </TableRow>
              );
            })
          ) : (
            <TableRow>
              <TableCell colSpan={8} align="center">
                <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                  No hay hosts para mostrar
                </Typography>
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      {filteredHostsLength > 0 && (
        <TablePagination
          component="div"
          count={filteredHostsLength}
          page={page}
          onPageChange={onPageChange || (() => {})}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={onRowsPerPageChange || (() => {})}
          rowsPerPageOptions={[5, 10, 25, 50, 100]}
          labelRowsPerPage="Hosts por página:"
          labelDisplayedRows={({ from, to, count }) => 
            `${from}-${to} de ${count !== -1 ? count : `más de ${to}`}`
          }
        />
      )}
    </Paper>
  );
};

export default React.memo(HostsTable);