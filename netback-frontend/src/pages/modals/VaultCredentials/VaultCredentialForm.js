import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
} from "@mui/material";

const VaultCredentialForm = ({
  open,
  onClose,
  formData,
  onChange,
  onSubmit,
  isEditing
}) => {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{isEditing ? "Editar Credencial" : "Nueva Credencial"}</DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          label="Nick"
          name="nick"
          value={formData.nick}
          onChange={onChange}
          required
          sx={{ mb: 2 }}
        />
        <TextField
          fullWidth
          label="Usuario"
          name="username"
          value={formData.username}
          onChange={onChange}
          required
          sx={{ mb: 2 }}
        />
        <TextField
          fullWidth
          label="Contraseña"
          type="password"
          name="password"
          value={formData.password}
          onChange={onChange}
          required
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button onClick={onSubmit} variant="contained" color="primary">
          {isEditing ? "Guardar Cambios" : "Crear"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default VaultCredentialForm;
