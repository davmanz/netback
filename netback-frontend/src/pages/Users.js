import { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  TextField,
  Snackbar,
  Alert,
  CircularProgress,
  TablePagination,
  InputAdornment,
} from "@mui/material";
import { Add, Edit, Delete, Search } from "@mui/icons-material";
import { getUsers, deleteUser } from "../api";
import UserFormModal from "./modals/Users/UserFormModal";
import ConfirmDialog from "./../components/common/ConfirmDialog";


const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "info" });

  const [openDialog, setOpenDialog] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);


  const [tableState, setTableState] = useState({
    page: 0,
    rowsPerPage: 10,
    search: "",
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await getUsers();
      setUsers(data || []);
    } catch {
      setSnackbar({ open: true, message: "Error al obtener los usuarios.", severity: "error" });
    }
    setLoading(false);
  };

  const handleDelete = (id) => {
    setUserToDelete(id);
    setConfirmOpen(true);
  };

  const confirmDelete = async () => {
    setConfirmOpen(false);
    if (!userToDelete) return;

  setLoading(true);
  try {
    await deleteUser(userToDelete);
    setSnackbar({ open: true, message: "Usuario eliminado.", severity: "success" });
    fetchUsers();
  } catch {
    setSnackbar({ open: true, message: "Error al eliminar el usuario.", severity: "error" });
  }
  setLoading(false);
};


  const handleChangePage = (event, newPage) => {
    setTableState((prev) => ({ ...prev, page: newPage }));
  };

  const handleChangeRowsPerPage = (event) => {
    setTableState({
      ...tableState,
      rowsPerPage: parseInt(event.target.value, 10),
      page: 0,
    });
  };

  const filteredUsers = users.filter((user) =>
    user.username.toLowerCase().includes(tableState.search.toLowerCase()) ||
    user.email.toLowerCase().includes(tableState.search.toLowerCase())
  );

  return (
      <Box sx={{
      p: { xs: 2, sm: 3, md: 4 },
      width: "100%",
      maxWidth: { xs: '100%', md: 900 },
      mx: "auto"
    }}>
      <Typography variant="h4" gutterBottom>
        Gestión de Usuarios
      </Typography>

      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
        <TextField
          fullWidth
          placeholder="Buscar usuarios..."
          value={tableState.search}
          onChange={(e) => setTableState((prev) => ({ ...prev, search: e.target.value }))}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />
        <Button
          variant="contained"
          startIcon={<Add />}
          sx={{ ml: 2 }}
          onClick={() => {
            setEditingUser(null);
            setOpenDialog(true);
          }}
        >
          Crear Usuario
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "200px" }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nombre</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Rol</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredUsers
                .slice(
                  tableState.page * tableState.rowsPerPage,
                  tableState.page * tableState.rowsPerPage + tableState.rowsPerPage
                )
                .map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{user.role}</TableCell>
                    <TableCell>
                      <IconButton color="primary" onClick={() => {
                        setEditingUser(user);
                        setOpenDialog(true);
                      }}>
                        <Edit />
                      </IconButton>
                      <IconButton color="error" onClick={() => handleDelete(user.id)}>
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              {filteredUsers.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} align="center">No se encontraron usuarios</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          <TablePagination
            component="div"
            count={filteredUsers.length}
            page={tableState.page}
            onPageChange={handleChangePage}
            rowsPerPage={tableState.rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            labelRowsPerPage="Filas por página"
            labelDisplayedRows={({ from, to, count }) => `${from}-${to} de ${count}`}
          />
        </TableContainer>
      )}

      {/* Modal separado */}
      <UserFormModal
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        editingUser={editingUser}
        onSuccess={fetchUsers}
      />

      <ConfirmDialog
        open={confirmOpen}
        title="¿Eliminar usuario?"
        content="Esta acción no se puede deshacer. ¿Deseas continuar?"
        onClose={() => setConfirmOpen(false)}
        onConfirm={confirmDelete}
      />


      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default Users;
