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
} from "@mui/material";

const HostsTable = ({
  paginatedHosts,
  filteredHostsLength,
  page,
  rowsPerPage,
  onPageChange,
  onRowsPerPageChange,
  selectedHosts,
  onHostToggle
}) => {
  return (
    <Paper elevation={3} sx={{ padding: 2, borderRadius: 2, mb: 2 }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>✔</TableCell>
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
          {paginatedHosts.map((host) => (
            <TableRow
              key={host.hostname}
              sx={{
                backgroundColor: host.missing.length > 0 ? "#e3f2fd" : "inherit",
              }}
            >
              <TableCell>
                <Checkbox
                  checked={selectedHosts.includes(host.hostname)}
                  onChange={() => onHostToggle(host.hostname)}
                />
              </TableCell>
              <TableCell><strong>{host.hostname}</strong></TableCell>
              <TableCell>{host.ip}</TableCell>
              <TableCell>{host.classification.model}</TableCell>
              <TableCell>{host.manufacturer.name}</TableCell>
              <TableCell>{host.deviceType.name}</TableCell>
              <TableCell>{host.area?.name || "Sin asignar"}</TableCell>
              <TableCell>
                {host.missing.length > 0 ? (
                  <Chip label={host.missing.join(", ")} color="warning" size="small" />
                ) : (
                  <Chip label="✔ Completo" color="success" size="small" />
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <TablePagination
        component="div"
        count={filteredHostsLength}
        page={page}
        onPageChange={onPageChange}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={onRowsPerPageChange}
        rowsPerPageOptions={[5, 10, 25, 50, 100]}
      />
    </Paper>
  );
};

export default React.memo(HostsTable);
