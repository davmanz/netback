import { useState, useEffect, useMemo } from "react";
import {
  getVaultCredentials, createVaultCredential,
  updateVaultCredential, deleteVaultCredential,
} from "../api";
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Button, IconButton, Snackbar, Alert, Typography, Box, TablePagination,
} from "@mui/material";
import { Add, Edit, Delete, FileDownload } from "@mui/icons-material";
import VaultCredentialForm from "./modals/VaultCredentials/VaultCredentialForm";
import {ConfirmDialog} from "../components/common/ConfirmDialog";


const VaultCredentials = () => {
  const [credentials, setCredentials] = useState([]);
  const [formData, setFormData] = useState({ nick: "", username: "", password: "" });
  const [editingId, setEditingId] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [credentialToDelete, setCredentialToDelete] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "info" });

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    fetchCredentials();
  }, []);

  const fetchCredentials = async () => {
    try {
      const data = await getVaultCredentials();
      if (Array.isArray(data)) setCredentials(data);
    } catch {
      setSnackbar({ open: true, message: "Error al obtener credenciales.", severity: "error" });
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.nick || !formData.username || !formData.password) {
      setSnackbar({ open: true, message: "Todos los campos son obligatorios.", severity: "error" });
      return;
    }

    let result;
    if (editingId) {
      result = await updateVaultCredential(editingId, formData);
    } else {
      result = await createVaultCredential(formData);
    }

    if (result) {
      setOpenDialog(false);
      setSnackbar({ open: true, message: editingId ? "Credencial actualizada." : "Credencial creada.", severity: "success" });
      fetchCredentials();
    } else {
      setSnackbar({ open: true, message: "Error al guardar la credencial.", severity: "error" });
    }

    setEditingId(null);
    setFormData({ nick: "", username: "", password: "" });
  };

  const handleDelete = (credential) => {
    setCredentialToDelete(credential);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    const result = await deleteVaultCredential(credentialToDelete.id);
    if (result) {
      setSnackbar({ open: true, message: "Credencial eliminada.", severity: "success" });
      fetchCredentials();
    } else {
      setSnackbar({ open: true, message: "Error al eliminar la credencial.", severity: "error" });
    }
    setDeleteDialogOpen(false);
    setCredentialToDelete(null);
  };

  const handleEdit = (credential) => {
    setFormData({ nick: credential.nick, username: credential.username, password: "" });
    setEditingId(credential.id);
    setOpenDialog(true);
  };

  const exportToCSV = () => {
    const headers = ["Nick,Usuario"];
    const csvData = credentials.map(c => `${c.nick},${c.username}`);
    const csv = [headers, ...csvData].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "credenciales_vault.csv";
    link.click();
  };

  const paginatedCredentials = useMemo(() => {
    const start = page * rowsPerPage;
    const end = start + rowsPerPage;
    return credentials.slice(start, end);
  }, [credentials, page, rowsPerPage]);

  return (
    <Box sx={{ padding: 4 }}>
      <Typography variant="h4" gutterBottom>
        Gestión de Credenciales Vault
      </Typography>

      <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<Add />}
          onClick={() => setOpenDialog(true)}
        >
          Agregar Nueva Credencial
        </Button>

        <Button
          variant="outlined"
          startIcon={<FileDownload />}
          onClick={exportToCSV}
        >
          Exportar CSV
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Nick</TableCell>
              <TableCell>Usuario</TableCell>
              <TableCell>Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedCredentials.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3} align="center">
                  No hay credenciales disponibles
                </TableCell>
              </TableRow>
            ) : (
              paginatedCredentials.map((credential) => (
                <TableRow key={credential.id}>
                  <TableCell>{credential.nick}</TableCell>
                  <TableCell>{credential.username}</TableCell>
                  <TableCell>
                    <IconButton color="primary" onClick={() => handleEdit(credential)}>
                      <Edit />
                    </IconButton>
                    <IconButton color="error" onClick={() => handleDelete(credential)}>
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>

        <TablePagination
          component="div"
          count={credentials.length}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          rowsPerPageOptions={[5, 10, 25]}
        />
      </TableContainer>

      {/* Dialog para crear/editar credenciales */}
      <VaultCredentialForm
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        formData={formData}
        onChange={handleChange}
        onSubmit={handleSubmit}
        isEditing={!!editingId}
      />

      {/* Dialog Confirmar eliminación */}
      <ConfirmDialog
        open={deleteDialogOpen}
        title="¿Eliminar credencial?"
        content={`Esta acción no se puede deshacer. ¿Deseas eliminar "${credentialToDelete?.nick}"?`}
        onClose={() => setDeleteDialogOpen(false)}
        onConfirm={confirmDelete}
      />

      <Snackbar open={snackbar.open} autoHideDuration={3000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default VaultCredentials;
