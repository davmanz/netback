import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
} from '@mui/material';

const AreaDialog = ({ open, onClose, onSave, newArea, setNewArea }) => {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Agregar Nueva Área</DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          label="Nombre del Área"
          variant="outlined"
          sx={{ mt: 2 }}
          value={newArea.name}
          onChange={(e) => setNewArea({ ...newArea, name: e.target.value })}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button variant="contained" onClick={onSave}>
          Guardar
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AreaDialog;
