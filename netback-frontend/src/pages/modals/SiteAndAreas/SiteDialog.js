import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';

const SiteDialog = ({ open, onClose, onSave, newSite, setNewSite, countries }) => {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Agregar Nuevo Site</DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          label="Nombre del Site"
          variant="outlined"
          sx={{ mt: 2 }}
          value={newSite.name}
          onChange={(e) => setNewSite({ ...newSite, name: e.target.value })}
        />
        <FormControl fullWidth sx={{ mt: 2 }}>
          <InputLabel>País</InputLabel>
          <Select
            value={newSite.country}
            onChange={(e) => setNewSite({ ...newSite, country: e.target.value })}
          >
            {countries.map((c) => (
              <MenuItem key={c.id} value={c.id}>
                {c.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
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

export default SiteDialog;
