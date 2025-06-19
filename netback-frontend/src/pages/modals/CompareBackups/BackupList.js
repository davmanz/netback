import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Checkbox,
  Alert,
  Typography,
} from "@mui/material";

const BackupList = ({ backups, selectedBackups, onToggle }) => {
  if (!backups || backups.length === 0) {
    return <Alert severity="info">No hay respaldos disponibles.</Alert>;
  }

  return (
    <>
      <Typography variant="h6" sx={{ mt: 3 }}>
        Respaldos Disponibles
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Fecha</TableCell>
              <TableCell>Seleccionar</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {backups.map((backup) => (
              <TableRow key={backup.id}>
                <TableCell>{new Date(backup.backupTime).toLocaleString()}</TableCell>
                <TableCell>
                  <Checkbox
                    checked={selectedBackups.includes(backup.id)}
                    onChange={() => onToggle(backup.id)}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
};

export default BackupList;
