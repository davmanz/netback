import { useEffect, useState } from "react";
import { Box, Typography, Button, Snackbar, Alert } from "@mui/material";
import { getClassificationRules, deleteClassificationRuleSet } from "../api";
import { RuleSetList } from "../components/ClassificationRules/RuleSetList";
import { RuleSetModal } from "../components/ClassificationRules/RuleSetModal";
import { EditRuleSetModal } from "../components/ClassificationRules/EditRuleSetModal";

const ClassificationRules = () => {
  const [ruleSets, setRuleSets] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState(null); // "create" | "edit"
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "info" });

  const loadRules = async () => {
    const rules = await getClassificationRules();
    setRuleSets(rules);
  };

  useEffect(() => {
    loadRules();
  }, []);

  const handleCreate = () => {
    setSelectedId(null);
    setModalMode("create");
    setModalOpen(true);
  };

  const handleEdit = (id) => {
    setSelectedId(id);
    setModalMode("edit");
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    const success = await deleteClassificationRuleSet(id);
    if (success) {
      setSnackbar({ open: true, message: "✅ Eliminado correctamente", severity: "success" });
      loadRules();
    } else {
      setSnackbar({ open: true, message: "❌ Error al eliminar", severity: "error" });
    }
  };

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        🧠 Reglas de Clasificación
      </Typography>

      <RuleSetList ruleSets={ruleSets} onEdit={handleEdit} onDelete={handleDelete} />

      <Button variant="contained" sx={{ mt: 2 }} onClick={handleCreate}>
        ➕ Nuevo conjunto
      </Button>

      {/* Modal para CREACIÓN */}
      {modalMode === "create" && (
        <RuleSetModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          ruleSetId={null}
          onSaved={() => {
            setModalOpen(false);
            loadRules();
          }}
        />
      )}

      {/* Modal para EDICIÓN */}
      {modalMode === "edit" && selectedId && (
        <EditRuleSetModal
          open={modalOpen}
          ruleSetId={selectedId}
          onClose={() => setModalOpen(false)}
          onUpdated={() => {
            setModalOpen(false);
            loadRules();
          }}
        />
      )}

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

export default ClassificationRules;
