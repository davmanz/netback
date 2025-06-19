// 📂 src/components/BackupModal.js
import { Dialog, DialogTitle, DialogContent, DialogActions, Typography, Button, Box } from "@mui/material";

const BackupModal = ({ open, onClose, backupData }) => {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Último Backup</DialogTitle>
      <DialogContent sx={{ minWidth: "80vw", maxHeight: "80vh", overflow: "auto" }}>
        {backupData ? (
          <Box>
            <Typography variant="h6">Running Config</Typography>
            <Box sx={{
              background: "#222",
              color: "#fff",
              padding: "10px",
              borderRadius: "5px",
              display: "inline-block",
              maxWidth: "100%",
              overflowX: "auto"
            }}>
              <pre style={{ margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                {backupData.runningConfig ? backupData.runningConfig.replace(/(.{80})/g, "$1\n") : "No disponible"}
              </pre>
            </Box>

            <Typography variant="h6">VLAN Config</Typography>
            <Box sx={{
              background: "#222",
              color: "#fff",
              padding: "10px",
              borderRadius: "5px",
              display: "inline-block",
              maxWidth: "100%",
              overflowX: "auto"
            }}>
              <pre style={{ margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                {backupData.vlanBrief ? backupData.vlanBrief.replace(/(.{80})/g, "$1\n") : "No disponible"}
              </pre>
            </Box>
          </Box>
        ) : (
          <Typography>No hay datos disponibles</Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cerrar</Button>
      </DialogActions>
    </Dialog>
  );
};

export default BackupModal;
