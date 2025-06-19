import PropTypes from "prop-types";
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton
} from "@mui/material";
import BackupIcon from "@mui/icons-material/CloudDownload";
import MoreVertIcon from "@mui/icons-material/MoreVert";

const DeviceTable = ({ devices, onBackupClick, onMenuClick }) => (
  <TableContainer component={Paper} >
    <Table stickyHeader>
      <TableHead>
        <TableRow>
          <TableCell>Hostname</TableCell>
          <TableCell>IP</TableCell>
          <TableCell>País</TableCell>
          <TableCell>Sitio</TableCell>
          <TableCell>Área</TableCell>
          <TableCell>Última Actualización</TableCell>
          <TableCell>Acciones</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {devices.map((device) => (
          <TableRow key={device.id} hover>
            <TableCell>{device.hostname}</TableCell>
            <TableCell>{device.ipAddress}</TableCell>
            <TableCell>{device.country_name}</TableCell>
            <TableCell>{device.site_name}</TableCell>
            <TableCell>{device.area_name}</TableCell>
            <TableCell>{device.last_updated}</TableCell>
            <TableCell>
              <IconButton color="primary" onClick={() => onBackupClick(device.id)}>
                <BackupIcon />
              </IconButton>
              <IconButton color="secondary" onClick={(e) => onMenuClick(e, device)}>
                <MoreVertIcon />
              </IconButton>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </TableContainer>
);

DeviceTable.propTypes = {
  devices: PropTypes.array.isRequired,
  onBackupClick: PropTypes.func.isRequired,
  onMenuClick: PropTypes.func.isRequired,
};

export default DeviceTable;
