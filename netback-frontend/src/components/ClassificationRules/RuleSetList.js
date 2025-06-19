// 📂 src/components/ClassificationRules/RuleSetList.js
import { useState } from "react";
import {
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TextField,
  TablePagination,
  Button,
  Box
} from "@mui/material";

export const RuleSetList = ({ ruleSets, onEdit, onDelete }) => {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const filtered = ruleSets.filter((r) =>
    r.name.toLowerCase().includes(search.toLowerCase())
  );

  const handleChangePage = (_, newPage) => setPage(newPage);

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box>
      <TextField
        fullWidth
        placeholder="Buscar conjunto de reglas..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        sx={{ mb: 2 }}
      />

      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Nombre</TableCell>
            <TableCell>Acciones</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filtered
            .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
            .map((rule) => (
              <TableRow key={rule.id}>
                <TableCell>{rule.name}</TableCell>
                <TableCell>
                  <Button
                    variant="outlined"
                    size="small"
                    sx={{ mr: 1 }}
                    onClick={() => onEdit(rule.id)}
                  >
                    ✏️ Editar
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    color="error"
                    onClick={() => onDelete(rule.id)}
                  >
                    🗑️ Eliminar
                  </Button>
                </TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>

      <TablePagination
        component="div"
        count={filtered.length}
        page={page}
        onPageChange={handleChangePage}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="Filas por página"
      />
    </Box>
  );
};

export default RuleSetList;
