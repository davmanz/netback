import { useEffect, useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Snackbar,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from "@mui/material";
import { createUser, updateUser } from "../../../api";

const UserFormModal = ({ open, onClose, editingUser, onSuccess }) => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    role: "viewer",
  });

  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "info" });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (editingUser) {
      setFormData({
        username: editingUser.username || "",
        email: editingUser.email || "",
        password: "",
        role: editingUser.role || "viewer",
      });
    } else {
      setFormData({ username: "", email: "", password: "", role: "viewer" });
    }
  }, [editingUser]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const validateForm = () => {
    if (!formData.username || !formData.email) {
      setSnackbar({ open: true, message: "Nombre y email son obligatorios", severity: "error" });
      return false;
    }
    if (!editingUser && !formData.password) {
      setSnackbar({ open: true, message: "La contraseña es obligatoria para nuevos usuarios", severity: "error" });
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;
    setLoading(true);
    const result = editingUser
      ? await updateUser(editingUser.id, formData)
      : await createUser(formData);

    if (result) {
      setSnackbar({
        open: true,
        message: editingUser ? "Usuario actualizado exitosamente" : "Usuario creado exitosamente",
        severity: "success",
      });
      onSuccess(); // Para recargar la lista
      onClose();   // Cierra el modal
    } else {
      setSnackbar({
        open: true,
        message: "Error al guardar el usuario",
        severity: "error",
      });
    }
    setLoading(false);
  };

  return (
    <>
      <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
        <DialogTitle>{editingUser ? "Editar Usuario" : "Crear Usuario"}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Nombre"
            name="username"
            variant="outlined"
            value={formData.username}
            onChange={handleChange}
            sx={{ mt: 2 }}
          />
          <TextField
            fullWidth
            label="Email"
            name="email"
            type="email"
            variant="outlined"
            value={formData.email}
            onChange={handleChange}
            sx={{ mt: 2 }}
          />
          {!editingUser && (
            <TextField
              fullWidth
              label="Contraseña"
              name="password"
              type="password"
              variant="outlined"
              value={formData.password}
              onChange={handleChange}
              sx={{ mt: 2 }}
            />
          )}
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Rol</InputLabel>
            <Select name="role" value={formData.role} onChange={handleChange}>
              <MenuItem value="viewer">Viewer</MenuItem>
              <MenuItem value="operator">Operator</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancelar</Button>
          <Button variant="contained" onClick={handleSubmit} disabled={loading}>
            {editingUser ? "Actualizar" : "Crear"}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </>
  );
};

export default UserFormModal;
