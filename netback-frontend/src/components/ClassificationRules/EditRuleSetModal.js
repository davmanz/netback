import { useEffect, useState } from "react";
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, Alert, CircularProgress, Box, Snackbar
} from "@mui/material";
import { getClassificationRules, getVaultCredentials, saveClassificationRuleSet } from "../../api";
import EditRuleSetForm from "./EditRuleSetForm";

export const EditRuleSetModal = ({ open, ruleSetId, onClose, onUpdated }) => {
  const [ruleSet, setRuleSet] = useState(null);
  const [vaultCredentials, setVaultCredentials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const all = await getClassificationRules();
        const selected = all.find((r) => r.id === ruleSetId);
        setRuleSet(selected || null);
        const creds = await getVaultCredentials();
        setVaultCredentials(creds);
      } catch (err) {
        setError("No se pudieron cargar los datos. Inténtalo de nuevo más tarde.");
      } finally {
        setLoading(false);
      }
    };

    if (open && ruleSetId) fetch();
  }, [open, ruleSetId]);

  const handleUpdate = async (updatedData) => {
    setSaving(true);
    setError(null);
    
    try {
      const result = await saveClassificationRuleSet(ruleSetId, updatedData);
      if (result?.id) {
        setSuccessMessage("Reglas de clasificación actualizadas con éxito");
        setTimeout(() => {
          onUpdated?.();
          onClose();
        }, 1500);
      } else {
        throw new Error("No se pudo guardar el conjunto de reglas");
      }
    } catch (err) {
      setError("Ocurrió un error al guardar los cambios. Inténtalo de nuevo.");
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    if (!saving) {
      onClose();
    }
  };

  const handleSnackbarClose = () => {
    setSuccessMessage("");
    setError(null);
  };

  return (
    <>
      <Dialog 
        open={open} 
        onClose={handleClose} 
        maxWidth="md" 
        fullWidth
        scroll="paper"
      >
        <DialogTitle>
          <Box display="flex" alignItems="center">
            ✏️ Editar Reglas de Clasificación
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {loading ? (
            <Box display="flex" justifyContent="center" p={3}>
              <Alert icon={<CircularProgress size={20} />} severity="info">
                Cargando conjunto de reglas...
              </Alert>
            </Box>
          ) : error ? (
            <Alert severity="error">{error}</Alert>
          ) : ruleSet ? (
            <EditRuleSetForm
              ruleSet={ruleSet}
              vaultCredentials={vaultCredentials}
              onSubmit={handleUpdate}
            />
          ) : (
            <Alert severity="warning">
              No se encontró el conjunto de reglas solicitado.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={saving}>
            Cancelar
          </Button>
          <Button 
            form="edit-rule-form" 
            type="submit" 
            variant="contained"
            disabled={loading || saving || !ruleSet}
            startIcon={saving ? <CircularProgress size={16} /> : null}
          >
            {saving ? "Guardando..." : "Guardar Cambios"}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={!!successMessage || !!error}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        message={successMessage || error}
      />
    </>
  );
};

export default EditRuleSetModal;